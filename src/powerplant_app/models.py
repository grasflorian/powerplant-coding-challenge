from typing import Annotated

from pydantic import BaseModel, Field, model_validator, field_validator, PlainSerializer
from enum import StrEnum
from decimal import Decimal, ROUND_UP

ROUNDING = Decimal("0.1")

CO2_TONS_PER_KWH = Decimal(0.3)


class PowerPerPowerplant(BaseModel):
    name: str
    p: Annotated[
        Decimal,
        PlainSerializer(
            float,
            return_type=float,
            when_used="json",
        ),
    ]


class PowerPlantType(StrEnum):
    GASFIRED = "gasfired"
    TURBOJET = "turbojet"
    WINDTURBINE = "windturbine"


POWERPLANT_TYPE_TO_FUEL_NAME = {
    PowerPlantType.GASFIRED: "gas",
    PowerPlantType.TURBOJET: "kerosine",
    PowerPlantType.WINDTURBINE: "wind",
}


class FuelPrices(BaseModel):
    gas: Decimal = Field(alias="gas(euro/MWh)", description="Gas price in euro/MWh")
    kerosine: Decimal = Field(
        alias="kerosine(euro/MWh)", description="Kerosine price in euro/MWh"
    )
    co2: Decimal = Field(alias="co2(euro/ton)", description="CO2 price in euro/ton")
    wind: Decimal = Field(alias="wind(%)", description="Wind efficiency in %")

    @model_validator(mode="after")
    def add_co2_emission(self):
        """Adjusts prices by adding CO2 emission costs."""
        self.gas += self.co2 * CO2_TONS_PER_KWH * 1000
        self.kerosine += self.co2 * CO2_TONS_PER_KWH * 1000
        return self


class PowerplantInfo(BaseModel):
    name: str
    type: PowerPlantType
    efficiency: Decimal
    pmin: Decimal
    pmax: Decimal

    @property
    def fuel_name(self):
        return POWERPLANT_TYPE_TO_FUEL_NAME[self.type]

    def cost_per_mwh(self, fuel_prices: FuelPrices) -> float:
        """Cost of mWh production for this power plant.

        Wind turbines are assumed to produce at no cost.

        Args:
            fuel_prices (FuelPrices): The fuel prices assumed to be in currency per kWh.
        Returns:
            float: Cost per kWh in the currency given in fuel prices.
        """
        if self.type == PowerPlantType.WINDTURBINE:
            return 0
        # if the price is not available, be conservative and assume infinite cost
        return getattr(fuel_prices, self.fuel_name, float("inf")) / self.efficiency

    def adjusted_pmax(self, fuel_prices: FuelPrices) -> Decimal:
        """Adjusted maximum power output.

        In case of wind turbines, the maximum power output is adjusted by the wind efficiency.

        Args:
            fuel_prices (FuelPrices): The fuel prices.
        Returns:
            float: The adjusted maximum power output.
        """
        return (
            self.pmax
            if self.type != PowerPlantType.WINDTURBINE
            else self.pmax * fuel_prices.wind / 100
        ).quantize(ROUNDING, ROUND_UP)


class PowerPlanIn(BaseModel):
    load: Decimal
    fuels: FuelPrices
    powerplants: list[PowerplantInfo]

    @field_validator("load", mode="after")
    @classmethod
    def round_up_to_nearest_01(cls, load: Decimal) -> Decimal:
        return load.quantize(ROUNDING, ROUND_UP)

    def optimize(self) -> list[PowerPerPowerplant]:
        """
        Optimizes the power distribution across power plants to meet the required load
        while minimizing the cost of production. The power plants are prioritized based
        on their cost per mWh, and in case of equal costs, they are further sorted
        alphabetically by name.
        Load is rounded up to the nearest 0.1 kWh, so a load of 1.51MWh will be rounded to 1.6MWh.

        Returns:
            list[PowerPerPowerplant]: A list of `PowerPerPowerplant` objects, representing the optimized production by cost
        """
        # sort by kwh and alphanumerically
        sorted_by_cost = sorted(
            self.powerplants, key=lambda p: (p.cost_per_mwh(self.fuels), p.name)
        )
        remaining_load = self.load
        power_distribution = []
        for powerplant in sorted_by_cost:
            if remaining_load <= 0:
                # Keep track of unused powerplants
                power_distribution.append(
                    PowerPerPowerplant(
                        name=powerplant.name, p=Decimal(0).quantize(ROUNDING)
                    )
                )
                continue
            powerplant_max_output = powerplant.adjusted_pmax(self.fuels)
            if powerplant_max_output >= remaining_load:
                # last necessary power plant
                power_distribution.append(
                    PowerPerPowerplant(name=powerplant.name, p=remaining_load)
                )
                power_produced = remaining_load
            else:
                power_distribution.append(
                    PowerPerPowerplant(name=powerplant.name, p=powerplant_max_output)
                )
                power_produced = powerplant_max_output
            remaining_load = (remaining_load - power_produced).quantize(
                ROUNDING, ROUND_UP
            )

        return power_distribution
