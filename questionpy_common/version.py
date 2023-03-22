import re
from functools import total_ordering
from typing import Callable, Iterator

from semver import VersionInfo  # type: ignore


class SemVer(VersionInfo):
    @classmethod
    def _parse(cls, version: str) -> 'SemVer':
        return cls.parse(version)

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable[[str], 'SemVer']]:
        yield cls._parse


RE_API = re.compile(r'^(?P<major>\d+)\.(?P<minor>\d+)$')


@total_ordering
class APIVersion:
    def __init__(self, major: int, minor: int = 0):
        if major < 0 or minor < 0:
            raise ValueError("each number of the version must be zero or positive")
        self.major = major
        self.minor = minor

    @classmethod
    def _parse(cls, version: str) -> 'APIVersion':
        if not (match := RE_API.match(version)):
            raise ValueError(f"'{version}' is not valid")
        major = int(match.group('major'))
        minor = int(match.group('minor'))
        return cls(major, minor)

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable[[str], 'APIVersion']]:
        yield cls._parse

    def __str__(self) -> str:
        return f'{self.major}.{self.minor}'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(major={self.major}, minor={self.minor})'

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, APIVersion):
            raise NotImplementedError()
        if self.major < other.major:
            return True
        if self.major == other.major:
            return self.minor < other.minor
        return False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, APIVersion):
            raise NotImplementedError()
        return (self.major, self.minor) == (other.major, other.minor)
