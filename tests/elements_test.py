from typing import Type

import pytest
from pydantic import BaseModel
from pydantic_factories import ModelFactory

from questionpy_common.dev.factories import StaticTextElementFactory, TextInputElementFactory, CheckboxElementFactory, \
    CheckboxGroupElementFactory, OptionFactory, RadioGroupElementFactory, SelectElementFactory, HiddenElementFactory, \
    GroupElementFactory, FormSectionFactory, OptionsFormDefinitionFactory
from questionpy_common.elements import StaticTextElement, TextInputElement, CheckboxElement, CheckboxGroupElement, \
    Option, RadioGroupElement, SelectElement, HiddenElement, GroupElement, FormSection, \
    OptionsFormDefinition, is_form_element, CanHaveConditions


@pytest.mark.parametrize("factory, model", (
    [StaticTextElementFactory, StaticTextElement],
    [TextInputElementFactory, TextInputElement],
    [CheckboxElementFactory, CheckboxElement],
    [CheckboxGroupElementFactory, CheckboxGroupElement],
    [OptionFactory, Option],
    [RadioGroupElementFactory, RadioGroupElement],
    [SelectElementFactory, SelectElement],
    [HiddenElementFactory, HiddenElement],
    [GroupElementFactory, GroupElement],
    [FormSectionFactory, FormSection],
    [OptionsFormDefinitionFactory, OptionsFormDefinition]
))
def test_factory_builds_valid_model(factory: ModelFactory, model: Type[BaseModel]) -> None:
    fake_model = factory.build()
    assert isinstance(fake_model, model)


@pytest.mark.parametrize("factory, model", (
    [StaticTextElementFactory, StaticTextElement],
    [TextInputElementFactory, TextInputElement],
    [CheckboxElementFactory, CheckboxElement],
    [CheckboxGroupElementFactory, CheckboxGroupElement],
    [OptionFactory, Option],
    [RadioGroupElementFactory, RadioGroupElement],
    [SelectElementFactory, SelectElement],
    [HiddenElementFactory, HiddenElement],
    [GroupElementFactory, GroupElement],
    [FormSectionFactory, FormSection],
    [OptionsFormDefinitionFactory, OptionsFormDefinition]
))
def test_ignore_additional_properties(factory: ModelFactory, model: Type[BaseModel]) -> None:
    data = factory.build().dict()
    created_model = model(**data, additional_property='test')
    assert not hasattr(created_model, 'additional_property')


@pytest.mark.parametrize("factory", (
    StaticTextElementFactory,
    TextInputElementFactory,
    CheckboxElementFactory,
    CheckboxGroupElementFactory,
    RadioGroupElementFactory,
    SelectElementFactory,
    HiddenElementFactory,
    GroupElementFactory,
))
def test_is_form_element_should_return_true(factory: ModelFactory) -> None:
    assert is_form_element(factory.build())


@pytest.mark.parametrize("instance", (
    object(),
    CanHaveConditions(),
    Option(label="", value=""),
    FormSection(header="", elements=[]),
    OptionsFormDefinition()
))
def test_is_form_element_should_return_false(instance: object) -> None:
    assert not is_form_element(instance)
