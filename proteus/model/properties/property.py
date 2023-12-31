# ==========================================================================
# File: property.py
# Description: PROTEUS abstract property
# Date: 27/02/2023
# Version: 0.3
# Author: Amador Durán Toro
#         Pablo Rivera Jiménez
#         José María Delgado Sánchez    
# ==========================================================================

# --------------------------------------------------------------------------
# Standard library imports
# --------------------------------------------------------------------------

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Any
import logging

# --------------------------------------------------------------------------
# Third-party library imports
# --------------------------------------------------------------------------

import lxml.etree as ET

# --------------------------------------------------------------------------
# Project specific imports
# --------------------------------------------------------------------------

import proteus
from proteus.model import NAME_TAG, CATEGORY_TAG
from proteus.model.properties import DEFAULT_NAME, DEFAULT_CATEGORY

# logging configuration
log = logging.getLogger(__name__)

# --------------------------------------------------------------------------
# Class: Property (abstract)
# Description: Abstract dataclass for PROTEUS properties
# Date: 17/10/2022
# Version: 0.3
# Author: Amador Durán Toro
# --------------------------------------------------------------------------
# About using __post_init__: 
# https://stackoverflow.com/questions/60179799/python-dataclass-whats-a-pythonic-way-to-validate-initialization-arguments
# Dataclasses have a replace(object, value=new_value) function which returns 
# a copy of an object with a new value (similar to attr.evolve()).
# https://stackoverflow.com/questions/56402694/how-to-evolve-a-dataclass-in-python
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Property(ABC):
    """
    Abstract class for PROTEUS properties.
    """
    # dataclass instance attributes
    name     : str = str(DEFAULT_NAME)
    category : str = str(DEFAULT_CATEGORY)
    value    : Any = str()

    def __post_init__(self) -> None:
        """
        It validates name and category of an abstract PROTEUS property. 
        Value is converted into a string (just in case) and validated in subclasses.
        """      
        # Name validation
        if not self.name:
            log.warning(f"PROTEUS properties must have a '{NAME_TAG}' attribute -> assigning '{DEFAULT_NAME}' as name")
            # self.name = DEFAULT_NAME cannot be used when frozen=True
            # https://stackoverflow.com/questions/53756788/how-to-set-the-value-of-dataclass-field-in-post-init-when-frozen-true
            object.__setattr__(self, 'name', DEFAULT_NAME)

        # Category validation
        if not self.category:
            # self.category = DEFAULT_CATEGORY cannot be used when frozen=True
            object.__setattr__(self, 'category', DEFAULT_CATEGORY)

        # Value -> string
        object.__setattr__(self, 'value', str(self.value))

    def clone(self, new_value=None) -> 'Property':
        """
        It clones the property with a new value if it is not None.
        The new value must be provided as a string.
        :param new_value: new value for the property.
        :return: a copy of the property with the new value.
        """
        if new_value is None:
            return replace(self)
        
        return replace(self, value=str(new_value))

    def generate_xml(self) -> ET._Element:
        """
        This template method generates the XML element for the property.
        """
        # element_tagname is a class attribute of each concrete subclass
        property_element : ET._Element = ET.Element(self.element_tagname)
        property_element.set(NAME_TAG, self.name)
        property_element.set(CATEGORY_TAG, self.category)
        # generate_xml_value() is defined in subclasses
        property_element.text = self.generate_xml_value(property_element)

        return property_element

    @abstractmethod
    def generate_xml_value(self, _:ET._Element = None) -> str | ET.CDATA:
        """
        It generates the value of the property for its XML element.
        Depending on the type of property, it can be a string or
        a CDATA section.
        """
