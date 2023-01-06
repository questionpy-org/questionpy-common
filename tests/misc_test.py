from unittest.mock import patch

import pytest

from questionpy_common.misc import Size, SizeUnit


KB = 1024
MB = 1024**2
GB = 1024**3
TB = 1024**4


@pytest.mark.parametrize('byte_size, expected', [
    (SizeUnit.B, 1),
    (SizeUnit.KiB, KB),
    (SizeUnit.MiB, MB),
    (SizeUnit.GiB, GB),
    (SizeUnit.TiB, TB),
])
def test_byte_size(byte_size: SizeUnit, expected: int) -> None:
    assert byte_size == expected


@pytest.mark.parametrize('value, unit, expected', [
    # Integers.
    (1, SizeUnit.B, 1),
    (1024, SizeUnit.B, KB),
    (1, SizeUnit.KiB, KB),
    (1, SizeUnit.MiB, MB),
    (1, SizeUnit.GiB, GB),
    (1, SizeUnit.TiB, TB),
    (-1, SizeUnit.KiB, -KB),

    # Floats.
    (0.4, SizeUnit.B, 0),
    (0.6, SizeUnit.B, 1),
    (1.0, SizeUnit.B, 1),
    (0.5, SizeUnit.KiB, 512),

    (-0.4, SizeUnit.B, 0),
    (-0.6, SizeUnit.B, -1),
    (-0.5, SizeUnit.KiB, -512),

    # Strings.
    ('0.4', SizeUnit.B, 0),
    ('0.6', SizeUnit.B, 1),
    ('1.5', SizeUnit.KiB, 1536),
    ('1', SizeUnit.MiB, MB),
    ('1', SizeUnit.GiB, GB),
    ('1', SizeUnit.TiB, TB),

    ('+0.4', SizeUnit.B, 0),
    ('+0.6', SizeUnit.B, 1),
    ('+1.5', SizeUnit.KiB, 1536),
    ('+1', SizeUnit.MiB, MB),
    ('+1', SizeUnit.GiB, GB),
    ('+1', SizeUnit.TiB, TB),

    ('-0.4', SizeUnit.B, 0),
    ('-0.6', SizeUnit.B, -1),
    ('-1.5', SizeUnit.KiB, -1536),
    ('-1', SizeUnit.MiB, -MB),
    ('-1', SizeUnit.GiB, -GB),
    ('-1', SizeUnit.TiB, -TB),
])
def test_init(value: float, unit: SizeUnit, expected: int) -> None:
    assert Size(value, unit) == expected


@pytest.mark.parametrize('value', [
    Size(0),
    Size(-0),
    Size(+0),
    Size(0.0),
    Size(-0.0),
    Size(+0.0),
    Size('0'),
    Size('-0'),
    Size('+0'),
    Size('0.0'),
    Size('-0.0'),
    Size('+0.0')
])
def test_zero(value: Size) -> None:
    assert 0 == value


def test_incorrect_type() -> None:
    with pytest.raises(TypeError):
        Size([])  # type: ignore


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
        Size(value)


@pytest.mark.parametrize('string, expected', [
    # Without unit.
    ('0', 0),
    ('1', 1),
    ('1.0', 1),
    ('1.4', 1),
    ('1.6', 2),
    ('1024', KB),
    ('1024.0', KB),
    ('1024.5', KB),
    ('1024.6', KB + 1),

    # With unit.
    ('1 b', 1),
    ('1 B', 1),
    ('1k', KB),
    ('1kb', KB),
    ('1KB', KB),
    ('1kib', KB),
    ('1 m', MB),
    ('1 mb', MB),
    ('1 MB', MB),
    ('1 mib', MB),
    ('1 G', GB),
    ('1 Gb', GB),
    ('1 gB', GB),
    ('1 giB', GB),
    ('1 T  ', TB),
    ('  1 tib', TB),
    ('  1 TiB  ', TB),
])
def test_from_string(string: str, expected: int) -> None:
    assert Size.from_string(string) == expected


@pytest.mark.parametrize('string', [
    '1.0.0',
    'KiB',
    '1 KiB KiB',
    '1 5',
    '1 5 MiB',
])
def test_from_string_not_valid(string: str) -> None:
    with pytest.raises(ValueError):
        Size.from_string(string)


@pytest.mark.parametrize('value, unit, expected', [
    (Size(1), SizeUnit.B, 1),
    (Size(0), SizeUnit.B, 0),
    (Size(-1), SizeUnit.B, -1),

    (Size(KB), SizeUnit.KiB, 1),
    (Size(1, SizeUnit.KiB), SizeUnit.B, KB),

    (Size(KB, SizeUnit.MiB), SizeUnit.GiB, 1),
    (Size(1, SizeUnit.GiB), SizeUnit.MiB, KB),

    (Size(KB, SizeUnit.MiB), SizeUnit.GiB, 1),
    (Size(1, SizeUnit.GiB), SizeUnit.MiB, KB),

    (Size(KB, SizeUnit.GiB), SizeUnit.TiB, 1),
    (Size(1, SizeUnit.TiB), SizeUnit.GiB, KB),

    (Size(KB, SizeUnit.TiB), SizeUnit.GiB, KB),

    (Size(1536, SizeUnit.KiB), SizeUnit.GiB, 1.5),
    (Size(-1.5, SizeUnit.GiB), SizeUnit.KiB, -1536),

    (Size(2, SizeUnit.MiB), SizeUnit.B, 2 * MB),
    (Size(-2, SizeUnit.GiB), SizeUnit.B, -2 * MB),
])
def test_convert_to(value: Size, unit: SizeUnit, expected: int) -> None:
    pytest.approx(value.convert_to(unit), expected)


@pytest.mark.parametrize('value, expected', [
    (Size(1), '1 B'),
    (Size(KB), '1.00 KiB'),
    (Size(KB, SizeUnit.KiB), '1.00 MiB'),
    (Size(KB, SizeUnit.MiB), '1.00 GiB'),
    (Size(KB, SizeUnit.GiB), '1.00 TiB'),
    (Size(KB, SizeUnit.TiB), '1024.00 TiB'),

    (Size(1.5), '2 B'),
    (Size(1536), '1.50 KiB'),
    (Size(1536, SizeUnit.KiB), '1.50 MiB'),
    (Size(1536, SizeUnit.MiB), '1.50 GiB'),
    (Size(1536, SizeUnit.GiB), '1.50 TiB'),
    (Size(1536, SizeUnit.TiB), '1536.00 TiB'),

    (Size(-1.5), '-2 B'),
    (Size(-1536), '-1.50 KiB'),
    (Size(-1536, SizeUnit.KiB), '-1.50 MiB'),
    (Size(-1536, SizeUnit.MiB), '-1.50 GiB'),
    (Size(-1536, SizeUnit.GiB), '-1.50 TiB'),
    (Size(-1536, SizeUnit.TiB), '-1536.00 TiB')
])
def test_to_str(value: Size, expected: str) -> None:
    assert str(value) == expected


def test_repr() -> None:
    with patch.object(Size, '__str__', return_value='test') as mock:
        assert repr(Size(1)) == 'Size(test)'
        mock.assert_called_once_with()
