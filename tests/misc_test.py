from unittest.mock import patch

import pytest

from questionpy_common.misc import Bytes, ByteSize


@pytest.mark.parametrize('byte_size, expected', [
    (ByteSize.B, 1),
    (ByteSize.KiB, 1024),
    (ByteSize.MiB, 1048576),
    (ByteSize.GiB, 1073741824),
    (ByteSize.TiB, 1099511627776),
])
def test_byte_size(byte_size: ByteSize, expected: int) -> None:
    assert byte_size == expected


@pytest.mark.parametrize('value, unit, expected', [
    # Integers.
    (1, ByteSize.B, 1),
    (1024, ByteSize.B, 1024),
    (1, ByteSize.KiB, 1024),
    (1, ByteSize.MiB, 1048576),
    (1, ByteSize.GiB, 1073741824),
    (1, ByteSize.TiB, 1099511627776),
    (-1, ByteSize.KiB, -1024),

    # Floats.
    (0.4, ByteSize.B, 0),
    (0.6, ByteSize.B, 1),
    (1.0, ByteSize.B, 1),
    (0.5, ByteSize.KiB, 512),

    (-0.4, ByteSize.B, 0),
    (-0.6, ByteSize.B, -1),
    (-0.5, ByteSize.KiB, -512),

    # Strings.
    ('0.4', ByteSize.B, 0),
    ('0.6', ByteSize.B, 1),
    ('1.5', ByteSize.KiB, 1536),
    ('1', ByteSize.MiB, 1048576),
    ('1', ByteSize.GiB, 1073741824),
    ('1', ByteSize.TiB, 1099511627776),

    ('+0.4', ByteSize.B, 0),
    ('+0.6', ByteSize.B, 1),
    ('+1.5', ByteSize.KiB, 1536),
    ('+1', ByteSize.MiB, 1048576),
    ('+1', ByteSize.GiB, 1073741824),
    ('+1', ByteSize.TiB, 1099511627776),

    ('-0.4', ByteSize.B, 0),
    ('-0.6', ByteSize.B, -1),
    ('-1.5', ByteSize.KiB, -1536),
    ('-1', ByteSize.MiB, -1048576),
    ('-1', ByteSize.GiB, -1073741824),
    ('-1', ByteSize.TiB, -1099511627776),
])
def test_init(value: float, unit: ByteSize, expected: int) -> None:
    assert Bytes(value, unit) == expected


def test_zero() -> None:
    assert 0 == Bytes(0) == Bytes(-0) == Bytes(0.0) == Bytes(-0.0) == Bytes('0') == Bytes('-0') == Bytes('+0') == \
           Bytes('0.0') == Bytes('-0.0') == Bytes('+0.0')


def test_incorrect_type() -> None:
    with pytest.raises(TypeError):
        Bytes([])  # type: ignore


@pytest.mark.parametrize('value', [
    '10,0',
    '1 00'
    '--1',
    '++1',
    '1-1',
    '1.0.0',
    'abc',
    '100abc',
    'abc100',
    'abc100abc',
    '100 abc',
    'abc 100',
    'abc 100 abc',
])
def test_incorrect_input(value: str) -> None:
    with pytest.raises(ValueError):
        Bytes(value)


@pytest.mark.parametrize('string, expected', [
    # Without unit.
    ('0', 0),
    ('1', 1),
    ('1.0', 1),
    ('1.4', 1),
    ('1.6', 2),
    ('1024', 1024),
    ('1024.0', 1024),
    ('1024.5', 1024),
    ('1024.6', 1025),

    # With unit.
    ('1 b', 1),
    ('1 B', 1),
    ('1k', 1024),
    ('1kb', 1024),
    ('1KB', 1024),
    ('1kib', 1024),
    ('1 m', 1048576),
    ('1 mb', 1048576),
    ('1 MB', 1048576),
    ('1 mib', 1048576),
    ('1 G', 1073741824),
    ('1 Gb', 1073741824),
    ('1 gB', 1073741824),
    ('1 giB', 1073741824),
    ('1 T  ', 1099511627776),
    ('  1 tib', 1099511627776),
    ('  1 TiB  ', 1099511627776),
])
def test_from_string(string: str, expected: int) -> None:
    assert Bytes.from_str(string) == expected


@pytest.mark.parametrize('string', [
    '1.0.0',
    'KiB',
    '1 KiB KiB',
    '1 5',
    '1 5 MiB',
])
def test_from_string_not_valid(string: str) -> None:
    with pytest.raises(ValueError):
        Bytes.from_str(string)


@pytest.mark.parametrize('value, unit, expected', [
    (Bytes(1), ByteSize.B, 1),
    (Bytes(0), ByteSize.B, 0),
    (Bytes(-1), ByteSize.B, -1),

    (Bytes(1024), ByteSize.KiB, 1),
    (Bytes(1, ByteSize.KiB), ByteSize.B, 1024),

    (Bytes(1024, ByteSize.MiB), ByteSize.GiB, 1),
    (Bytes(1, ByteSize.GiB), ByteSize.MiB, 1024),

    (Bytes(1024, ByteSize.MiB), ByteSize.GiB, 1),
    (Bytes(1, ByteSize.GiB), ByteSize.MiB, 1024),

    (Bytes(1024, ByteSize.GiB), ByteSize.TiB, 1),
    (Bytes(1, ByteSize.TiB), ByteSize.GiB, 1024),

    (Bytes(1024, ByteSize.TiB), ByteSize.GiB, 1024),

    (Bytes(1536, ByteSize.KiB), ByteSize.GiB, 1.5),
    (Bytes(-1.5, ByteSize.GiB), ByteSize.KiB, -1536),

    (Bytes(2, ByteSize.MiB), ByteSize.B, 2097152),
    (Bytes(-2, ByteSize.GiB), ByteSize.B, -2147483648),
])
def test_convert_to(value: Bytes, unit: ByteSize, expected: int) -> None:
    pytest.approx(value.convert_to(unit), expected)


@pytest.mark.parametrize('value, expected', [
    (Bytes(1), '1 B'),
    (Bytes(1024), '1.00 KiB'),
    (Bytes(1024, ByteSize.KiB), '1.00 MiB'),
    (Bytes(1024, ByteSize.MiB), '1.00 GiB'),
    (Bytes(1024, ByteSize.GiB), '1.00 TiB'),
    (Bytes(1024, ByteSize.TiB), '1024.00 TiB'),

    (Bytes(1.5), '2 B'),
    (Bytes(1536), '1.50 KiB'),
    (Bytes(1536, ByteSize.KiB), '1.50 MiB'),
    (Bytes(1536, ByteSize.MiB), '1.50 GiB'),
    (Bytes(1536, ByteSize.GiB), '1.50 TiB'),
    (Bytes(1536, ByteSize.TiB), '1536.00 TiB'),

    (Bytes(-1.5), '-2 B'),
    (Bytes(-1536), '-1.50 KiB'),
    (Bytes(-1536, ByteSize.KiB), '-1.50 MiB'),
    (Bytes(-1536, ByteSize.MiB), '-1.50 GiB'),
    (Bytes(-1536, ByteSize.GiB), '-1.50 TiB'),
    (Bytes(-1536, ByteSize.TiB), '-1536.00 TiB')
])
def test_to_str(value: Bytes, expected: str) -> None:
    assert str(value) == expected


def test_repr() -> None:
    with patch.object(Bytes, '__str__', return_value='test') as mock:
        assert repr(Bytes(1)) == "Bytes(test)"
        mock.assert_called_once_with()
