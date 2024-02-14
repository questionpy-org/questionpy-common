#  This file is part of QuestionPy. (https://questionpy.org)
#  QuestionPy is free software released under terms of the MIT license. See LICENSE.md.
#  (c) Technische Universität Berlin, innoCampus <info@isis.tu-berlin.de>
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Annotated, Union, Mapping, TYPE_CHECKING

from pydantic import BaseModel, Field
from typing_extensions import Self

from .attempt import BaseAttempt

__all__ = ["ScoringMethod", "PossibleResponse", "SubquestionModel", "QuestionModel", "BaseQuestion"]

if TYPE_CHECKING:
    from .qtype import BaseQuestionType


class ScoringMethod(Enum):
    ALWAYS_MANUAL_SCORING_REQUIRED = 'ALWAYS_MANUAL_SCORING_REQUIRED'
    AUTOMATICALLY_SCORABLE = 'AUTOMATICALLY_SCORABLE'
    AUTOMATICALLY_SCORABLE_WITH_COUNTBACK = 'AUTOMATICALLY_SCORABLE_WITH_COUNTBACK'


class PossibleResponse(BaseModel):
    response_class: Annotated[str, Field(max_length=30, strict=True)]
    score: float


class SubquestionModel(BaseModel):
    subquestion_id: Annotated[str, Field(max_length=30, strict=True)]
    score_max: Optional[float]
    response_classes: Optional[list[PossibleResponse]]


class QuestionModel(BaseModel):
    num_variants: Annotated[int, Field(ge=1, strict=True)] = 1
    score_min: float = 0
    """Lowest score used by this question, as a fraction of the default mark set by the LMS."""
    score_max: float = 1
    """Highest score used by this question, as a fraction of the default mark set by the LMS."""
    scoring_method: ScoringMethod
    penalty: Optional[float] = None
    random_guess_score: Optional[float] = None
    response_analysis_by_variant: bool = True

    subquestions: Optional[list[SubquestionModel]] = None


class BaseQuestion(ABC):
    @abstractmethod
    def start_attempt(self, variant: int) -> BaseAttempt:
        """Start an attempt at this question with the given variant.

        Args:
            variant: Not implemented.

        Returns:
            A :class:`BaseAttempt` object representing the attempt.
        """

    @abstractmethod
    def get_attempt(self, attempt_state: str, scoring_state: Optional[str] = None,
                    response: Optional[dict] = None) -> BaseAttempt:
        """Create an attempt object for a previously started attempt.

        Args:
            attempt_state: The attempt state, as previously returned by your implementation of
                           :meth:`BaseAttempt.get_state`.
            scoring_state: The scoring state, as previously returned by your implementation of :meth:`Score.get_state`.
            response: The response currently entered by the student.

        Returns:
            A :class:`BaseAttempt` object which should be identical to the one which generated the given state(s).
        """

    @abstractmethod
    def get_state(self) -> Union[str, Mapping[str, object], BaseModel]:
        """"""

    @classmethod
    @abstractmethod
    def from_state(cls, qtype: "BaseQuestionType", state: str) -> Self:
        """"""

    @abstractmethod
    def export(self) -> QuestionModel:
        """Get metadata about this question."""