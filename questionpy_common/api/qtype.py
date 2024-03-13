#  This file is part of QuestionPy. (https://questionpy.org)
#  QuestionPy is free software released under terms of the MIT license. See LICENSE.md.
#  (c) Technische Universität Berlin, innoCampus <info@isis.tu-berlin.de>

from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic, Mapping

from .question import BaseQuestion
from ..elements import OptionsFormDefinition

__all__ = ["BaseQuestionType", "OptionsFormValidationError"]

_Q = TypeVar("_Q", bound=BaseQuestion)


class BaseQuestionType(ABC, Generic[_Q]):
    @abstractmethod
    def get_options_form(self, question: Optional[_Q]) -> tuple[OptionsFormDefinition, Mapping[str, object]]:
        """Get the form used to create a new or edit an existing question.

        Args:
            question: The current question if editing, or ``None`` if creating a new question.

        Returns:
            Tuple of the form definition and the current data of the inputs.
        """

    @abstractmethod
    def create_question_from_options(self, form_data: Mapping[str, object],
                                     old_question: Optional[_Q]) -> _Q:
        """Create or update the question (state) with the form data from a submitted question edit form.

        Args:
            form_data: Form data from a submitted question edit form.
            old_question: Current question if editing, or ``None`` if creating a new question.

        Returns:
            New or updated question object.

        Raises:
            OptionsFormValidationError: When `form_data` is invalid.
        """

    @abstractmethod
    def create_question_from_state(self, question_state: str) -> _Q:
        """Deserialize the given question state, returning a question object equivalent to the one which exported it."""


class OptionsFormValidationError(Exception):
    def __init__(self, errors: dict[str, str]):
        """There was at least one validation error."""
        self.errors = errors  # input element name -> error description
        super().__init__("Form input data could not be validated successfully.")
