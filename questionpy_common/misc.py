from enum import IntEnum
from typing import overload, Union, Optional


class ByteSize(IntEnum):
    # pylint: disable=invalid-name
    B = 1
    KiB = 1024
    MiB = 1024 * KiB
    GiB = 1024 * MiB
    TiB = 1024 * GiB


class Bytes(int):
    """Bytes class for easier byte representation."""

    @overload
    def __new__(cls, value: int, unit: ByteSize = ByteSize.B) -> 'Bytes':
        ...

    @overload
    def __new__(cls, value: float, unit: ByteSize = ByteSize.B) -> 'Bytes':
        ...

    @overload
    def __new__(cls, value: str, unit: ByteSize = ByteSize.B) -> 'Bytes':
        ...

    def __new__(cls, value: Union[int, float, str], unit: ByteSize = ByteSize.B) -> 'Bytes':
        cls._string: Optional[str] = None
        if isinstance(value, int):
            return super().__new__(cls, value * unit)
        if isinstance(value, float):
            return super().__new__(cls, round(value * unit.value))
        if isinstance(value, str):
            return super().__new__(cls, round(float(value) * unit.value))
        raise TypeError(f"Cannot convert {type(value)} to Bytes.")

    @classmethod
    def from_string(cls, string: str) -> 'Bytes':
        """
        Convert a string to a Bytes object.

        :param string: String to convert.
        :return: Bytes object.
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
                return cls(sanitized[:-1], ByteSize.KiB)
            if sanitized.endswith('m'):
                return cls(sanitized[:-1], ByteSize.MiB)
            if sanitized.endswith('g'):
                return cls(sanitized[:-1], ByteSize.GiB)
            if sanitized.endswith('t'):
                return cls(sanitized[:-1], ByteSize.TiB)
            return cls(sanitized)
        except ValueError as e:
            raise ValueError(f"Could not convert '{string}'") from e

    def convert_to(self, unit: ByteSize) -> float:
        """
        Convert to given unit.

        :param unit: Unit to convert to.
        :return: Converted value.
        """

        return self / unit

    def __str__(self) -> str:
        if self._string:
            return self._string

        absolut = abs(self)

        if absolut < ByteSize.KiB:
            self._string = f'{int(self)} {ByteSize.B.name}'
        elif absolut < ByteSize.MiB:
            self._string = f'{self.convert_to(ByteSize.KiB):.2f} {ByteSize.KiB.name}'
        elif absolut < ByteSize.GiB:
            self._string = f'{self.convert_to(ByteSize.MiB):.2f} {ByteSize.MiB.name}'
        elif absolut < ByteSize.TiB:
            self._string = f'{self.convert_to(ByteSize.GiB):.2f} {ByteSize.GiB.name}'
        else:
            self._string = f'{self.convert_to(ByteSize.TiB):.2f} {ByteSize.TiB.name}'

        return self._string

    def __repr__(self) -> str:
        return f'Bytes({self})'
