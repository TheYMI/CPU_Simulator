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


class BitValue:
    """ The value class represents a binary value """

    def __init__(self, value=0, bits=32):
        # Check for legality and set the number of bits (once set, can't be changed)
        if type(bits) is not int:
            raise RuntimeError("Number of bits for a value must be an integer")
        self._bits = bits

        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        """ The setter can convert different types of values:
            int  -> base 10
            str  -> base 10
            "0b" -> base 2
            "0o" -> base 8
            "0x" -> base 16
            float is not supported at the moment
        """
        format_str = "{:0>" + str(self.bits) + "b}"

        try:
            # Convert to string to identify the base (assume decimal by default)
            value_str = str(new_value)
            base = {"0b": 2, "0o": 8, "0x": 16}.get(value_str[0:2], 10)

            # Modulo is used to truncate the value into the required number of bits while preserving 2's complement in
            # negative numbers
            int_value = int(value_str, base) % (2**self.bits)
            value_str = format_str.format(int_value)
        except ValueError:
            raise RuntimeError("Illegal value: " + str(new_value))

        self._value = value_str[-self.bits:]

    @property
    def bits(self):
        return self._bits

    @bits.setter
    def bits(self, num_of_bits):
        pass

    # Slicing:
    # Slicing allows handling of subset of bits (steps different than 1 are not supported)
    # Due to the inverted indexing scheme (index 0 = MSB; index -1 = LSB), some extra manipulation is required
    def __getitem__(self, key):
        if type(key) is slice:
            # The 'indices' method returns the normalized indices, requiring only the switch from LTR to RTL indexing
            start, stop, step = key.indices(self.bits)
            start, stop, step = self.bits - stop, self.bits - start, 1
        else:
            # A positive index requires the switch from LTR to RTL indexing
            # A negative index is in the correct place, but with the opposite sign
            stop = self.bits - key if key >= 0 else abs(key)
            start, step = stop - 1, 1

        return self.value[start:stop:step]

    # Comparison operators:
    # Each operator compares its integer value to an integer representation of another object
    def __lt__(self, other):
        return int(self) < int(other)

    def __le__(self, other):
        return int(self) <= int(other)

    def __eq__(self, other):
        return int(self) == int(other)

    def __ne__(self, other):
        return int(self) != int(other)

    def __ge__(self, other):
        return int(self) >= int(other)

    def __gt__(self, other):
        return int(self) > int(other)

    # Arithmetic operators:
    # Each operator performs an arithmetic operation on its integer value and an integer representation of another
    # object (if applicable), and returns a new BitValue object (or self if an "in-place" version)
    def __abs__(self):
        int_value = int(self) if self._value[0] == "0" else -int(self)
        return BitValue(int_value, self.bits)

    def __neg__(self):
        return BitValue(-int(self), self.bits)

    def __pos__(self):
        return BitValue(int(self), self.bits)

    def __add__(self, other):
        return BitValue(int(self) + int(other), self.bits)

    def __iadd__(self, other):
        self.value = int(self) + int(other)
        return self

    def __sub__(self, other):
        return BitValue(int(self) - int(other), self.bits)

    def __isub__(self, other):
        self.value = int(self) - int(other)
        return self

    def __mul__(self, other):
        return BitValue(int(self) * int(other), self.bits)

    def __imul__(self, other):
        self.value = int(self) * int(other)
        return self

    def __mod__(self, other):
        return BitValue(int(self) % int(other), self.bits)

    def __imod__(self, other):
        self.value = int(self) % int(other)
        return self

    def __floordiv__(self, other):
        return BitValue(int(self) // int(other), self.bits)
    __truediv__ = __floordiv__

    def __ifloordiv__(self, other):
        self.value = int(self) // int(other)
        return self
    __itruediv__ = __ifloordiv__

    def __pow__(self, other):
        if int(other) < 0:
            raise ValueError("Exponent must be a positive integer")
        return BitValue(int(self) ** int(other), self.bits)

    def __ipow__(self, other):
        if int(other) < 0:
            raise ValueError("Exponent must be a positive integer")
        self.value = int(self) ** int(other)
        return self

    # Bitwise operators:
    # Each operator performs a bitwise operation on its integer value and an integer representation of another
    # object (if applicable), and returns a new BitValue object (or self if an "in-place" version)
    def __invert__(self):
        return BitValue(~int(self), self.bits)

    def __and__(self, other):
        return BitValue(int(self) & int(other), self.bits)

    def __iand__(self, other):
        self.value = int(self) & int(other)
        return self

    def __or__(self, other):
        return BitValue(int(self) | int(other), self.bits)

    def __ior__(self, other):
        self.value = int(self) | int(other)
        return self

    def __xor__(self, other):
        return BitValue(int(self) ^ int(other), self.bits)

    def __ixor__(self, other):
        self.value = int(self) ^ int(other)
        return self

    def __lshift__(self, other):
        return BitValue(int(self) << other, self.bits)

    def __ilshift__(self, other):
        self.value = int(self) << other
        return self

    def __rshift__(self, other):
        return BitValue(int(self) >> other, self.bits)

    def __irshift__(self, other):
        self.value = int(self) >> other
        return self

    # Evaluation as boolean
    def __bool__(self):
        return int(self) != 0

    # Conversions:
    def __int__(self):
        return int(self.value, 2)
    int = __int__
    __index__ = __int__

    def bin(self):
        return "0b" + self.value
    __str__ = bin

    def oct(self):
        # 3 binary digits = 1 octal digit
        # Adding 2 to the number of digits causes the floor division to behave like ceiling division (in case the number
        # of bits doesn't divide evenly by 3)
        hex_digits = (self.bits + 2) // 3
        format_str = "{:>0" + str(hex_digits) + "o}"

        return "0o" + format_str.format(int(self)).upper()

    def dec(self):
        return str(int(self))

    def hex(self):
        # 4 binary digits = 1 hexadecimal digit
        # Adding 3 to the number of digits causes the floor division to behave like ceiling division (in case the number
        # of bits doesn't divide evenly by 4)
        hex_digits = (self.bits + 3) // 4
        format_str = "{:>0" + str(hex_digits) + "x}"

        return "0x" + format_str.format(int(self)).upper()
