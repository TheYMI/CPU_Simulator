""" This module tests the BitValue class """

import pytest

from src.framework.bit_value import BitValue


@pytest.mark.BitValue
class TestConstructor:
    """ This class tests the constructor of a BitValue object """

    constructor_params = [(0, 4, "0000"), (5, 4, "0101"), (-1, 4, "1111"), (-7, 4, "1001"),  # int
                          ("0", 4, "0000"), ("5", 4, "0101"), ("-1", 4, "1111"), ("-7", 4, "1001"),  # str
                          ("0b011", 4, "0011"), ("0o5", 4, "1101"), ("0xAb", 8, "10101011"),  # different bases
                          (0, 16, "0000000000000000"), ("0xF0F", 16, "1111111100001111"),  # padding
                          (-7, 16, "1111111111111001"), ("-2", 8, "11111110"),  # padding negative
                          (65536, 16, "0000000000000000"), ("0xF0F", 8, "00001111"),  # truncating
                          (BitValue(7, 4), 12, "000000000111"), (BitValue("0xAA", 16), 4, "1010")]  # BitValue

    def test_default_constructor(self):
        bv = BitValue()
        assert bv.value == "0" * 32, "the default value should be '" + ("0" * 32) + "'"
        assert bv.bits == 32, "the default number of bits should be 32"

    @pytest.mark.parametrize("value, bits, expected", constructor_params)
    def test_constructor(self, value, bits, expected):
        bv = BitValue(value, bits)
        assert bv.value == expected, "the value should be '{}'".format(expected)
        assert bv.bits == bits, "the number of bits should be {}".format(bits)

    unsigned_params = [("0b11", 4, "0011"), ("0o5", 4, "0101"), ("0xF0F", 16, "0000111100001111")]

    @pytest.mark.parametrize("value, bits, expected", unsigned_params)
    def test_unsigned_constructor(self, value, bits, expected):
        bv = BitValue(value, bits, signed=False)
        assert bv.value == expected, "the value should be '{}'".format(expected)
        assert bv.bits == bits, "the number of bits should be {}".format(bits)

    bit_count_errors = [(None, TypeError, "number of bits for a value must be an integer"),
                        (-1, ValueError, "number of bits for a value must be positive")]

    @pytest.mark.parametrize("bits, exception, message", bit_count_errors)
    def test_bit_count_error(self, bits, exception, message):
        """ Create an object with the given bit count and check that an exception is raised """
        try:
            BitValue(bits=bits)
        except exception as e:
            assert str(e) == message
        except Exception as e:
            error = "unexpected exception ({}): {}".format(type(e).__name__, str(e))
            raise AssertionError(error)
        else:
            error = "no exception was raised (expected {})".format(exception.__name__)
            raise AssertionError(error)

    value_errors = [("12.3", ValueError, "invalid literal for int() with base 10: '12.3'"),
                    ("12a", ValueError, "invalid literal for int() with base 10: '12a'"),
                    ("0b002", ValueError, "illegal binary value: '0b002'"),
                    ("0o187", ValueError, "illegal octal value: '0o187'"),
                    ("0x1q", ValueError, "illegal hexadecimal value: '0x1q'"),
                    (True, TypeError, "illegal type for binary value: bool")]

    @pytest.mark.parametrize("value, exception, message", value_errors)
    def test_value_errors(self, value, exception, message):
        try:
            BitValue(value)
        except exception as e:
            assert str(e) == message
        except Exception as e:
            error = "unexpected exception ({}): {}".format(type(e).__name__, str(e))
            assert False, error
        else:
            error = "no exception was raised (expected {})".format(exception.__name__)
            raise AssertionError(error)


