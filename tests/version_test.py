from typing import Optional

import pytest
from pydantic import BaseModel, parse_raw_as

from questionpy_common.version import SemVer, APIVersion


def test_use_semver_in_basemodel() -> None:
    class Model(BaseModel):
        version: SemVer

        class Config:
            json_encoders = {
                SemVer: str,
            }

    model_1 = Model(version='1.0.0')
    json = model_1.json()
    model_2 = parse_raw_as(Model, json)

    assert model_1 == model_2


def test_use_api_version_in_basemodel() -> None:
    class Model(BaseModel):
        version: APIVersion

        class Config:
            json_encoders = {
                APIVersion: str,
            }

    model_1 = Model(version="1.0")
    json = model_1.json()
    model_2 = parse_raw_as(Model, json)

    assert model_1 == model_2


@pytest.mark.parametrize('version', [
    '0.0',
    '0.1',
    '1.0',
    '42.21',
    '00.00',
    '010.010',
])
def test_parse_api_version_successfully(version: str) -> None:
    APIVersion._parse(version)


@pytest.mark.parametrize('version', [
    '-0.0',
    '0.-0',
    '0.0-',
    '0.0.0',
    '42',
    '1 0',
])
def test_parse_api_version_unsuccessfully(version: str) -> None:
    with pytest.raises(ValueError):
        APIVersion._parse(version)


@pytest.mark.parametrize('v_1, v_2', [
    ('0.0', '1.0'),
    ('0.0', '1.0'),
    ('0.0', '1.0'),
    ('0.0', '1.0'),
    ('0.0', '1.0'),
])
def test_compare_api_version_inequality(v_1: str, v_2: str) -> None:
    version_1 = APIVersion._parse(v_1)
    version_2 = APIVersion._parse(v_2)

    assert version_1 < version_2
    assert version_1 <= version_2
    assert version_2 > version_1
    assert version_2 >= version_1


@pytest.mark.parametrize('version', [
    '0.0',
    '1.0',
    '12.0',
    '0.12',
    '12.12'
])
def test_compare_api_version_equality(version: str) -> None:
    version_1 = APIVersion._parse(version)
    version_2 = APIVersion._parse(version)

    assert version_1 == version_2
    assert version_1 <= version_2
    assert version_1 >= version_2
    assert not version_1 != version_2  # pylint: disable unneeded-not


@pytest.mark.parametrize('major, minor', [
    (0, None),
    (0, 0),
    (1, None),
    (1, 1),
    (42, None),
    (42, 0),
    (42, 42)
])
def test_successful_initialisation(major: int, minor: Optional[int]) -> None:
    if minor:
        APIVersion(major, minor)
    else:
        APIVersion(major)


@pytest.mark.parametrize('major, minor', [
    (0, -1),
    (-1, None),
    (-1, 0),
    (-1, -1),
    (-42, 0),
    (0, -42)
])
def test_unsuccessful_initialisation(major: int, minor: Optional[int]) -> None:
    with pytest.raises(ValueError):
        if minor:
            APIVersion(major, minor)
        else:
            APIVersion(major)
