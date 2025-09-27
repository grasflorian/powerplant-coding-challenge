import pytest

from powerplant_app.models import FuelPrices

from fastapi.testclient import TestClient
from powerplant_app.app import app


@pytest.fixture
def co2_euro_per_ton():
    return 20


@pytest.fixture
def gas_euro_per_mwh():
    return 13.4


@pytest.fixture
def kerosine_euro_per_mwh():
    return 50.8


@pytest.fixture
def wind_efficiency():
    return 60


@pytest.fixture
def fuel_prices(
    co2_euro_per_ton, gas_euro_per_mwh, kerosine_euro_per_mwh, wind_efficiency
) -> FuelPrices:
    return FuelPrices(
        **{
            "gas(euro/MWh)": gas_euro_per_mwh,
            "kerosine(euro/MWh)": kerosine_euro_per_mwh,
            "co2(euro/ton)": co2_euro_per_ton,
            "wind(%)": wind_efficiency,
        }
    )


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
