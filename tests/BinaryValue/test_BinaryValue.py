""" This module tests the BinaryValue class """

import pytest

from src.framework.binary_value import BinaryValue


class TestConversions:
    """ Tests the conversion of values with different representation to binary values """

    conversion_values = [(1, "1"), (2, "10"), (15, "1111"), (65535, "1111111111111111"),  # integer values
                         ("23", "10111"), ("002048", "100000000000"),  # decimal values (string)
                         ("0b1010", "1010"), ("0b00001111", "1111"),  # binary values
                         ("0o742", "111100010"), ("0o00111", "1001001"),  # octal values
                         ("0xFA", "11111010"), ("0xbc", "10111100")]  # hexadecimal values (lower and upper case)
    conversion_errors = [(-1, ValueError, "negative numbers cannot be converted to binary values"),
                         ("-1", ValueError, "negative numbers cannot be converted to binary values"),
                         ("12.3", ValueError, "invalid literal for int() with base 10: '12.3'"),
                         ("12a", ValueError, "invalid literal for int() with base 10: '12a'"),
                         ("0b002", ValueError, "illegal binary value: '0b002'"),
                         ("0o187", ValueError, "illegal octal value: '0o187'"),
                         ("0x1q", ValueError, "illegal hexadecimal value: '0x1q'"),
                         (None, TypeError, "int() argument must be a string, a bytes-like object or a number, not"
                                           " 'NoneType'")]

    @pytest.mark.parametrize("value, expected", conversion_values)
    def test_conversions_to_binary_value(self, value, expected):
        """ Convert a value to its binary representation """

        error = "{} -> {} (expected {})".format(value, BinaryValue.bin(value), expected)
        assert BinaryValue.bin(value) == expected, error

    @pytest.mark.parametrize("value, exception, message", conversion_errors)
    def test_conversions_to_binary_value_error(self, value, exception, message):
        try:
            BinaryValue.bin(value)
            assert False, "no exception was raised (expected " + exception + ")"
        except exception as e:
            assert str(e) == message
        except Exception as e:
            error = "unexpected exception ({}): {}".format(type(e).__name__, str(e))
            assert False, error


class TestComparison:
    """ Tests the the comparison logic of binary values """

    comparison_values = [(1, 1), (1, 0), (0, 1), ("1", "1"), ("1", "0"), ("0", "1"), ("001", "1"), ("1", "000"),
                         (10, "0b10"), (10, "0o10"), (10, "10"), (10, "0x10"), (1, "0b1"), (1, "0b0001"),
                         ("0x002", "0b10"), ("0o123", "0x23"), ("0x0F0f", "0b0000111100001111")]

    @pytest.mark.parametrize("value, comparand", comparison_values)
    def test_comparison(self, value, comparand):

        base_map = {"0b": 2, "0o": 8, "0x": 16}

        def convert_to_int(item):
            try:
                base = base_map.get(item[0:2], 10)
                return int(item, base)
            except TypeError:
                return item

        int_v, int_c = convert_to_int(value), convert_to_int(comparand)

        error = "mismatch in '{} < {}'".format(value, comparand)
        assert BinaryValue.less_than(value, comparand) == (int_v < int_c), error

        error = "mismatch in '{} <= {}'".format(value, comparand)
        assert BinaryValue.less_than_or_equal(value, comparand) == (int_v <= int_c), error

        error = "mismatch in '{} == {}'".format(value, comparand)
        assert BinaryValue.equal(value, comparand) == (int_v == int_c), error

        error = "mismatch in '{} != {}'".format(value, comparand)
        assert BinaryValue.not_equal(value, comparand) == (int_v != int_c), error

        error = "mismatch in '{} > {}'".format(value, comparand)
        assert BinaryValue.greater_than(value, comparand) == (int_v > int_c), error

        error = "mismatch in '{} >= {}'".format(value, comparand)
        assert BinaryValue.greater_than_or_equal(value, comparand) == (int_v >= int_c), error


