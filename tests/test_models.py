import pytest

from decimal import Decimal

from powerplant_app.models import FuelPrices


@pytest.mark.parametrize("co2_value", [0, 1000, 10000])
def test_co2_adjustment(
    co2_value,
    co2_euro_per_ton,
    kerosine_euro_per_mwh,
    gas_euro_per_mwh,
    wind_efficiency,
    monkeypatch,
):
    monkeypatch.setattr("powerplant_app.models.CO2_TONS_PER_KWH", co2_value)
    fuel_prices = FuelPrices(
        **{
            "gas(euro/MWh)": gas_euro_per_mwh,
            "kerosine(euro/MWh)": kerosine_euro_per_mwh,
            "co2(euro/ton)": co2_euro_per_ton,
            "wind(%)": wind_efficiency,
        }
    )
    # no adjustment for these
    assert fuel_prices.co2 == co2_euro_per_ton
    assert fuel_prices.wind == wind_efficiency
    # ajustment for these
    assert fuel_prices.gas == Decimal(
        gas_euro_per_mwh + co2_value * co2_euro_per_ton * 1000
    ).quantize(Decimal("0.1"))
    assert fuel_prices.kerosine == Decimal(
        kerosine_euro_per_mwh + co2_value * co2_euro_per_ton * 1000
    ).quantize(Decimal("0.1"))
