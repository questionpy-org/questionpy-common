#  This file is part of QuestionPy. (https://questionpy.org)
#  QuestionPy is free software released under terms of the MIT license. See LICENSE.md.
#  (c) Technische Universität Berlin, innoCampus <info@isis.tu-berlin.de>

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence, Annotated, Union, Mapping, TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel, Field
from typing_extensions import Self

__all__ = ["CacheControl", "UiFile", "AttemptUi", "AttemptModel", "ScoringCode", "ClassifiedResponse",
           "ScoreModel", "AttemptScoredModel", "BaseAttempt"]

if TYPE_CHECKING:
    pass


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


class ScoreModel(BaseModel):
    scoring_state: str = "{}"
    scoring_code: ScoringCode
    score: Optional[float]
    """The total score for this question attempt, as a fraction of the default mark set by the LMS."""
    classification: Optional[Sequence[ClassifiedResponse]] = None


class AttemptScoredModel(AttemptModel, ScoreModel):
    pass


class Score(BaseModel):
    code: ScoringCode
    fraction: Optional[float] = None
    classification: Optional[Sequence[ClassifiedResponse]] = None

    def get_state(self) -> Union[str, Mapping[str, object], BaseModel]:
        return self

    @classmethod
    def from_state(cls, state: str) -> Self:
        return cls.model_validate_json(state)


_Q = TypeVar("_Q", bound="BaseQuestion")


class BaseAttempt(ABC, Generic[_Q]):

    @abstractmethod
    def get_state(self) -> Union[str, Mapping[str, object], BaseModel]:
        """"""

    @classmethod
    @abstractmethod
    def from_state(cls, question: _Q, attempt_state: str, scoring_state: Optional[str],
                   response: Optional[dict]) -> Self:
        """"""

    @abstractmethod
    def score_response(self) -> Score:
        """"""

    @abstractmethod
    def export(self) -> AttemptModel:
        """Get metadata about this attempt."""