@pytest.mark.BitValue
class TestValueSetting:
    """ This class tests the behavior of setting the value of a BitValue object """

    values = [(10, "00001010"), (-3, "11111101"), ("7", "00000111"), ("-5", "11111011"),  # int/str (+padding)
              ("0b0010", "00000010"), ("0o54", "11101100"), ("0xBc", "10111100"),  # other bases
              ("0o742", "11100010"), ("0x5A5", "10100101"), (256, "00000000"), ("257", "00000001"),  # truncating
              (BitValue(7, 4), "00000111"), (BitValue("0xFAFA", 16), "11111010")]  # BitValue

    @pytest.mark.parametrize("value, expected", values)
    def test_set_value(self, value, expected):
        bv = BitValue(bits=8)
        bv.value = value
        assert bv.value == expected, "the value should have been '{}', not '{}'".format(expected, bv.value)

    unsigned_values = [("0o54", "00101100"), ("0xF", "00001111")]

    @pytest.mark.parametrize("value, expected", unsigned_values)
    def test_set_unsigned_value(self, value, expected):
        bv = BitValue(bits=8, signed=False)
        bv.value = value
        assert bv.value == expected, "the value should have been '{}', not '{}'".format(expected, bv.value)

    error_values = [(True, "illegal type for binary value: bool"), ([], "illegal type for binary value: list")]

    @pytest.mark.parametrize("value, message", error_values)
    def test_set_value_error(self, value, message):
        try:
            bv = BitValue(bits=8)
            bv.value = value
        except TypeError as e:
            assert str(e) == message
        except Exception as e:
            error = "unexpected exception ({}): {}".format(type(e).__name__, str(e))
            raise AssertionError(error)
        else:
            raise AssertionError("no exception was raised (expected TypeError)")


@pytest.mark.BitValue
class TestSlicing:
    """ This class tests the behavior of slicing on a BitValue object """

    def test_single_index(self):
        bv = BitValue("0x9B5F", 16)

        # The indexing is inverted because it indicates the power of 2 represented by the bit
        for i in range(len(bv)):
            assert bv[i] == bv.value[-(i+1)], "the bit at index {} is {}, not {}".format(i, bv.value[-(i+1)], bv[i])

    def test_empty_slice(self):
        bv = BitValue("0x9B5F", bits=16)
        assert bv[:] == "1001101101011111", "the slice should have been '1001101101011111', not '{}'".format(bv[:])

    def test_slice_from_start(self):
        bv = BitValue("0x9B5F", bits=16)

        # The indexing is inverted because it indicates the power of 2 represented by the bit
        for i in range(1, len(bv) + 1):
            error = "the slice at [:{}] is {}, not {}".format(i, bv.value[-i:], bv[:i])
            assert bv[:i] == bv.value[-i:], error

        for i in range(-1, -len(bv), -1):
            error = "the slice at [:{}] is {}, not {}".format(i, bv.value[-i:], bv[:i])
            assert bv[:i] == bv.value[-i:], error

    def test_slice_until_end_values(self):
        bv = BitValue("0x9B5F", bits=16)

        # The indexing is inverted because it indicates the power of 2 represented by the bit
        # Test [0:] separately, because the [:-i] doesn't work with -0
        assert bv[0:] == "1001101101011111", "the slice should have been '1001101101011111', not '{}'".format(bv[:])

        for i in range(1, len(bv)):
            error = "the slice at [{}:] is {}, not {}".format(i, bv.value[:-i], bv[i:])
            assert bv[i:] == bv.value[:-i], error

        for i in range(-1, -len(bv), -1):
            error = "the slice at [{}:] is {}, not {}".format(i, bv.value[:-i], bv[i:])
            assert bv[i:] == bv.value[:-i], error

    @pytest.mark.parametrize("start, end, expected", [(3, 10, "1011001"), (0, 8, "11001110"), (-8, -3, "00010")])
    def test_slice(self, start, end, expected):
        bv = BitValue("0x02468ACE", bits=32)
        assert bv[start:end] == expected, "the slice should have been '{}', not '{}'".format(expected, bv[start:end])

    slice_errors = [(slice(2, 6, 2), ValueError, "'BitValue' object does not support steps in slicing"),
                    (slice(2, 6, -1), ValueError, "'BitValue' object does not support steps in slicing"),
                    (18, IndexError, "bit index out of range"), (-20, IndexError, "bit index out of range")]

    @pytest.mark.parametrize("key, exception, message", slice_errors)
    def test_key_error(self, key, exception, message):
        try:
            BitValue("0x9B5F", bits=16)[key]
        except exception as e:
            assert str(e) == message
        except Exception as e:
            error = "unexpected exception ({}): {}".format(type(e).__name__, str(e))
            raise AssertionError(error)
        else:
            error = "no exception was raised (expected {})".format(exception.__name__)
            raise AssertionError(error)


