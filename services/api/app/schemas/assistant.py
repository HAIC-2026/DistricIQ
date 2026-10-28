from typing import Annotated, Literal

from pydantic import Field, StringConstraints, model_validator

from app.schemas.discovery import StrictModel

DISTRICT_PATTERN = r"^(?:house-(?:0[1-9]|[1-4][0-9]|5[01])|senate-(?:0[1-9]|1[0-9]|2[0-5]))$"
DistrictId = Annotated[str, StringConstraints(pattern=DISTRICT_PATTERN)]


class ChatMessage(StrictModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1200)


class ChatRequest(StrictModel):
    message: str = Field(min_length=1, max_length=2000)
    district_id: DistrictId | None = None
    history: list[ChatMessage] = Field(default_factory=list, max_length=12)

    @model_validator(mode="after")
    def validate_history(self):
        if not self.message.strip():
            raise ValueError("Message cannot be blank")
        if len(self.history) % 2 or any(
            m.role != ("user" if i % 2 == 0 else "assistant") for i, m in enumerate(self.history)
        ):
            raise ValueError("History must contain complete user/assistant pairs")
        if sum(len(m.content) for m in self.history) > 12000:
            raise ValueError("Conversation history exceeds limit")
        return self


class AnswerSelection(StrictModel):
    intent: Literal[
        "facts",
        "summary",
        "comparison",
        "distribution",
        "missing",
        "moe",
        "clarification",
        "out_of_scope",
        "unsupported",
        "context",
        "programs",
    ]
    fact_refs: list[str] = Field(max_length=26)
    comparison_refs: list[str] = Field(max_length=8)
    active_district_id: DistrictId | None
    explanations: list[
        Literal[
            "moe",
            "missing",
            "comparison",
            "housing",
            "bins",
            "joint",
            "eligibility",
            "hardship",
            "instability",
            "remainder",
            "trends",
            "householder",
        ]
    ] = Field(max_length=5)
    presentation: Literal["brief", "key_findings", "table"] | None = Field(
        default=None,
        description="Choose a brief direct answer, prioritized findings, or a comparison table. Null lets the server fit the evidence.",
    )
    insight: Literal["income_sources", "housing", "service_planning"] | None = Field(
        default=None,
        description="Optional short interpretation, only when relevant to the question and supported by selected evidence. Null for simple facts.",
    )
    follow_up: Literal["state_comparison", "age_distribution", "source_details"] | None = Field(
        default=None,
        description="One specific optional next analysis. Use null unless it helps resolve the user's question; never append one routinely.",
    )
    program_ids: list[str] | None = Field(
        default=None,
        max_length=5,
        description="Select the most relevant retrieved program IDs in priority order, usually two or three. Null keeps the retrieved list; never invent IDs.",
    )
