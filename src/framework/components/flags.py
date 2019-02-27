"""
Created By: Yuval Tzur
Date: 26/2/19
Description: The flags module defines the classes for the different flag types. Flags are one-bit values. Some flags may
             trigger an interrupt when their value changes. Some flags represent an interrupt.

             In addition to single flags, a register can be used to hold the values of several distinct flags by
             assigning different bits within the register to different flags. Such registers can behave as registers at
             times, but their value has no meaning by itself (it's just a compact representation of all the different
             values).
"""

import abc

from src.framework.components.components import DataComponent
from src.framework.bit_value import BitValue


class BaseFlag(DataComponent):
    """ This is the base class for flags """

    __metaclass__ = abc.ABCMeta

    def __init__(self, flag_id, flag_name):
        super(BaseFlag, self).__init__(flag_id, flag_name)
        self._content = False

    @property
    def content(self):
        return self._content

    def __len__(self):
        return 1

    @abc.abstractmethod
    def clear(self):
        pass

    @abc.abstractmethod
    def set(self):
        pass

    @abc.abstractmethod
    def complement(self):
        pass

    @abc.abstractmethod
    def toggle(self):
        pass

    def up_tick(self):
        pass

    def down_tick(self):
        pass

    def __bool__(self):
        return self.content

    def __int__(self):
        return int(self.content)
    int = __int__
    __index__ = __int__

    def _get_value_str(self):
        return "1" if self.content else "0"
    dec = _get_value_str

    def bin(self):
        return "0b" + self._get_value_str()

    def oct(self):
        return "0o" + self._get_value_str()

    def hex(self):
        return "0x" + self._get_value_str()

    def __str__(self):
        return str(self.content)


class Flag(BaseFlag):
    """ This class represents a simple one-bit flag """

    def __init__(self, flag_id, flag_name):
        super(Flag, self).__init__(flag_id, flag_name)
        self._buffer = None

    def clear(self):
        self._buffer = False

    def set(self):
        self._buffer = True

    def complement(self):
        self._buffer = not self.content
    toggle = complement

    def down_tick(self):
        if self._buffer is not None:
            self._content = self._buffer

        # Once the buffer was read, clear the buffer
        self._buffer = None


class InterruptFlag(BaseFlag):
    """ This class represents a flag used for interrupt tracking. Whenever an interrupt represented by this flag occurs,
        the flag is set. The flag is cleared once the value is checked. """

    def __init__(self, flag_id, flag_name):
        super(InterruptFlag, self).__init__(flag_id, flag_name)

    def clear(self):
        self._content = False

    def set(self):
        self._content = True

    def complement(self):
        self._content = not self.content
    toggle = complement

    def check(self):
        """ Checks whether an interrupt was raised (value is true) since the last check, and clears the interrupt """
        interrupt_raised = self.content
        self.clear()
        return interrupt_raised


# TODO: FlagRegister requires some decisions and implementation
class FlagRegister(DataComponent):
    """ This class represents a register that holds the values of a set of one-bit flags. Each flag can be set or
        cleared separately, but some actions can be taken on the register as a whole. Not all bits in a flag register
        need to be assigned to working flags. Flags can be accessed by index, or by name. """

    def __init__(self, register_id, register_name, size):
        super(FlagRegister, self).__init__(register_id, register_name)
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

    def up_tick(self):
        # TODO: implement this
        raise NotImplementedError

    def down_tick(self):
        # TODO: implement this
        raise NotImplementedError

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