@pytest.mark.BitValue
class TestComparison:
    """ Tests the the comparison logic of BitValue objects """

    comparison_values = [(1, 1), (1, 0), (0, 1), ("1", "1"), ("1", "0"), ("0", "1"), ("001", "1"), ("1", "000"),
                         (10, "0b010"), (10, "0o010"), (10, "10"), (10, "0x010"), (1, "0b01"), (1, "0b0001"),
                         ("0x002", "0b010"), ("0o0123", "0x023"), ("0x0F0f", "0b0000111100001111"),
                         (-1, 0), (0, -1), (-3, -5), (1, BitValue()), (0, BitValue(-1)), ("0x00F", BitValue("0xFF"))]

    @pytest.mark.parametrize("value, other", comparison_values)
    def test_comparison(self, value, other):

        base_map = {"0b": 2, "0o": 8, "0x": 16}

        def convert_to_int(item):
            try:
                base = base_map.get(item[0:2], 10)
                return int(item, base)
            except TypeError:
                return int(item)

        int_v, int_c = convert_to_int(value), convert_to_int(other)
        bv = BitValue(value)

        error = "mismatch in '{} < {}'".format(value, other)
        assert (bv < other) == (int_v < int_c), error

        error = "mismatch in '{} <= {}'".format(value, other)
        assert (bv <= other) == (int_v <= int_c), error

        error = "mismatch in '{} == {}'".format(value, other)
        assert (bv == other) == (int_v == int_c), error

        error = "mismatch in '{} != {}'".format(value, other)
        assert (bv != other) == (int_v != int_c), error

        error = "mismatch in '{} > {}'".format(value, other)
        assert (bv > other) == (int_v > int_c), error

        error = "mismatch in '{} >= {}'".format(value, other)
        assert (bv >= other) == (int_v >= int_c), error


