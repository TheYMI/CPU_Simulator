"""
Created By: Yuval Tzur
Date: 1/1/19
Description: The bit_value module handles all the value representations throughout the simulator.
             Values are represented using strings that consist of zeros ('0') and ones ('1') to denote the binary
             representation of the value. Strings were chosen for several reasons:
             1. Strings support slicing by default
             2. Strings are single objects, but are iterable
             3. Strings are immutable, thus can be shared by multiple objects without the risk of one object changing a
                value and affecting other objects
             4. Strings less manipulation before they can be used for output
             Tuples offer some of those advantages, but not all.

             Bit values should support a great range of operators since they can be used to mimic numbers, boolean
             values or sets of bits. Values represent binary notation, and similar to hardware notation, they're indexed
             from right to left (as opposed to programming data structures), since the index represents the power of 2 a
             bit represents. Slicing operators require some extra handling for this reason. Since some operators depend
             on the number of bits used to represent the value, a BitValue object will have a specified number of bits.
             Negative values are represented using 2's complement. Values that overflow the number of bits are
             truncated.
"""

import re


class BinaryValue:
    """ The value class allows to perform operations on a binary value.
        All operations are performed using boolean arithmetic to simulate an actual binary value.
        While conversion to integers is easier, the purpose of this project is educational.
        Negative values require a set number of bits to be identified, so they are not supported as a standalone value.
        The creation of objects from this class is not required for usability. """

    # The following conversion maps are used when handling different numerical bases:
    _oct = {"0": "000", "1": "001", "2": "010", "3": "011", "4": "100", "5": "101", "6": "110", "7": "111"}
    _hex = {"0": "0000", "1": "0001", "2": "0010", "3": "0011", "4": "0100", "5": "0101", "6": "0110", "7": "0111",
            "8": "1000", "9": "1001", "A": "1010", "B": "1011", "C": "1100", "D": "1101", "E": "1110", "F": "1111"}

    # The following maps are used for arithmetic and bitwise operations
    _add = {("0", "0", "0"): ("0", "0"), ("0", "0", "1"): ("1", "0"),  # Map:
            ("0", "1", "0"): ("1", "0"), ("0", "1", "1"): ("0", "1"),  # (b1, b2, c) -> (s, c)
            ("1", "0", "0"): ("1", "0"), ("1", "0", "1"): ("0", "1"),  # b1 and b2 are single binary digits
            ("1", "1", "0"): ("0", "1"), ("1", "1", "1"): ("1", "1")}  # s = sum of b1 and b2; c = end carry
    _inv = {"0": "1", "1": "0"}
    _and = {("0", "0"): "0", ("0", "1"): "0", ("1", "0"): "0", ("1", "1"): "1"}
    _or = {("0", "0"): "0", ("0", "1"): "1", ("1", "0"): "1", ("1", "1"): "1"}
    _xor = {("0", "0"): "0", ("0", "1"): "1", ("1", "0"): "1", ("1", "1"): "0"}

    def __init__(self):
        """ The class can be used without initializing an object """
        pass

    # Base conversions:
    @classmethod
    def _bin_to_bin(cls, value):
        """ Remove the '0b' prefix if needed and check that the value is indeed binary """
        try:
            parsed_value = re.match(r"^(0b)?(?P<value>[01]+)$", str(value))
            return parsed_value.group("value")
        except AttributeError:
            raise ValueError("illegal binary value: '" + str(value) + "'")

    @classmethod
    def _oct_to_bin(cls, value):
        """ Converts an octal value to a binary value """
        try:
            parsed_value = re.match(r"^(0o)?(?P<value>[0-7]+)$", str(value))
            value = parsed_value.group("value")
            bin_value = "".join([cls._oct[digit] for digit in value])

            return bin_value
        except AttributeError:
            raise ValueError("illegal octal value: '" + str(value) + "'")

    @classmethod
    def _int_to_bin(cls, value):
        """ Converts an integer value to a binary value """
        value = int(value)
        if value < 0:
            raise ValueError("negative numbers cannot be converted to binary values")

        bin_value = ""
        while value:
            bin_value = str(value % 2) + bin_value
            value //= 2

        return bin_value if bin_value else "0"

    @classmethod
    def _dec_to_bin(cls, value):
        """ Converts a decimal value (string) to a binary value (negative numbers are not supported) """
        try:
            parsed_value = re.match(r"^(?P<negative>-)?(?P<value>[\d]+)$", str(value))
            value = int(parsed_value.group("value"))
            if parsed_value.group("negative") is not None:
                raise ValueError("negative numbers cannot be converted to binary values")

            return cls._int_to_bin(value)
        except (AttributeError, TypeError):
            if type(value) is int:
                return cls._int_to_bin(value)
            raise ValueError("illegal decimal value: '" + str(value) + "'")

    @classmethod
    def _hex_to_bin(cls, value):
        """ Converts an hexadecimal value to a binary value """
        try:
            parsed_value = re.match(r"^(0x)?(?P<value>[\da-fA-F]+)$", str(value))
            value = parsed_value.group("value").upper()
            bin_value = "".join([cls._hex[digit] for digit in value])

            return bin_value
        except AttributeError:
            raise ValueError("illegal hexadecimal value: '" + str(value) + "'")

    @classmethod
    def bin(cls, value, strip_zeros=True):
        """ Converts the given value to a binary value """
        conversion_func = {"0b": cls._bin_to_bin,
                           "0o": cls._oct_to_bin,
                           "0x": cls._hex_to_bin}.get(str(value)[0:2], cls._int_to_bin)

        bin_value = conversion_func(value)
        if strip_zeros:
            bin_value = bin_value.lstrip("0")
        return bin_value if bin_value else "0"

    # Comparison operations:
    @classmethod
    def less_than(cls, value, comparand):
        """ Checks if the value is smaller than the comparand """

        value, comparand = cls.bin(value), cls.bin(comparand)
        len1, len2 = len(value), len(comparand)

        # The conversion to binary returns a value with all leading zeroes stripped, so a longer number is bigger
        if len1 != len2:
            return len1 < len2

        # If both numbers have the same length, do a bit-by-bit comparison
        for i in range(len1):
            if value[i] != comparand[i]:
                return value[i] < comparand[i]

        return False  # if there was no change, they're equal

    @classmethod
    def less_than_or_equal(cls, value, comparand):
        """ Checks if the value is smaller or equal to the comparand """
        return cls.equal(value, comparand) or cls.less_than(value, comparand)

    @classmethod
    def equal(cls, value, comparand):
        """ Checks whether the value is equal to the comparand """
        value, comparand = cls.bin(value), cls.bin(comparand)
        return value == comparand

    @classmethod
    def not_equal(cls, value, comparand):
        """ Checks whether the value is different than the comparand """
        return not cls.equal(value, comparand)  # if not equal, they're different

    @classmethod
    def greater_than(cls, value, comparand):
        """ Checks if the value is greater than the comparand """
        # If the value is not smaller or equal to the comparand, it's greater
        return not cls.less_than_or_equal(value, comparand)

    @classmethod
    def greater_than_or_equal(cls, value, comparand):
        """ Checks if the value is greater or equal to the comparand """
        # If the value is not smaller than the comparand, it's ether greater or equal to it
        return not cls.less_than(value, comparand)

    # Arithmetic operations:
    @classmethod
    def add(cls, augend, addend):
        """ Adds the addend to the augend """

        augend, addend = cls.bin(augend), cls.bin(addend)
        length = max(len(augend), len(addend))

        # Add leading zeroes so both numbers match in length, and reverse because addition should start from the LSB
        format_str = "{:0>" + str(length) + "}"
        augend = format_str.format(augend)[::-1]
        addend = format_str.format(addend)[::-1]

        result = ""
        carry = "0"
        for i in range(length):
            sum_, carry = cls._add[augend[i], addend[i], carry]
            result = sum_ + result

        result = (carry + result).lstrip("0")
        return result if result else "0"

    @classmethod
    def sub(cls, minuend, subtrahend):
        """ Subtracts the subtrahend from the minuend (doesn't support negative values or result) """

        if cls.less_than(minuend, subtrahend):
            raise ValueError("can't subtract '" + str(subtrahend) + "' from '" + str(minuend) + "'")
        minuend, subtrahend = cls.bin(minuend), cls.bin(subtrahend)

        # Add leading zeroes so both numbers match in length
        length = max(len(minuend), len(subtrahend))
        format_str = "{:0>" + str(length) + "}"
        minuend = format_str.format(minuend)
        subtrahend = format_str.format(subtrahend)

        # With 'length' as our number of bits, we can use 2's complement to reverse the sign of the subtrahend
        subtrahend = cls.invert("0b" + subtrahend)
        subtrahend = cls.add("0b" + subtrahend, 1)

        return cls.add("0b" + minuend, "0b" + subtrahend)[-length:]

    @classmethod
    def mul(cls, multiplicand, multiplier):
        """ Multiplies the multiplicand by the multiplier """

        multiplicand, multiplier = cls.bin(multiplicand), cls.bin(multiplier)
        multiplier = multiplier[::-1]  # start multiplying from the LSB

        result = "0"
        for i in range(len(multiplier)):
            if multiplier[i] == "1":
                result = cls.add("0b" + result, "0b" + multiplicand)
            multiplicand += "0"

        return result

    @classmethod
    def _floor_division(cls, numerator, denominator):
        """ Divides the numerator by the denominator and return both the quotient and the remainder """

        remainder, denominator = cls.bin(numerator), cls.bin(denominator)

        quotient = 0
        while cls.greater_than_or_equal("0b" + remainder, "0b" + denominator):
            quotient += 1
            remainder = cls.sub("0b" + remainder, "0b" + denominator)

        return cls.bin(quotient), remainder

    @classmethod
    def mod(cls, numerator, denominator):
        """ Gets the remainder of the division of the numerator by the denominator """
        quotient, remainder = cls._floor_division(numerator, denominator)
        return remainder

    @classmethod
    def div(cls, numerator, denominator):
        """ Divides the numerator by the denominator """
        quotient, remainder = cls._floor_division(numerator, denominator)
        return quotient

    @classmethod
    def pow(cls, base, exponent):
        """ Raises the base to the exponent power (using the exponentiation by squaring algorithm) """

        base, exponent = cls.bin(base), cls.bin(exponent)
        exponent = exponent[::-1]  # start applying the exponent from the LSB

        result = "1"
        for digit in exponent:
            if digit == "1":
                result = cls.mul("0b" + result, "0b" + base)
            base = cls.mul("0b" + base, "0b" + base)

        return result

    # Bitwise operations:
    @classmethod
    def invert(cls, value):
        """ Inverts each bit in the value (including leading zeros """
        value = cls.bin(value, strip_zeros=False)
        return "".join([cls._inv[digit] for digit in value])

    @classmethod
    def _normalize_bitwise_values(cls, value_1, value_2):
        """ Gets both values as binary values with the same length """

        value_1, value_2 = cls.bin(value_1, strip_zeros=False), cls.bin(value_2, strip_zeros=False)
        length = max(len(value_1), len(value_2))

        # Add leading zeroes so both numbers match in length
        format_str = "{:0>" + str(length) + "}"
        value_1 = format_str.format(value_1)
        value_2 = format_str.format(value_2)

        return value_1, value_2

    @classmethod
    def bitwise_and(cls, value_1, value_2):
        """ Performs an 'and' operation on each respective bits of both values  """

        value_1, value_2 = cls._normalize_bitwise_values(value_1, value_2)
        result = "".join([cls._and[value_1[i], value_2[i]] for i in range(len(value_1))])

        return result

    @classmethod
    def bitwise_or(cls, value_1, value_2):
        """ Performs an 'or' operation on each respective bits of both values  """

        value_1, value_2 = cls._normalize_bitwise_values(value_1, value_2)
        result = "".join([cls._or[value_1[i], value_2[i]] for i in range(len(value_1))])

        return result

    @classmethod
    def bitwise_xor(cls, value_1, value_2):
        """ Performs a 'xor' operation on each respective bits of both values  """

        value_1, value_2 = cls._normalize_bitwise_values(value_1, value_2)
        result = "".join([cls._xor[value_1[i], value_2[i]] for i in range(len(value_1))])

        return result

    @classmethod
    def shift_left(cls, value, places):
        """ Shifts the value to the left by adding the required number of zeros """
        value, places = cls.bin(value), cls.bin(places)
        return value + "0" * int(places, 2)

    @classmethod
    def shift_right(cls, value, places):
        """ Shifts the value to the right by removing the required number of digits """
        value, places = cls.bin(value), cls.bin(places)
        return value[:-int(places, 2)]


