"""
Created By: Yuval Tzur
Date: 20/2/19
Description: The registers module defines the classes for the different register types. Registers can store data as a
             binary value.

             There are three main types of registers:
             1. General purpose register: holds a value
             2. Slice register: used to access a section within another, larger, register (has no value of its own)
             3. Flag register: used as a set of flags, where each bit represents the status of a different flag
"""

import abc

from src.framework.components.components import DataComponent
from src.framework.bit_value import BitValue


class DataRegister(DataComponent):
    """ This class is the base class for registers that hold a value. Each register has an input component, whose value
        is transferred to the register (if write is enabled). """

    __metaclass__ = abc.ABCMeta

    def __init__(self, register_id, register_name):
        super(DataRegister, self).__init__(register_id, register_name)

        self._write_enable = False
        self._input = None
        self._buffer = None

    @property
    def write_enable(self):
        return self._write_enable

    @property
    def input(self):
        input_str = "({}) {}".format(self._input.id, self._input.name)
        return input_str

    @input.setter
    def input(self, input_component):
        self._validate_input_component(input_component)
        self._input = input_component

    @property
    @abc.abstractmethod
    def content(self):
        pass

    @content.setter
    @abc.abstractmethod
    def content(self, value):
        pass

    @abc.abstractmethod
    def __len__(self):
        pass

    @abc.abstractmethod
    def __getitem__(self, item):
        pass

    @abc.abstractmethod
    def clear(self):
        pass

    @abc.abstractmethod
    def increment(self):
        pass

    @abc.abstractmethod
    def __bool__(self):
        pass

    @abc.abstractmethod
    def __int__(self):
        pass

    @abc.abstractmethod
    def int(self):
        pass

    @abc.abstractmethod
    def __index__(self):
        pass

    @abc.abstractmethod
    def bin(self):
        pass

    @abc.abstractmethod
    def __str__(self):
        pass

    @abc.abstractmethod
    def oct(self):
        pass

    @abc.abstractmethod
    def dec(self):
        pass

    @abc.abstractmethod
    def hex(self):
        pass

    def enable_write(self):
        self._write_enable = True

    def up_tick(self):
        """ Updates the buffer during the "up" tick, before the input changes during the "down" tick """
        self._buffer = self._input.bin() if self.write_enable else None

    def down_tick(self):
        """ Updates the value during the "down" tick, after any "up" reads were performed """
        if self._buffer:
            self.content = self._buffer

        # Once a value was read, disable write until its set by the system
        self._write_enable = False


class GeneralPurposeRegister(DataRegister):
    """ This class represents a register that holds a value with no specific context. Each register has an input
        component, whose value is transferred to the register (if write is enabled). """

    def __init__(self, register_id, register_name, size):
        super(GeneralPurposeRegister, self).__init__(register_id, register_name)
        self._content = BitValue(bits=size)

    @property
    def content(self):
        return self._content.value

    @content.setter
    def content(self, value):
        self._content.value = value

    def __len__(self):
        return len(self._content)

    def __getitem__(self, item):
        return self._content[item]

    def clear(self):
        self._content.value = 0

    def increment(self):
        self._content.increment()

    def __bool__(self):
        return bool(self._content)

    def __int__(self):
        return int(self._content)
    int = __int__
    __index__ = __int__

    def bin(self):
        return self._content.bin()
    __str__ = bin

    def oct(self):
        return self._content.oct()

    def dec(self):
        return self._content.dec()

    def hex(self):
        return self._content.hex()


class SliceRegister(DataRegister):
    """ This class represents a register that accesses a segment of another register. Each register has a parent
        register and an input component. A SliceRegister object allows access to a segment of the parent register, as if
        it were a GeneralPurposeRegister. A segment is defined by a bit index in the parent register, and a segment
        size. The ability of a slice register independent from its parent. """

    def __init__(self, register_id, register_name):
        super(SliceRegister, self).__init__(register_id, register_name)
        self._parent = None
        self._slice = None

    @property
    def parent(self):
        parent_str = "({}) {}".format(self._parent.id, self._parent.name)
        return parent_str

    @property
    def content(self):
        start, end, length = self._slice
        return self._parent[start:end]

    @content.setter
    def content(self, value):
        start, end, length = self._slice
        before, after = self._parent[:start], self._parent[end:]
        content = "0b" + after + BitValue(value, length).value + before
        self._parent.content = content

    def set_slice(self, parent, start_bit, slice_size):
        """ Defines the parent register and the slice within it that can be accessed """

        if not isinstance(parent, DataRegister):
            raise TypeError("only data registers can be accessed by slice registers")

        self._parent = parent
        self._slice = (start_bit, start_bit + slice_size, slice_size)  # start and end match Python slicing

    def __len__(self):
        return self._slice[2]  # slice size

    def __getitem__(self, item):
        bv = BitValue(self.bin(), len(self))
        return bv[item]

    def clear(self):
        self.content = 0

    def increment(self):
        bv = BitValue(self.bin(), len(self))
        bv.increment()
        self.content = bv

    def __bool__(self):
        return "1" in self.content

    def __int__(self):
        return int(BitValue(self.bin(), len(self)))
    int = __int__
    __index__ = __int__

    def bin(self):
        return "0b" + self.content
    __str__ = bin

    def oct(self):
        return BitValue(self.bin(), len(self)).oct()

    def dec(self):
        return BitValue(self.bin(), len(self)).dec()

    def hex(self):
        return BitValue(self.bin(), len(self)).hex()