class TestArithmeticOperations:
    """ Tests the the arithmetic operations of binary values """

    @pytest.mark.parametrize("augend, addend", [(1, 1), (7, 5), (4, 0)])
    def test_addition(self, augend, addend):
        result = int(BinaryValue.add(augend, addend), 2)
        assert result == augend + addend, "{} + {} != {}".format(augend, addend, result)

    @pytest.mark.parametrize("minuend, subtrahend", [(1, 1), (7, 5), (4, 0)])
    def test_subtraction(self, minuend, subtrahend):
        result = int(BinaryValue.sub(minuend, subtrahend), 2)
        assert result == minuend - subtrahend, "{} - {} != {}".format(minuend, subtrahend, result)

    @pytest.mark.parametrize("minuend, subtrahend", [(0, 1)])
    def test_subtraction_error(self, minuend, subtrahend):
        try:
            BinaryValue.sub(minuend, subtrahend)
            assert False, "no exception was raised (expected ValueError)"
        except ValueError as e:
            assert str(e) == "can't subtract '" + str(subtrahend) + "' from '" + str(minuend) + "'"
        except Exception as e:
            error = "unexpected exception ({}): {}".format(type(e).__name__, str(e))
            assert False, error

    @pytest.mark.parametrize("multiplicand, multiplier", [(1, 1), (7, 5), (4, 0)])
    def test_multiplication(self, multiplicand, multiplier):
        result = int(BinaryValue.mul(multiplicand, multiplier), 2)
        assert result == multiplicand * multiplier, "{} * {} != {}".format(multiplicand, multiplier, result)

    @pytest.mark.parametrize("numerator, denominator", [(1, 1), (7, 5), (0, 4)])
    def test_division(self, numerator, denominator):
        result = int(BinaryValue.mod(numerator, denominator), 2)
        assert result == numerator % denominator, "{} % {} != {}".format(numerator, denominator, result)

        result = int(BinaryValue.div(numerator, denominator), 2)
        assert result == numerator // denominator, "{} / {} != {}".format(numerator, denominator, result)

    @pytest.mark.parametrize("numerator, denominator", [(1, 0)])
    def test_division_error(self, numerator, denominator):
        try:
            BinaryValue.mod(numerator, denominator)
            assert False, "no exception was raised (expected ZeroDivisionError)"
        except ZeroDivisionError as e:
            assert str(e) == ""
        except Exception as e:
            error = "unexpected exception ({}): {}".format(type(e).__name__, str(e))
            assert False, error

        try:
            BinaryValue.div(numerator, denominator)
            assert False, "no exception was raised (expected ZeroDivisionError)"
        except ZeroDivisionError as e:
            assert str(e) == ""
        except Exception as e:
            error = "unexpected exception ({}): {}".format(type(e).__name__, str(e))
            assert False, error

    @pytest.mark.parametrize("base, exponent", [(1, 1), (2, 5), (5, 3), (4, 0)])
    def test_addition(self, base, exponent):
        result = int(BinaryValue.pow(base, exponent), 2)
        assert result == base**exponent, "{}**{} != {}".format(base, exponent, result)


class TestBitwiseOperations:
    """ Tests the the bitwise operations of binary values """

    @pytest.mark.parametrize("value, expected", [(1, "0"), (7, "000"), (4, "011"), ("0xA", "0101")])
    def test_invert(self, value, expected):
        result = BinaryValue.invert(value)
        assert result == expected, "~{} != {} (expected '{}')".format(value, result, expected)

    @pytest.mark.parametrize("value1, value2, expected", [(1, 1, "1"), (7, "000", "000"), (4, 5, "100"),
                                                          ("0xA", "0b0101", "0000"), (1, "0xF", "0001")])
    def test_bitwise_and(self, value1, value2, expected):
        result = BinaryValue.bitwise_and(value1, value2)
        assert result == expected, "{} & {} != {} (expected '{}')".format(value1, value2, result, expected)

    @pytest.mark.parametrize("value1, value2, expected", [(1, 1, "1"), (7, "000", "111"), (4, 5, "101"),
                                                          ("0xA", "0b0101", "1111"), (1, "0xF", "1111")])
    def test_bitwise_or(self, value1, value2, expected):
        result = BinaryValue.bitwise_or(value1, value2)
        assert result == expected, "{} | {} != {} (expected '{}')".format(value1, value2, result, expected)

    @pytest.mark.parametrize("value1, value2, expected", [(1, 1, "0"), (7, "000", "111"), (4, 5, "001"),
                                                          ("0xA", "0b0101", "1111"), (1, "0xF", "1110")])
    def test_bitwise_xor(self, value1, value2, expected):
        result = BinaryValue.bitwise_xor(value1, value2)
        assert result == expected, "{} ^ {} != {} (expected '{}')".format(value1, value2, result, expected)
