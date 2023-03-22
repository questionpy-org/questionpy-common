import re
from enum import Enum
from keyword import iskeyword, issoftkeyword
from typing import Optional, Union

from pydantic import BaseModel
from pydantic.class_validators import validator

from questionpy_common.version import SemVer, APIVersion


class PackageType(str, Enum):
    LIBRARY = 'LIBRARY'
    QUESTIONTYPE = 'QUESTIONTYPE'
    QUESTION = 'QUESTION'


# Defaults.
DEFAULT_ENTRYPOINT = '__main__'
DEFAULT_NAMESPACE = 'local'
DEFAULT_PACKAGETYPE = PackageType.QUESTIONTYPE

# Regular expressions.
RE_VALID_CHARS_NAME = re.compile(r"^[a-z\d_]+$")


# Validators.
def ensure_is_valid_name(name: str) -> str:
    """
    Raises ValueError if the given name does not match the following conditions:
        - contains only lowercase alphanumeric characters and underscores
        - is 1 - 127 characters long
        - does not start with a number
        - is a valid Python identifier
        - is NOT a Python keyword

    :param name: the name to be checked
    :return: name
    """
    length = len(name)

    if length < 1:
        raise ValueError("can not be empty")
    if not RE_VALID_CHARS_NAME.match(name):
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
    version: SemVer
    api_version: APIVersion
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

    class Config:
        json_encoders = {
            SemVer: str,
            APIVersion: str
        }
