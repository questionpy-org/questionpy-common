# pylint: disable=unneeded-not

from typing import Optional, NamedTuple

import pytest

from questionpy_common.version import SemVer, APIVersion


class V(NamedTuple):
    major: int
    minor: int = 0
    patch: int = 0
    prerelease: Optional[str] = None
    build: Optional[str] = None


valid_semver: dict[str, V] = {
    '0.0.4': V(0, 0, 4, None, None),
    '1.2.3': V(1, 2, 3, None, None),
    '10.20.30': V(10, 20, 30, None, None),
    '1.1.2-prerelease+meta': V(1, 1, 2, 'prerelease', 'meta'),
    '1.1.2+meta': V(1, 1, 2, None, 'meta'),
    '1.1.2+meta-valid': V(1, 1, 2, None, 'meta-valid'),
    '1.0.0-alpha': V(1, 0, 0, 'alpha', None),
    '1.0.0-beta': V(1, 0, 0, 'beta', None),
    '1.0.0-alpha.beta': V(1, 0, 0, 'alpha.beta', None),
    '1.0.0-alpha.beta.1': V(1, 0, 0, 'alpha.beta.1', None),
    '1.0.0-alpha.1': V(1, 0, 0, 'alpha.1', None),
    '1.0.0-alpha0.valid': V(1, 0, 0, 'alpha0.valid', None),
    '1.0.0-alpha.0valid': V(1, 0, 0, 'alpha.0valid', None),
    '1.0.0-alpha-a.b-c-somethinglong+build.1-aef.1-its-okay': V(1, 0, 0, 'alpha-a.b-c-somethinglong',
                                                                'build.1-aef.1-its-okay'),
    '1.0.0-rc.1+build.1': V(1, 0, 0, 'rc.1', 'build.1'),
    '2.0.0-rc.1+build.123': V(2, 0, 0, 'rc.1', 'build.123'),
    '1.2.3-beta': V(1, 2, 3, 'beta', None),
    '10.2.3-DEV-SNAPSHOT': V(10, 2, 3, 'DEV-SNAPSHOT', None),
    '1.2.3-SNAPSHOT-123': V(1, 2, 3, 'SNAPSHOT-123', None),
    '1.0.0': V(1, 0, 0, None, None),
    '2.0.0': V(2, 0, 0, None, None),
    '1.1.7': V(1, 1, 7, None, None),
    '2.0.0+build.1848': V(2, 0, 0, None, 'build.1848'),
    '2.0.1-alpha.1227': V(2, 0, 1, 'alpha.1227', None),
    '1.0.0-alpha+beta': V(1, 0, 0, 'alpha', 'beta'),
    '1.2.3----RC-SNAPSHOT.12.9.1--.12+788': V(1, 2, 3, '---RC-SNAPSHOT.12.9.1--.12', '788'),
    '1.2.3----R-S.12.9.1--.12+meta': V(1, 2, 3, '---R-S.12.9.1--.12', 'meta'),
    '1.2.3----RC-SNAPSHOT.12.9.1--.12': V(1, 2, 3, '---RC-SNAPSHOT.12.9.1--.12', None),
    '1.0.0+0.build.1-rc.10000aaa-kk-0.1': V(1, 0, 0, None, '0.build.1-rc.10000aaa-kk-0.1'),
    '99999999999999999999999.999999999999999999.99999999999999999': V(99999999999999999999999, 999999999999999999,
                                                                      99999999999999999, None, None),
    '1.0.0-0A.is.legal': V(1, 0, 0, '0A.is.legal', None)
}


@pytest.mark.parametrize('string, components', valid_semver.items())
def test_valid_semver_initialisation(string: str, components: V) -> None:
    semver = SemVer(*components)

    assert semver.major == components.major
    assert semver.minor == components.minor
    assert semver.patch == components.patch
    assert semver.prerelease == components.prerelease
    assert semver.build == components.build

    assert str(semver) == string


@pytest.mark.parametrize('string, components', valid_semver.items())
def test_valid_semver_string_parsing(string: str, components: V) -> None:
    semver = SemVer.from_string(string)

    assert semver.major == components.major
    assert semver.minor == components.minor
    assert semver.patch == components.patch
    assert semver.prerelease == components.prerelease
    assert semver.build == components.build

    assert str(semver) == string


@pytest.mark.parametrize('string', [
    '1',
    '1.2',
    '1.2.3-0123',
    '1.2.3-0123.0123',
    '1.1.2+.123',
    '+invalid',
    '-invalid',
    '-invalid+invalid',
    '-invalid.01',
    'alpha',
    'alpha.beta',
    'alpha.beta.1',
    'alpha.1',
    'alpha+beta',
    'alpha_beta',
    'alpha.',
    'alpha..',
    'beta',
    '1.0.0-alpha_beta',
    '-alpha.',
    '1.0.0-alpha..',
    '1.0.0-alpha..1',
    '1.0.0-alpha...1',
    '1.0.0-alpha....1',
    '1.0.0-alpha.....1',
    '1.0.0-alpha......1',
    '1.0.0-alpha.......1',
    '01.1.1',
    '1.01.1',
    '1.1.01',
    '1.2',
    '1.2.3.DEV',
    '1.2-SNAPSHOT',
    '1.2.31.2.3----RC-SNAPSHOT.12.09.1--..12+788',
    '1.2-RC-SNAPSHOT',
    '-1.0.3-gamma+b7718',
    '+justmeta',
    '9.8.7+meta+meta',
    '9.8.7-whatever+meta+meta',
    '99999999999999999999999.999999999999999999.99999999999999999----RC-SNAPSHOT.12.09.1-------------------------..12'
])
def test_invalid_semver_string_parsing(string: str) -> None:
    with pytest.raises(ValueError, match='invalid SemVer string'):
        SemVer.from_string(string)


