"""
Created By: Yuval Tzur
Date: 19/2/19
Description: The components module defines the base classes for all the different components in the system.
             Components are further divided into subtypes with more specific behaviors.

             Each component should have a name and an ID (once set, they can't be changed).
             While running, the system works in cycles. Each cycle consists of an "up" tick that happens when the cycle
             starts, and a "down" tick that happens when the cycle ends. Components have to implement their
             functionality during those phases. Some might do nothing, which is acceptable, but it's required for
             system-wide actions.
"""

import abc


class Component:
    """ This class is the base class for all the simulated hardware components in the system """

    __metaclass__ = abc.ABCMeta

    def __init__(self, component_id, component_name):
        self._id = str(component_id)
        self._name = str(component_name)

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @abc.abstractmethod
    def up_tick(self):
        """ Performs actions when a cycle starts """
        pass

    @abc.abstractmethod
    def down_tick(self):
        """ Performs actions when a cycle ends """
        pass


class DataComponent(Component):
    """ This class is the base class for components that hold or transfer data """

    __metaclass__ = abc.ABCMeta

    def __init__(self, component_id, component_name):
        super(DataComponent, self).__init__(component_id, component_name)

    @abc.abstractmethod
    def up_tick(self):
        """ Performs actions when a cycle starts """
        pass

    @abc.abstractmethod
    def down_tick(self):
        """ Performs actions when a cycle ends """
        pass

    @staticmethod
    def _validate_input_component(component):
        """ Validates that the input component is valid """
        if component is None:
            return

        if not isinstance(component, DataComponent):
            raise TypeError("only data components can be used as inputs for other data components")
