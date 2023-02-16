import re
from enum import Enum
from keyword import iskeyword, issoftkeyword
from typing import Optional, Union, Annotated

from pydantic import BaseModel
from pydantic.class_validators import validator
from pydantic.fields import Field


class PackageType(str, Enum):
    LIBRARY = 'LIBRARY'
    QUESTIONTYPE = 'QUESTIONTYPE'
    QUESTION = 'QUESTION'


# Defaults.
DEFAULT_ENTRYPOINT = '__main__'
DEFAULT_NAMESPACE = 'default'
DEFAULT_PACKAGETYPE = PackageType.QUESTIONTYPE

# Regular expressions.
RE_SEMVER = re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)'
                       r'(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$')
RE_VALID_CHARS = re.compile(r"^[a-z1-9_]+$")


# Validators.
def ensure_is_valid_name(name: str) -> str:
    """
    Raises ValueError if the given name does not match the following conditions:
    It should be:
        - a valid Python identifier
        - NOT a Python keyword
        - lowercase
        - URL-friendly (i.e. only characters which will not be %-escaped)

    :param name: the name to be checked
    :return: name
    """
    length = len(name)

    if length < 1:
        raise ValueError("can not be empty")
    if not RE_VALID_CHARS.match(name):
        raise ValueError("can only contain lowercase alphanumeric characters and underscores")
    if length > 127:
        raise ValueError("can have at most 127 characters")
    if name[0].isdigit():
        raise ValueError("can not start with a digit")
    if not name.isidentifier():
        # This check should be redundant - we keep it just in case.
        raise ValueError("is not a valid Python identifier")
    if iskeyword(name) or issoftkeyword(name) or name in ["_", "case", "match"]:
        raise ValueError("can not be a Python keyword")

    return name


class Manifest(BaseModel):
    short_name: str
    namespace: str = DEFAULT_NAMESPACE
    version: Annotated[str, Field(regex=RE_SEMVER.pattern)]
    api_version: Annotated[str, Field(regex=RE_SEMVER.pattern)]
    author: str
    name: dict[str, str] = {}
    entrypoint: str = DEFAULT_ENTRYPOINT
    url: Optional[str] = None
    languages: set[str] = set()
    description: dict[str, str] = {}
    icon: Optional[str] = None
    type: PackageType = DEFAULT_PACKAGETYPE
    license: Optional[str] = None
    permissions: set[str] = set()
    tags: set[str] = set()
    requirements: Optional[Union[str, list[str]]] = None

    @validator('short_name', 'namespace')
    # pylint: disable=no-self-argument
    def ensure_is_valid_name(cls, value: str) -> str:
        return ensure_is_valid_name(value)

    @property
    def identifier(self) -> str:
        return f"@{self.namespace}/{self.short_name}"