@pytest.mark.parametrize('components', [
    (-1,),
    (0, -1),
    (0, 0, -1)
])
def test_semver_initialisation_with_negative_values_raise_error(components: tuple) -> None:
    with pytest.raises(ValueError, match='negative version parts are not allowed'):
        SemVer(*components)


@pytest.mark.parametrize('components', valid_semver.values())
def test_semver_equality_check(components: V) -> None:
    semver_1 = SemVer(*components)
    semver_2 = SemVer(*components)

    assert semver_1 == semver_2
    assert semver_1 >= semver_2
    assert semver_1 <= semver_2
    assert not semver_1 != semver_2
    assert not semver_1 > semver_2
    assert not semver_1 < semver_2


@pytest.mark.parametrize('version_1, version_2', [
    ('1.0.0', '1.1.1'),
    ('1.0.0', '1.1.0'),
    ('1.0.0', '1.1.1'),
    ('1.0.0', '2.0.0'),
    ('1.0.9', '1.0.10'),
    ('1.9.0', '1.10.0'),
    ('1.9.0', '2.0.0')
])
def test_semver_inequality_check(version_1: str, version_2: str) -> None:
    semver_1 = SemVer.from_string(version_1)
    semver_2 = SemVer.from_string(version_2)

    assert semver_1 != semver_2
    assert semver_1 < semver_2
    assert semver_1 <= semver_2
    assert not semver_1 == semver_2
    assert not semver_1 > semver_2
    assert not semver_1 >= semver_2

    assert semver_2 != semver_1
    assert semver_2 > semver_1
    assert semver_2 >= semver_1
    assert not semver_2 == semver_1
    assert not semver_2 < semver_1
    assert not semver_2 <= semver_1


valid_api_versions = {
    '0.0': V(0, 0),
    '0.1': V(0, 1),
    '1.0': V(1, 0),
    '42.21': V(42, 21),
    '10.10': V(10, 10),
    '9999999999999.99999999999': V(9999999999999, 99999999999)
}


@pytest.mark.parametrize('string, components', valid_api_versions.items())
def test_valid_api_version_initialisation(string: str, components: V) -> None:
    api = APIVersion(*components[:2])

    assert api.major == components.major
    assert api.minor == components.minor

    assert str(api) == string


@pytest.mark.parametrize('string, components', valid_api_versions.items())
def test_valid_api_version_string_parsing(string: str, components: V) -> None:
    api = APIVersion(*components[:2])

    assert api.major == components.major
    assert api.minor == components.minor

    assert str(api) == string


@pytest.mark.parametrize('string', [
    '-0.0',
    '0.-0',
    '0.0-',
    '0.0.0',
    '42',
    '1 0',
    'invalid'
])
def test_invalid_api_version_string_parsing(string: str) -> None:
    with pytest.raises(ValueError, match='invalid API version string'):
        APIVersion.from_string(string)


@pytest.mark.parametrize('components', [
    (-1,),
    (0, -1),
])
def test_api_version_initialisation_with_negative_values_raise_error(components: tuple) -> None:
    with pytest.raises(ValueError, match='negative version parts are not allowed'):
        APIVersion(*components)


@pytest.mark.parametrize('components', valid_api_versions.values())
def test_api_version_equality_check(components: V) -> None:
    api_components = components[:2]
    version_1 = APIVersion(*api_components)
    version_2 = APIVersion(*api_components)

    assert version_1 == version_2
    assert version_1 >= version_2
    assert version_1 <= version_2
    assert not version_1 != version_2
    assert not version_1 > version_2
    assert not version_1 < version_2


@pytest.mark.parametrize('version_1, version_2', [
    ('0.0', '0.1'),
    ('0.1', '1.0'),
    ('1.0', '1.1'),
    ('1.0', '2.0'),
    ('11.0', '12.0'),
])
def test_api_version_inequality_check(version_1: str, version_2: str) -> None:
    api_1 = APIVersion.from_string(version_1)
    api_2 = APIVersion.from_string(version_2)

    assert api_1 != api_2
    assert api_1 < api_2
    assert api_1 <= api_2
    assert not api_1 == api_2
    assert not api_1 > api_2
    assert not api_1 >= api_2

    assert api_2 != api_1
    assert api_2 > api_1
    assert api_2 >= api_1
    assert not api_2 == api_1
    assert not api_2 < api_1
    assert not api_2 <= api_1
