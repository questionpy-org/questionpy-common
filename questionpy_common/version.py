import re
from functools import total_ordering
from typing import Callable, Iterator, Optional


@total_ordering
class _ComparableVersion:
    """
    A multipart version that can be compared to other versions.
    """
    def __init__(self, part: int, *parts: int):
        parts = (part,) + parts

        for part in parts:
            if part < 0:
                raise ValueError("negative version parts are not allowed")

        self._length = len(parts)
        self._parts = parts

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, _ComparableVersion) or self._length != other._length:
            return NotImplemented

        for left, right in zip(self._parts, other._parts):
            if left < right:
                return True
            if left > right:
                return False

        return False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _ComparableVersion) or self._length != other._length:
            return NotImplemented
        return self._parts == other._parts


class APIVersion(_ComparableVersion):
    """
    Represents an API version consisting of a major and minor version number.
    """

    _RE_API = re.compile(r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)$')

    def __init__(self, major: int, minor: int = 0):
        super().__init__(major, minor)

        self._str: Optional[str] = None
        self._repr: Optional[str] = None

    @property
    def major(self) -> int:
        return self._parts[0]

    @property
    def minor(self) -> int:
        return self._parts[1]

    @classmethod
    def from_string(cls, version: str) -> 'APIVersion':
        if not (match := cls._RE_API.match(version)):
            raise ValueError("invalid API version string")

        major = int(match.group('major'))
        minor = int(match.group('minor'))

        return cls(major, minor)

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable[[str], 'APIVersion']]:
        yield cls.from_string

    def __str__(self) -> str:
        if self._str is None:
            self._str = f'{self.major}.{self.minor}'
        return self._str

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(major={self.major}, minor={self.minor})'


class SemVer(_ComparableVersion):
    """
    Represents a semantic version consisting of a major, minor and patch version number. Optionally, a prerelease and
    build version can be specified.
    """
    _RE_SEMVER = re.compile(r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)'
                            r'(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)'
                            r'(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
                            r'(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$')

    def __init__(self, major: int, minor: int = 0, patch: int = 0, prerelease: Optional[str] = None,
                 build: Optional[str] = None):
        super().__init__(major, minor, patch)

        self._prerelease = prerelease
        self._build = build

        self._str: Optional[str] = None
        self._repr: Optional[str] = None

    @property
    def major(self) -> int:
        return self._parts[0]

    @property
    def minor(self) -> int:
        return self._parts[1]

    @property
    def patch(self) -> int:
        return self._parts[2]

    @property
    def prerelease(self) -> Optional[str]:
        return self._prerelease

    @property
    def build(self) -> Optional[str]:
        return self._build

    @classmethod
    def from_string(cls, version: str) -> 'SemVer':
        if not (match := cls._RE_SEMVER.match(version)):
            raise ValueError("invalid SemVer string")

        major = int(match.group('major'))
        minor = int(match.group('minor'))
        patch = int(match.group('patch'))

        prerelease = match.group('prerelease')
        build = match.group('build')

        return cls(major, minor, patch, prerelease, build)

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable[[str], 'SemVer']]:
        yield cls.from_string

    def __str__(self) -> str:
        if self._str is None:
            self._str = f'{self.major}.{self.minor}.{self.patch}'
            if self.prerelease:
                self._str += f'-{self.prerelease}'
            if self.build:
                self._str += f'+{self.build}'
        return self._str

    def __repr__(self) -> str:
        if self._repr is None:
            self._repr = f'{self.__class__.__name__}(major={self.major}, minor={self.minor}, patch={self.patch},' \
                         f'prerelease={self.prerelease}, build={self.build})'
        return self._repr
