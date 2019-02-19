"""
Created By: Yuval Tzur
Date: 19/2/19
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


class BitValue:
    """ The BitValue class allows to perform operations on a binary value, represented by a set amount of bits (similar
        to how values are represented in hardware). All operations are performed using boolean arithmetic to simulate an
        actual binary value (while conversion to integers is easier, the purpose of this project is educational).
        Negative values are represented using 2's complement """

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

    def __init__(self, value=None, bits=32, signed=True):
        """ Initializes a an object with the binary representation of the value, as it fits in the given amount of bits.
            Once the number of bits is set during the object's initialization, it can't be changed """

        # Check for legality and set the number of bits
        if type(bits) is not int:
            raise TypeError("number of bits for a value must be an integer")
        if bits < 1:
            raise ValueError("number of bits for a value must be positive")
        self._bits = bits

        self.signed = signed

        self._value = None
        self.value = value

    @property
    def bits(self):
        return self._bits

    @property
    def value(self):
        return self._value

    # Base conversions
    # These functions convert numbers from different bases to binary, as represented in the required number of bits
    def _adapt_bit_count(self, value):
        """ Adapt the value to the required number of bits """

        padding = value[0] if self.signed else "0"
        format_str = "{:" + padding + ">" + str(self.bits) + "}"
        value = format_str.format(value)

        return value[-self.bits:]

    def _set_from_bin(self, value):
        """ Remove the '0b' prefix if needed and check that the value is indeed binary """

        try:
            parsed_value = re.match(r"^(0b)?(?P<value>[01]+)$", str(value))
            bin_value = parsed_value.group("value")

            self._value = self._adapt_bit_count(bin_value)
        except AttributeError:
            raise ValueError("illegal binary value: '" + str(value) + "'")

    def _set_from_oct(self, value):
        """ Converts an octal value to a binary value """

        try:
            parsed_value = re.match(r"^(0o)?(?P<value>[0-7]+)$", str(value))
            value = parsed_value.group("value")
            bin_value = "".join([self._oct[digit] for digit in value])

            self._value = self._adapt_bit_count(bin_value)
        except AttributeError:
            raise ValueError("illegal octal value: '" + str(value) + "'")

    def _set_from_int(self, value):
        """ Converts an integer value to a binary value (accepts integer and string) """

        value = int(value)
        value, negative = abs(value), value < 0  # work with the positive value and handle the sign later

        bin_value = ""
        while value:
            bin_value = str(value % 2) + bin_value
            value //= 2

        # Add leading zero to indicate positive value
        bin_value = "0" + bin_value
        self._value = self._adapt_bit_count(bin_value)

        # If the original value was negative, change the sign using 2's complement
        if negative:
            self.invert()
            self.increment()
    _from_dec = _set_from_int

    def _set_from_hex(self, value):
        """ Converts an hexadecimal value to a binary value """

        try:
            parsed_value = re.match(r"^(0x)?(?P<value>[\da-fA-F]+)$", str(value))
            value = parsed_value.group("value").upper()
            bin_value = "".join([self._hex[digit] for digit in value])

            self._value = self._adapt_bit_count(bin_value)
        except AttributeError:
            raise ValueError("illegal hexadecimal value: '" + str(value) + "'")

    @value.setter
    def value(self, value):
        """ Sets the value to the binary representation of the given value that matches the required number of bits """

        if value is None:
            value = "0b0"

        if type(value) not in [int, str, BitValue]:
            raise TypeError("illegal type for binary value: " + type(value).__name__)

        value = str(value)
        setter = {"0b": self._set_from_bin,
                  "0o": self._set_from_oct,
                  "0x": self._set_from_hex}.get(value[0:2], self._set_from_int)
        setter(value)

    def __len__(self):
        return self.bits

    def __iter__(self):
        return (self[i] for i in range(self.bits))

    def copy(self):
        return BitValue(self, self.bits, self.signed)

    def _normalize_value(self, value):
        """ Returns a BitValue object with the same bit count and sign status as the current object """
        return BitValue(value, self.bits, self.signed)

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

    # Comparison operators:
    # Each operator compares the value to another, and returns a boolean response (must be similar BitValue objects)
    def compare_to(self, other):
        """ Compares the value to another value """

        other = self._normalize_value(other)

        # If the signs don't match on a signed value, positive is greater than negative
        # Due to the 2's complement representation, MSB = 0 is positive
        if self.signed and self.value[0] != other.value[0]:
            return {True: "greater", False: "less"}[self.value[0] == "0"]

        # Due to the 2's complement representation, greater negative values are also greater in a bitwise comparison
        for i in range(self.bits):
            if self.value[i] != other.value[i]:
                return {True: "greater", False: "less"}[self.value[i] > other.value[i]]

        # If all the bits are the same, the values are equal
        return "equal"

    def __lt__(self, other):
        return self.compare_to(other) == "less"

    def __le__(self, other):
        return self.compare_to(other) in ["less", "equal"]

    def __eq__(self, other):
        return self.compare_to(other) == "equal"

    def __ne__(self, other):
        return self.compare_to(other) != "equal"

    def __gt__(self, other):
        return self.compare_to(other) == "greater"

    def __ge__(self, other):
        return self.compare_to(other) in ["greater", "equal"]

    # Arithmetic operators:
    # Each operator performs an arithmetic operation on its value and the value of another object (if applicable), and
    # returns a new BitValue object (or self if an "in-place" version)
    # Both objects must be similar BitValue objects, and the result is similar as well
    def is_positive(self):
        # Unsigned numbers are always positive
        if not self.signed:
            return True
        return self.value[0] == "0"

    def is_negative(self):
        return not self.is_positive()

    def increment(self):
        """ Increase the value of the object by 1 """
        self.value = self + 1

    def decrement(self):
        """ Decrease the value of the object by 1 """
        self.value = self - 1

    def __abs__(self):
        return self.copy() if self.is_positive() else -self  # the __neg__ operator creates a new BitValue object

    def __neg__(self):
        result = ~self  # the __invert__ operator creates a new BitValue object
        result.increment()  # convert from 1's complement to 2's complement
        return result

    def __pos__(self):
        return self.copy()

    def __add__(self, other):
        other = self._normalize_value(other)

        result, carry = "", "0"
        for i in range(self.bits):
            sum_, carry = self._add[self[i], other[i], carry]
            result = sum_ + result
        result = "0b" + carry + result

        return self._normalize_value(result)

    def __iadd__(self, other):
        self.value = self + other
        return self

    def __sub__(self, other):
        other = self._normalize_value(other)
        return self + -other

    def __isub__(self, other):
        self.value = self - other
        return self

    def __mul__(self, other):
        other = self._normalize_value(other)

        multiplicand = self.copy()
        result = self._normalize_value(0)
        for bit in other:  # start multiplying from the LSB
            if bit == "1":
                result += multiplicand
            multiplicand <<= 1

        return result

    def __imul__(self, other):
        self.value = self * other
        return self

    def _floor_division(self, other):
        """ Divides the value by the denominator and returns both the quotient and the remainder """

        other = self._normalize_value(other)

        if int(other) == 0:
            raise ZeroDivisionError

        remainder = self.copy()
        quotient = self._normalize_value(0)
        while remainder >= other:
            quotient.increment()
            remainder -= other

        return quotient, remainder

    def __mod__(self, other):
        return self._floor_division(other)[1]  # (quotient, remainder)

    def __imod__(self, other):
        self.value = self % other
        return self

    def __floordiv__(self, other):
        return self._floor_division(other)[0]  # (quotient, remainder)
    __truediv__ = __floordiv__  # BitValue supports integers only

    def __ifloordiv__(self, other):
        self.value = self // other
        return self
    __itruediv__ = __ifloordiv__  # BitValue supports integers only

    def __pow__(self, other):
        other = self._normalize_value(other)

        base = self.copy()
        power = other.copy()
        result = self._normalize_value(1)
        for bit in power:
            if bit == "1":
                result *= base
            base *= base  # other**2

        return result

    def __ipow__(self, other):
        self.value = self**other
        return self

    # Bitwise operators:
    # Each operator performs a bitwise operation on its value and the value of another object (if applicable), and
    # returns a new BitValue object (or self if an "in-place" version).
    def __invert__(self):
        value = "0b" + "".join([self._inv[digit] for digit in self.value])
        return self._normalize_value(value)

    def invert(self):
        """ Inverts the value of the object """
        self.value = ~self

    def __and__(self, other):
        other = self._normalize_value(other)
        value = "0b" + "".join([self._and[b1, b2] for b1, b2 in zip(self.value, other.value)])
        return self._normalize_value(value)

    def __iand__(self, other):
        self.value = self & other
        return self

    def __or__(self, other):
        other = self._normalize_value(other)
        value = "0b" + "".join([self._or[b1, b2] for b1, b2 in zip(self.value, other.value)])
        return self._normalize_value(value)

    def __ior__(self, other):
        self.value = self | other
        return self

    def __xor__(self, other):
        other = self._normalize_value(other)
        value = "0b" + "".join([self._xor[b1, b2] for b1, b2 in zip(self.value, other.value)])
        return self._normalize_value(value)

    def __ixor__(self, other):
        self.value = self ^ other
        return self

    def __lshift__(self, other):
        value = "0b" + self.value + ("0" * int(other))
        return self._normalize_value(value)

    def __ilshift__(self, other):
        self.value = self << other
        return self

    def __rshift__(self, other):
        value = "0b" + ("0" * int(other)) + self.value[:-int(other)]
        return self._normalize_value(value)

    def __irshift__(self, other):
        self.value = self >> other
        return self

    # Conversions:
    def __bool__(self):
        return "1" in self

    def __int__(self):
        value, negative = str(abs(self)), self.is_negative()
        return int(value, 2) if not negative else -int(value, 2)
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
