from pydantic import BaseModel


class SimulationRequest(BaseModel):
    scenario: str


class SimulationResponse(BaseModel):
    simulation: dict

    resilience: dict

    risk: dict

    recommendation: str