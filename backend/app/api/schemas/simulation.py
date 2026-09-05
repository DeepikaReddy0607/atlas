from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    """
    Request for a network failure simulation.

    Supported scenarios:
        critical
        critical_node
        node
        critical_edge
        edge
    """

    scenario: str = Field(
        ...,
        min_length=1,
        description="Simulation scenario.",
    )

    node: list[int] | None = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="Selected node as [x, y].",
    )

    edge: list[list[int]] | None = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="Selected edge as [[x1, y1], [x2, y2]].",
    )


class SimulationResponse(BaseModel):
    simulation: dict

    resilience: dict

    risk: dict

    recommendation: str

