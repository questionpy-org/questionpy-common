from enum import Enum
from keyword import iskeyword, issoftkeyword
from typing import Optional, Union, Annotated
from urllib.parse import quote

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
RE_SEMVER = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)' \
            r'(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'


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
    if len(name) > 127:
        raise ValueError("can only have at most 127 character")
    if not name.isidentifier():
        raise ValueError("is not valid")
    if iskeyword(name) or issoftkeyword(name) or name in ["_", "case", "match"]:
        raise ValueError("can not be a Python keyword")
    if not name.islower():
        raise ValueError("has to be lowercase")
    if quote(name) != name:
        raise ValueError("can only contain URL-friendly characters")
    return name


class Manifest(BaseModel):
    short_name: str
    namespace: str = DEFAULT_NAMESPACE
    version: Annotated[str, Field(regex=RE_SEMVER)]
    api_version: Annotated[str, Field(regex=RE_SEMVER)]
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