@pytest.mark.BitValue
class TestArithmeticOperations:
    """ Tests the the arithmetic operations of binary values """

    @pytest.mark.parametrize("value, absolute", [(4, 4), (0, 0), (-3, 3)])
    def test_absolute(self, value, absolute):
        result = int(abs(BitValue(value)))
        assert result == absolute, "abs({}) != {}".format(value, result)

    @pytest.mark.parametrize("value, negative", [(4, -4), (0, 0), (-3, 3)])
    def test_negative(self, value, negative):
        result = int(-BitValue(value))
        assert result == negative, "-({}) != {}".format(value, result)

    @pytest.mark.parametrize("value, positive", [(4, 4), ("0o02", 2)])
    def test_positive(self, value, positive):
        result = int(+BitValue(value))
        assert result == positive, "+({}) != {}".format(value, result)

    add_sub_values = [(1, 1), (7, 5), (4, 0), (3, -2), (1, -2), (-1, 1), (-2, 3), (-2, -1)]

    @pytest.mark.parametrize("value, other", add_sub_values)
    def test_addition(self, value, other):
        result = int(BitValue(value) + other)
        assert result == value + other, "{} + {} != {}".format(value, other, result)

    @pytest.mark.parametrize("value, other", add_sub_values)
    def test_in_place_addition(self, value, other):
        bv = BitValue(value)
        bv += other
        assert int(bv) == value + other, "{} += {} != {}".format(value, other, int(bv))

    @pytest.mark.parametrize("value, other", add_sub_values)
    def test_subtraction(self, value, other):
        result = int(BitValue(value) - other)
        assert result == value - other, "{} - {} != {}".format(value, other, result)

    @pytest.mark.parametrize("value, other", add_sub_values)
    def test_in_place_subtraction(self, value, other):
        bv = BitValue(value)
        bv -= other
        assert int(bv) == value - other, "{} -= {} != {}".format(value, other, int(bv))

    multiplication_values = [(1, 1), (7, 5), (4, 0), (2, -3), (-2, 3), (-2, -2)]

    @pytest.mark.parametrize("value, other", multiplication_values)
    def test_multiplication(self, value, other):
        result = int(BitValue(value) * other)
        assert result == value * other, "{} * {} != {}".format(value, other, result)

    @pytest.mark.parametrize("value, other", multiplication_values)
    def test_in_place_multiplication(self, value, other):
        bv = BitValue(value)
        bv *= other
        assert int(bv) == value * other, "{} *= {} != {}".format(value, other, int(bv))

    division_values = [(1, 1), (7, 5), (0, 4)]

    @pytest.mark.parametrize("value, other", division_values)
    def test_division(self, value, other):
        result = int(BitValue(value) % other)
        assert result == value % other, "{} % {} != {}".format(value, other, result)

        result = int(BitValue(value) // other)
        assert result == value // other, "{} // {} != {}".format(value, other, result)

    @pytest.mark.parametrize("value, other", division_values)
    def test_in_place_division(self, value, other):
        bv = BitValue(value)
        bv %= other
        assert int(bv) == value % other, "{} %= {} != {}".format(value, other, int(bv))

        bv = BitValue(value)
        bv //= other
        assert int(bv) == value // other, "{} //= {} != {}".format(value, other, int(bv))

    def test_division_error(self):
        try:
            BitValue(1) % 0
        except ZeroDivisionError as e:
            assert str(e) == ""
        except Exception as e:
            error = "unexpected exception ({}): {}".format(type(e).__name__, str(e))
            raise AssertionError(error)
        else:
            raise AssertionError("no exception was raised (expected ZeroDivisionError)")

        try:
            BitValue(1) // 0
        except ZeroDivisionError as e:
            assert str(e) == ""
        except Exception as e:
            error = "unexpected exception ({}): {}".format(type(e).__name__, str(e))
            raise AssertionError(error)
        else:
            raise AssertionError("no exception was raised (expected ZeroDivisionError)")

    power_values = [(1, 1), (2, 5), (5, 3), (4, 0)]

    @pytest.mark.parametrize("value, other", power_values)
    def test_power(self, value, other):
        result = int(BitValue(value)**other)
        assert result == value**other, "{}**{} != {}".format(value, other, result)

    @pytest.mark.parametrize("value, other", [(1, 1), (2, 5), (5, 3), (4, 0)])
    def test_in_place_power(self, value, other):
        bv = BitValue(value)
        bv **= other
        assert int(bv) == value**other, "{} **= {} != {}".format(value, other, int(bv))


@pytest.mark.BitValue
class TestBitwiseOperations:
    """ Tests the the bitwise operations of binary values """

    inversion_values = [("0xAA", "01010101"), ("0x0F", "11110000"), ("0x99", "01100110")]

    @pytest.mark.parametrize("value, expected", inversion_values)
    def test_inversion(self, value, expected):
        result = ~BitValue(value, 8, signed=False)
        assert result.value == expected, "~({}) != {}".format(value, result.value)

    @pytest.mark.parametrize("value, expected", inversion_values)
    def test_in_place_inversion(self, value, expected):
        bv = BitValue(value, 8)
        bv.invert()
        assert bv.value == expected, "~({}) != {}".format(value, bv.value)

    bitwise_values = [("0xAA", "0x00"), ("0xAA", "0xFF"), ("0x0F", "0xF0"), ("0xAA", "0x55")]

    and_expected = ["00000000", "10101010", "00000000", "00000000"]

    @pytest.mark.parametrize("values, expected", zip(bitwise_values, and_expected))
    def test_and(self, values, expected):
        value, other = values
        result = BitValue(value, 8) & other
        assert result.value == expected, "{} & {} != {}".format(value, other, result)

    @pytest.mark.parametrize("values, expected", zip(bitwise_values, and_expected))
    def test_in_place_and(self, values, expected):
        value, other = values
        bv = BitValue(value, 8)
        bv &= other
        assert bv.value == expected, "{} &= {} != {}".format(value, other, bv.value)

    or_expected = ["10101010", "11111111", "11111111", "11111111"]

    @pytest.mark.parametrize("values, expected", zip(bitwise_values, or_expected))
    def test_or(self, values, expected):
        value, other = values
        result = BitValue(value, 8) | other
        assert result.value == expected, "{} | {} != {}".format(value, other, result)

    @pytest.mark.parametrize("values, expected", zip(bitwise_values, or_expected))
    def test_in_place_or(self, values, expected):
        value, other = values
        bv = BitValue(value, 8)
        bv |= other
        assert bv.value == expected, "{} |= {} != {}".format(value, other, bv.value)

    xor_expected = ["10101010", "01010101", "11111111", "11111111"]

    @pytest.mark.parametrize("values, expected", zip(bitwise_values, xor_expected))
    def test_xor(self, values, expected):
        value, other = values
        result = BitValue(value, 8) ^ other
        assert result.value == expected, "{} ^ {} != {}".format(value, other, result)

    @pytest.mark.parametrize("values, expected", zip(bitwise_values, xor_expected))
    def test_in_place_xor(self, values, expected):
        value, other = values
        bv = BitValue(value, 8)
        bv ^= other
        assert bv.value == expected, "{} ^= {} != {}".format(value, other, bv.value)

    shift_values = ["0x00", "0xFF", "0xAA", "0x55"]

    @pytest.mark.parametrize("value", shift_values)
    def test_left_shift(self, value):
        bv = BitValue(value, 8)
        for i in range(1, 9):
            expected = bv.value[i:] + ("0" * i)
            assert (bv << i).value == expected, "{} << {} != {}".format(value, i, expected)

    @pytest.mark.parametrize("value", shift_values)
    def test_in_place_left_shift(self, value):
        for i in range(1, 9):
            bv = BitValue(value, 8)
            expected = bv.value[i:] + ("0" * i)
            bv <<= i
            assert bv.value == expected, "{} <<= {} != {}".format(value, i, expected)

    @pytest.mark.parametrize("value", shift_values)
    def test_right_shift(self, value):
        bv = BitValue(value, 8)
        for i in range(1, 9):
            expected = ("0" * i) + bv.value[:-i]
            assert (bv >> i).value == expected, "{} >> {} != {}".format(value, i, expected)

    @pytest.mark.parametrize("value", shift_values)
    def test_in_place_right_shift(self, value):
        for i in range(1, 9):
            bv = BitValue(value, 8)
            expected = ("0" * i) + bv.value[:-i]
            bv >>= i
            assert bv.value == expected, "{} >>= {} != {}".format(value, i, expected)


@pytest.mark.BitValue
class TestConversions:
    """ Tests the the conversion of binary values into other types and bases """

    conversion_values = [0, 5, -2]

    expected_bool = [False, True, True]

    @pytest.mark.parametrize("value, expected", zip(conversion_values, expected_bool))
    def test_bool_conversion(self, value, expected):
        bv = BitValue(value, 8)
        assert bool(bv) == expected, "{} != {}".format(bool(bv), expected)

    expected_int = [0, 5, -2]

    @pytest.mark.parametrize("value, expected", zip(conversion_values, expected_int))
    def test_int_conversion(self, value, expected):
        bv = BitValue(value, 8)
        assert int(bv) == expected, "{} != {}".format(int(bv), expected)

    expected_str = ["0b00000000", "0b00000101", "0b11111110"]

    @pytest.mark.parametrize("value, expected", zip(conversion_values, expected_str))
    def test_str_conversion(self, value, expected):
        bv = BitValue(value, 8)
        assert str(bv) == expected, "{} != {}".format(str(bv), expected)

    expected_bin = ["0b00000000", "0b00000101", "0b11111110"]

    @pytest.mark.parametrize("value, expected", zip(conversion_values, expected_bin))
    def test_bin_conversion(self, value, expected):
        bv = BitValue(value, 8)
        assert bv.bin() == expected, "{} != {}".format(bv.bin(), expected)

    expected_oct = ["0o000", "0o005", "0o376"]

    @pytest.mark.parametrize("value, expected", zip(conversion_values, expected_oct))
    def test_oct_conversion(self, value, expected):
        bv = BitValue(value, 8)
        assert bv.oct() == expected, "{} != {}".format(bv.oct(), expected)

    expected_dec = ["0", "5", "-2"]

    @pytest.mark.parametrize("value, expected", zip(conversion_values, expected_dec))
    def test_dec_conversion(self, value, expected):
        bv = BitValue(value, 8)
        assert bv.dec() == expected, "{} != {}".format(bv.dec(), expected)

    expected_hex = ["0x00", "0x05", "0xFE"]

    @pytest.mark.parametrize("value, expected", zip(conversion_values, expected_hex))
    def test_hex_conversion(self, value, expected):
        bv = BitValue(value, 8)
        assert bv.hex() == expected, "{} != {}".format(bv.hex(), expected)