class BitValue:
    """ This class handles binary values, as represented by a set amount of bits, similar to how values are represented
        in hardware """

    def __init__(self, value="0b0", bits=None):
        """ Initializes a an object with the binary representation of the value, as it fits in the given amount of bits.
            If bits is 'None', the number of bits is set to the minimum amount required to fit the value.
            Once the number of bits is set during the object's initialization, it can't be changed """

        # Check for legality and set the number of bits
        if type(bits) not in [int, type(None)]:
            raise TypeError("number of bits for a value must be an integer or 'None'")
        if type(bits) is int and bits < 1:
            raise ValueError("number of bits for a value must be positive")
        self._bits = bits

        self._value = None
        self.value = value

    @property
    def bits(self):
        return self._bits

    def __len__(self):
        return self.bits

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        """ Sets the value to the binary representation of the given value that matches the required number of bits """

        try:
            int_value = int(value)
        except ValueError:
            # Find the base of the value (assume 10 by default)
            base = {"0b": 2, "0o": 8, "0x": 16}[value[0:2]]
            int_value = int(value, base)
        value, negative = abs(int_value), int_value < 0  # work with the positive value and handle the sign later

        # Use the BinaryValue class to generate a string of the binary representation of the value
        value_str = BinaryValue.bin(value)
        if not self.bits:
            # Add a leading zero to represent a positive number
            value_str = "0" + value_str
            # If 'bits' is 'None', match the count to the minimum number of bits required
            self._bits = len(value_str)
        else:
            # Add leading zeros in case that the binary representation requires less bits than the current bits in use
            format_str = "{:0>" + str(self.bits) + "}"
            value_str = format_str.format(value_str)

        # If the original value was negative, change the sign using 2's complement
        if negative:
            value_str = BinaryValue.invert("0b" + value_str)
            value_str = BinaryValue.add("0b" + value_str, 1)

        self._value = value_str[-self.bits:]

    # Slicing:
    # Slicing allows handling of subset of bits (steps different than 1 are not supported)
    # Due to the inverted indexing scheme (index 0 = MSB; index -1 = LSB), some extra manipulation is required
    def __getitem__(self, key):
        if type(key) is slice:
            # The 'indices' method returns the normalized indices, requiring only the switch from LTR to RTL indexing
            start, stop, step = key.indices(self.bits)
            if step != 1:
                raise ValueError("'BitValue' object does not support steps in slicing")
            start, stop = self.bits - stop, self.bits - start
        else:
            if key >= self.bits or key < -self.bits:
                raise IndexError("bit index out of range")
            # A positive index requires the switch from LTR to RTL indexing
            # A negative index is in the correct place, but with the opposite sign
            stop = self.bits - key if key >= 0 else abs(key)
            start, step = stop - 1, 1

        return self.value[start:stop:step]

    def _normalize_value_pair(self, other):
        """ Normalizes a value pair for binary operations  """

        other = BitValue(other).value
        length = max(len(self), len(other))

        # Add leading zeros or ones to match the length
        self_format_str = "{:" + self.value[0] + ">" + str(length) + "}"
        other_format_str = "{:" + other[0] + ">" + str(length) + "}"

        return self_format_str.format(self.value), other_format_str.format(other)

    # Comparison operators:
    # Each operator compares the value to another, and returns a boolean response
    def __lt__(self, other):
        self_value, other_value = self._normalize_value_pair(other)

        # Compare the sign bits to decide whether a full comparison is required.
        # When the sign is the same, compare the numbers (due to the 2's complement notation, this works for negative
        # values as well. If the sign is different,
        return {True: BinaryValue.less_than("0b" + self_value, "0b" + other_value),
                False: self_value[0] == "1"}[self_value[0] == other_value[0]]

    def __le__(self, other):
        return self == other or self < other

    def __eq__(self, other):
        # Normalize the values, then compare (the sign doesn't affect the result, since both values have the same length
        self_value, other_value = self._normalize_value_pair(other)
        return BinaryValue.equal("0b" + self_value, "0b" + other_value)

    def __ne__(self, other):
        return not self == other  # not equal is complementary to equal

    def __gt__(self, other):
        return not self <= other  # if the value is not smaller or equal to the other, it's greater than it

    def __ge__(self, other):
        return not self < other  # if the value is not smaller than the comparand, it's ether greater or equal to it

    # Arithmetic operators:
    # Each operator performs an arithmetic operation on its value and the value of another object (if applicable), and
    # returns a new BitValue object (or self if an "in-place" version).
    def __abs__(self):
        return BitValue(self.value) if self >= 0 else -self  # the __neg__ operator creates a new BitValue object

    def __neg__(self):
        result = ~self  # the __invert__ operator creates a new BitValue object
        result += 1  # convert from 1's complement to 2's complement
        return result

    def __pos__(self):
        """ This operator retains the value, but returns an object with the minimum number of bits required """
        return BitValue(self.value)

    def __add__(self, other):
        result = BinaryValue.add(self, other)
        return BitValue(result)

    def __iadd__(self, other):
        self.value = BinaryValue.add(self, other)
        return self

    def __sub__(self, other):
        result = BinaryValue.sub(self, other)
        return BitValue(result)

    def __isub__(self, other):
        self.value = BinaryValue.sub(self, other)
        return self

    def __mul__(self, other):
        result = BinaryValue.mul(self, other)
        return BitValue(result)

    def __imul__(self, other):
        self.value = BinaryValue.mul(self, other)
        return self

    def __mod__(self, other):
        result = BinaryValue.mod(self, other)
        return BitValue(result)

    def __imod__(self, other):
        self.value = BinaryValue.mod(self, other)
        return self

    def __floordiv__(self, other):
        result = BinaryValue.div(self, other)
        return BitValue(result)
    __truediv__ = __floordiv__  # BitValue supports integers only

    def __ifloordiv__(self, other):
        self.value = BinaryValue.div(self, other)
        return self
    __itruediv__ = __ifloordiv__  # BitValue supports integers only

    def __pow__(self, other):
        result = BinaryValue.pow(self, other)
        return BitValue(result)

    def __ipow__(self, other):
        self.value = BinaryValue.pow(self, other)
        return self

    # Bitwise operators:
    # Each operator performs a bitwise operation on its value and the value of another object (if applicable), and
    # returns a new BitValue object (or self if an "in-place" version).
    def __invert__(self):
        result = BinaryValue.invert(self)
        return BitValue(result)

    def __and__(self, other):
        self_value, other_value = self._normalize_value_pair(other)
        result = BinaryValue.bitwise_and("0b" + self_value, "0b" + other_value)
        return BitValue(result)

    def __iand__(self, other):
        self_value, other_value = self._normalize_value_pair(other)
        self.value = BinaryValue.bitwise_and("0b" + self_value, "0b" + other_value)
        return self

    def __or__(self, other):
        self_value, other_value = self._normalize_value_pair(other)
        result = BinaryValue.bitwise_or("0b" + self_value, "0b" + other_value)
        return BitValue(result)

    def __ior__(self, other):
        self_value, other_value = self._normalize_value_pair(other)
        self.value = BinaryValue.bitwise_or("0b" + self_value, "0b" + other_value)
        return self

    def __xor__(self, other):
        self_value, other_value = self._normalize_value_pair(other)
        result = BinaryValue.bitwise_xor("0b" + self_value, "0b" + other_value)
        return BitValue(result)

    def __ixor__(self, other):
        self_value, other_value = self._normalize_value_pair(other)
        self.value = BinaryValue.bitwise_xor("0b" + self_value, "0b" + other_value)
        return self

    def __lshift__(self, other):
        result = BinaryValue.shift_left(self, other)
        return BitValue(result)

    def __ilshift__(self, other):
        self.value = BinaryValue.shift_left(self, other)
        return self

    def __rshift__(self, other):
        result = BinaryValue.shift_right(self, other)
        return BitValue(result)

    def __irshift__(self, other):
        self.value = BinaryValue.shift_right(self, other)
        return self

    # Conversions:
    def __bool__(self):
        return "1" in self.value

    def __int__(self):
        return int(self.value, 2) if self >= 0 else -int(str(-self), 2)

    int = __int__
    __index__ = __int__

    def bin(self):
        return "0b" + self.value
    __str__ = bin
    __repr__ = bin

    def oct(self):
        # 3 binary digits = 1 octal digit
        # Adding 2 to the number of digits causes the floor division to behave like ceiling division (in case the number
        # of bits doesn't divide evenly by 3)
        length = len(self.value.lstrip("0"))
        oct_digits = (length + 2) // 3
        format_str = "{:>0" + str(oct_digits) + "o}"

        return "0o" + format_str.format(int(self.value, 2))

    def dec(self):
        return str(int(self))

    def hex(self):
        # 4 binary digits = 1 hexadecimal digit
        # Adding 3 to the number of digits causes the floor division to behave like ceiling division (in case the number
        # of bits doesn't divide evenly by 4)
        length = len(self.value.lstrip("0"))
        hex_digits = (length + 3) // 4
        format_str = "{:>0" + str(hex_digits) + "x}"

        return "0x" + format_str.format(int(self.value, 2)).upper()
