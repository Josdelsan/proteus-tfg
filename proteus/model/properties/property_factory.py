# ==========================================================================
# File: property_factory.py
# Description: PROTEUS property Factory
# Date: 27/02/2023
# Version: 0.3
# Author: Amador Durán Toro
#         Pablo Rivera Jiménez
#         José María Delgado Sánchez
# ==========================================================================

# --------------------------------------------------------------------------
# Standard library imports
# --------------------------------------------------------------------------

import logging

# --------------------------------------------------------------------------
# Third-party library imports
# --------------------------------------------------------------------------

import lxml.etree as ET

# --------------------------------------------------------------------------
# Project specific imports
# --------------------------------------------------------------------------

from proteus.model import ProteusClassTag
from proteus.model.properties.property import Property
from proteus.model.properties.string_property import StringProperty
from proteus.model.properties.boolean_property import BooleanProperty
from proteus.model.properties.date_property import DateProperty
from proteus.model.properties.time_property import TimeProperty
from proteus.model.properties.markdown_property import MarkdownProperty
from proteus.model.properties.integer_property import IntegerProperty
from proteus.model.properties.float_property import FloatProperty
from proteus.model.properties.enum_property import EnumProperty
from proteus.model.properties.file_property import FileProperty
from proteus.model.properties.url_property import UrlProperty
from proteus.model.properties.classlist_property import ClassListProperty
from proteus.model.properties.code_property import CodeProperty, ProteusCode

from proteus.model import (
    NAME_ATTRIBUTE,
    CATEGORY_ATTRIBUTE,
    REQUIRED_ATTRIBUTE,
    INMUTABLE_ATTRIBUTE,
    TOOLTIP_ATTRIBUTE,
)

from proteus.model.properties import (
    CLASS_TAG,
    DEFAULT_CATEGORY,
    CHOICES_ATTRIBUTE,
    PREFIX_TAG,
    NUMBER_TAG,
    SUFFIX_TAG,
)

# logging configuration
log = logging.getLogger(__name__)

# --------------------------------------------------------------------------
# Class: PropertyFactory
# Description: Factory class for PROTEUS properties
# Date: 30/08/2022
# Version: 0.1
# Author: Amador Durán Toro
# --------------------------------------------------------------------------


class PropertyFactory:
    """
    Factory class for PROTEUS properties.
    """

    # Dictionary of valid property types and classes (class attribute)
    # Note the type hint type[Property] for the dictionary
    # https://adamj.eu/tech/2021/05/16/python-type-hints-return-class-not-instance/
    propertyFactory: dict[str, type[Property]] = {
        BooleanProperty.element_tagname: BooleanProperty,
        StringProperty.element_tagname: StringProperty,
        DateProperty.element_tagname: DateProperty,
        TimeProperty.element_tagname: TimeProperty,
        MarkdownProperty.element_tagname: MarkdownProperty,
        IntegerProperty.element_tagname: IntegerProperty,
        FloatProperty.element_tagname: FloatProperty,
        EnumProperty.element_tagname: EnumProperty,
        FileProperty.element_tagname: FileProperty,
        UrlProperty.element_tagname: UrlProperty,
        ClassListProperty.element_tagname: ClassListProperty,
        CodeProperty.element_tagname: CodeProperty,
    }

    @classmethod
    def create(cls, element: ET._Element) -> Property | None:
        """
        Factory class method for PROTEUS properties.
        :param element: XML element with the property.
        :return: Property object or None if the property type is not valid.
        """
        # Check it is one of the valid property types
        try:
            property_class = cls.propertyFactory[element.tag]
        except KeyError:
            log.warning(
                f"<{element.tag}> is not a valid PROTEUS property type -> ignoring invalid property"
            )
            return None

        # Get name (checked in property constructors)
        name = element.attrib.get(NAME_ATTRIBUTE)

        # Get category (checked in property constructors)
        category = element.attrib.get(CATEGORY_ATTRIBUTE, DEFAULT_CATEGORY)

        # Get required (checked in property constructors)
        required_str = element.attrib.get(REQUIRED_ATTRIBUTE, "false")
        required: bool = True if required_str.lower() == "true" else False

        # Get inmutable (checked in property constructors)
        inmutable_str = element.attrib.get(INMUTABLE_ATTRIBUTE, "false")
        inmutable: bool = True if inmutable_str.lower() == "true" else False

        # Get tooltip (checked in property constructors)
        tooltip = element.attrib.get(TOOLTIP_ATTRIBUTE, str())

        # Get value (checked in property constructors)
        if property_class is ClassListProperty:
            # We need to collect the list of class names,
            # put them toghether in a list of ProteusClassTag objects
            if element.findall(CLASS_TAG):
                value = [ProteusClassTag(e.text) for e in element.findall(CLASS_TAG)]
            else:
                value = list()
        elif property_class is CodeProperty:
            # We need to collect its prefix, number and suffix
            prefix = element.find(PREFIX_TAG).text
            number = element.find(NUMBER_TAG).text
            suffix = element.find(SUFFIX_TAG).text
            value = ProteusCode(prefix, number, suffix)
        else:
            # Value could be empty
            value = str(element.text)

        # Create and return the property object

        # Special case: EnumProperty
        if property_class is EnumProperty:
            # We need to collect its choices
            choices = element.attrib.get(CHOICES_ATTRIBUTE, str())
            return EnumProperty(
                name, category, value, tooltip, required, inmutable, choices
            )

        # Ordinary case: rest of property classes
        return property_class(name, category, value, tooltip, required, inmutable)
