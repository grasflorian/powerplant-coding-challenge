from fastapi import APIRouter
from ..models import PowerPlanIn, PowerPerPowerplant

powerplans_router = APIRouter()


@powerplans_router.post(
    "/productionplan",
    response_model=list[PowerPerPowerplant],
    description="Produces an optimized power production distribution for cost for the load, powerplants and fuel prices given",
    response_description="A power production plan optimized for cost",
)
async def optimize_production_plan(powerplan: PowerPlanIn):
    return powerplan.optimize()
