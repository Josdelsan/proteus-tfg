# ==========================================================================
# File: test_boolean_properties.py
# Description: pytest file for PROTEUS boolean properties
# Date: 22/10/2022
# Version: 0.2
# Author: Pablo Rivera Jiménez
#         Amador Durán Toro
# ==========================================================================
# Update: 21/10/2022 (Amador)
# Description:
# - Code review.
# ==========================================================================
# Update: 22/10/2022 (Amador)
# Description:
# - Common code extracted as fixtures.
# ==========================================================================

# --------------------------------------------------------------------------
# Standard library imports
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Third-party library imports
# --------------------------------------------------------------------------

import pytest
import lxml.etree as ET

# --------------------------------------------------------------------------
# Project specific imports
# --------------------------------------------------------------------------

from proteus.model.properties import BOOLEAN_PROPERTY_TAG

# --------------------------------------------------------------------------
# Test specific imports
# --------------------------------------------------------------------------

import proteus.tests.properties.fixtures as fixtures

# --------------------------------------------------------------------------
# Boolean property tests
# --------------------------------------------------------------------------

@pytest.mark.parametrize('name',         [str(), 'test name'     ])
@pytest.mark.parametrize('category',     [str(), 'test category' ])
@pytest.mark.parametrize('value, expected_value, expected_xml_value',
    [
        ('false', False, 'false'),
        ('true', True, 'true'),
        ('True', True, 'true'),
        ('False', False, 'false'),
        (str(), False, 'false'),
        (7.5, False, 'false'),
        (7, False, 'false'),
        ('test value', False, 'false')
    ]
)
@pytest.mark.parametrize('new_value, expected_new_value, expected_new_xml_value',
    [   
        ('false', False, 'false'),
        ('true', True, 'true'),
        ('True', True, 'true'),
        ('False', False, 'false'),
        (str(), False, 'false'),
        (7.5, False, 'false'),
        (7, False, 'false'),
        ('test value', False, 'false')
    ]
)

def test_boolean_properties(name, category, value, expected_value, expected_xml_value, new_value, expected_new_value, expected_new_xml_value):
    """
    It tests creation, update, and evolution (cloning with a new value) 
    of boolean properties.
    """
    # Create property from XML element
    property_tag = BOOLEAN_PROPERTY_TAG
    (property, name, category) = fixtures.create_property(property_tag, name, category, value)

    # Check property
    assert(property.name == name)
    assert(property.category == category)    
    assert(property.value == expected_value)
    assert(
        ET.tostring(property.generate_xml()).decode() ==
        f'<{property_tag} name="{name}" category="{category}">{expected_xml_value}</{property_tag}>'
    )

    # Clone the property without changes
    cloned_property = property.clone()

    # Check cloned property
    assert(cloned_property.name == property.name)
    assert(cloned_property.category == property.category)
    assert(cloned_property.value == property.value)

    # Clone the property changing value
    evolved_property = property.clone(new_value)

    # Check cloned property
    assert(evolved_property.name == name)
    assert(evolved_property.category == category)
    assert(evolved_property.value == expected_new_value)    
    assert(
        ET.tostring(evolved_property.generate_xml()).decode() ==
        f'<{property_tag} name="{name}" category="{category}">{expected_new_xml_value}</{property_tag}>'
    )
