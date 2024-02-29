#  This file is part of QuestionPy. (https://questionpy.org)
#  QuestionPy is free software released under terms of the MIT license. See LICENSE.md.
#  (c) Technische Universität Berlin, innoCampus <info@isis.tu-berlin.de>

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Sequence, Annotated

from pydantic import BaseModel, Field

__all__ = ["CacheControl", "UiFile", "AttemptUi", "AttemptModel", "ScoringCode", "ClassifiedResponse",
           "Score", "AttemptScoredModel", "BaseAttempt"]


class CacheControl(Enum):
    SHARED_CACHE = "SHARED_CACHE"
    PRIVATE_CACHE = "PRIVATE_CACHE"
    NO_CACHE = "NO_CACHE"


class UiFile(BaseModel):
    name: str
    data: str
    mime_type: Optional[str] = None


class AttemptUi(BaseModel):
    content: str
    """X(H)ML markup of the question UI."""
    placeholders: dict[str, str] = {}
    """Names and values of the ``<?p`` placeholders that appear in content."""
    include_inline_css: Optional[str] = None
    include_css_file: Optional[str] = None
    cache_control: CacheControl = CacheControl.PRIVATE_CACHE
    files: list[UiFile] = []


class AttemptModel(BaseModel):
    variant: int
    ui: AttemptUi


class ScoringCode(Enum):
    AUTOMATICALLY_SCORED = 'AUTOMATICALLY_SCORED'
    NEEDS_MANUAL_SCORING = 'NEEDS_MANUAL_SCORING'
    RESPONSE_NOT_SCORABLE = 'RESPONSE_NOT_SCORABLE'
    INVALID_RESPONSE = 'INVALID_RESPONSE'


class ClassifiedResponse(BaseModel):
    subquestion_id: Annotated[str, Field(max_length=30, strict=True)]
    response_class: Annotated[str, Field(max_length=30, strict=True)]
    response: str
    score: float


class AttemptScoredModel(AttemptModel):
    scoring_state: str = "{}"
    scoring_code: ScoringCode
    score: Optional[float]
    """The total score for this question attempt, as a fraction of the default mark set by the LMS."""
    classification: Optional[Sequence[ClassifiedResponse]] = None


class Score(BaseModel):
    """A score for a particular response during a question attempt."""
    code: ScoringCode
    fraction: Optional[float] = None
    classification: Optional[Sequence[ClassifiedResponse]] = None

    def export_scoring_state(self) -> str:
        """Serialize the score's relevant data."""
        return self.model_dump_json()


class BaseAttempt(ABC):

    @abstractmethod
    def score_response(self) -> Score:
        """Score the current response (which was passed to :meth:`BaseQuestion.get_attempt`)."""

    @abstractmethod
    def export_attempt_state(self) -> str:
        """Serialize this attempt's relevant data.

        A future call to :meth:`BaseQuestion.get_attempt` should result in an attempt object identical to the one which
        exported the state.
        """

    @abstractmethod
    def export(self) -> AttemptModel:
        """Get metadata about this attempt."""
