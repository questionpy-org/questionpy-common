from enum import IntEnum
from typing import Optional, Union


class SizeUnit(IntEnum):
    # pylint: disable=invalid-name
    B = 1
    KiB = 1024
    MiB = 1024 * KiB
    GiB = 1024 * MiB
    TiB = 1024 * GiB


class Size(int):
    """Size class for easier byte representation."""

    def __new__(cls, value: Union[int, float, str], unit: SizeUnit = SizeUnit.B) -> 'Size':
        if isinstance(value, int):
            return super().__new__(cls, value * unit)
        if isinstance(value, float):
            return super().__new__(cls, round(value * unit.value))
        if isinstance(value, str):
            return super().__new__(cls, round(float(value) * unit.value))
        raise TypeError(f"Cannot convert {type(value)} to Size.")

    def __init__(self, _value: Union[int, float, str], _unit: SizeUnit = SizeUnit.B):
        self._string: Optional[str] = None

    @classmethod
    def from_string(cls, string: str) -> 'Size':
        """
        Convert a string to a Size object.

        :param string: String to convert.
        :return: Size object.
        """

        # Remove whitespace and lowercase the string
        sanitized = string.rstrip().lower()

        # Remove the unit from the string
        if sanitized.endswith('ib'):
            sanitized = sanitized[:-2]
        if sanitized.endswith('b'):
            sanitized = sanitized[:-1]

        # Check binary prefix and return the correct value
        try:
            if sanitized.endswith('k'):
                return cls(sanitized[:-1], SizeUnit.KiB)
            if sanitized.endswith('m'):
                return cls(sanitized[:-1], SizeUnit.MiB)
            if sanitized.endswith('g'):
                return cls(sanitized[:-1], SizeUnit.GiB)
            if sanitized.endswith('t'):
                return cls(sanitized[:-1], SizeUnit.TiB)
            return cls(sanitized)
        except ValueError as e:
            raise ValueError(f"Could not convert '{string}'") from e

    def convert_to(self, unit: SizeUnit) -> float:
        """
        Convert to given unit.

        :param unit: Unit to convert to.
        :return: Converted value.
        """

        return self / unit

    def __str__(self) -> str:
        if self._string:
            return self._string

        absolute = abs(self)

        if absolute < SizeUnit.KiB:
            self._string = f'{int(self)} {SizeUnit.B.name}'
        elif absolute < SizeUnit.MiB:
            self._string = f'{self.convert_to(SizeUnit.KiB):.2f} {SizeUnit.KiB.name}'
        elif absolute < SizeUnit.GiB:
            self._string = f'{self.convert_to(SizeUnit.MiB):.2f} {SizeUnit.MiB.name}'
        elif absolute < SizeUnit.TiB:
            self._string = f'{self.convert_to(SizeUnit.GiB):.2f} {SizeUnit.GiB.name}'
        else:
            self._string = f'{self.convert_to(SizeUnit.TiB):.2f} {SizeUnit.TiB.name}'

        return self._string

    def __repr__(self) -> str:
        return f'Size({self})'
