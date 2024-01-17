# ==========================================================================
# File: glossary_handler.py
# Description: PyQT6 glossary handler for the REMUS plugin
# Date: 09/01/2024
# Version: 0.1
# Author: José María Delgado Sánchez
# ==========================================================================

# --------------------------------------------------------------------------
# Standard library imports
# --------------------------------------------------------------------------

import logging
from typing import Dict, List, MutableSet
import re

# --------------------------------------------------------------------------
# Third-party library imports
# --------------------------------------------------------------------------

import markdown
from trieregex import TrieRegEx as TRE

# --------------------------------------------------------------------------
# Project specific imports
# --------------------------------------------------------------------------

from proteus.model import ProteusID, PROTEUS_NAME
from proteus.model.project import Project
from proteus.model.object import Object
from proteus.model.properties import BooleanProperty
from proteus.views.components.abstract_component import ProteusComponent
from proteus.utils.events import (
    OpenProjectEvent,
    AddObjectEvent,
    DeleteObjectEvent,
    ModifyObjectEvent,
)

# logging configuration
log = logging.getLogger(__name__)

PARAGRAPH_CLASS = "paragraph"
GLOSSARY_PROPERTY = "is-glossary"


# --------------------------------------------------------------------------
# Class: GlossaryHandler
# Description: Glossary handler class for the REMUS plugin
# Date: 09/01/2024
# Version: 0.1
# Author: José María Delgado Sánchez
# --------------------------------------------------------------------------
class GlossaryHandler(ProteusComponent):
    """
    Glossary handler class for the REMUS plugin. Implements the neccesary
    logic to handle glossary items highlighting in the document html view.

    Glossary items are not case sensitive. If a glossary item contains multiple
    words separated by commas, each word is considered a glossary item. When
    highlighting the glossary items, the first glossary item found is used to
    link the item to the description, all descriptions will be displayed in the
    tooltip.

    Glossary items are detected in text using the regex pattern '\b(?<!-){item}(?!-)\b'.
    This means that if the item is 'item', the text 'item', 'item/', 'Item' or
    'ITEM,' will be detected as a glossary reference but not 'item1', '-item', etc.
    """

    # Class attributes
    items_descriptions: Dict[ProteusID, str] = dict()  # k: ProteusID, v: description
    object_ids_by_item: Dict[
        str, MutableSet[ProteusID]
    ] = dict()  # k: glossary item name, v: Set[ProteusID]
    pattern: re.Pattern = None

    # --------------------------------------------------------------------------
    # Method: __init__
    # Description: It initializes the glossary handler.
    # Date: 09/01/2024
    # Version: 0.1
    # Author: José María Delgado Sánchez
    # --------------------------------------------------------------------------
    def __init__(self, parent):
        """
        It initializes the glossary handler.
        """
        super().__init__(parent)

        # Subscribe to the events
        OpenProjectEvent().connect(self.update_on_project_open)
        AddObjectEvent().connect(self.update_on_add_object)
        DeleteObjectEvent().connect(self.update_on_delete_object)
        ModifyObjectEvent().connect(self.update_on_modify_object)

    # --------------------------------------------------------------------------
    # Method: update_on_project_open
    # Description: It loads the glossary items from the project.
    # Date: 09/01/2024
    # Version: 0.1
    # Author: José María Delgado Sánchez
    # --------------------------------------------------------------------------
    def update_on_project_open(self) -> None:
        """
        It loads the glossary items from the project.

        Triggered by: OpenProjectEvent
        """
        # Clear the glossary items
        GlossaryHandler.items_descriptions = dict()
        GlossaryHandler.object_ids_by_item = dict()

        # Iterate over the project objects
        # NOTE: Iterating using ids to make it more readable
        current_project: Project = self._controller.get_current_project()

        for object_id in current_project.get_ids():
            # Skip the current project
            if object_id == current_project.id:
                continue

            # Get the object
            object: Object = self._controller.get_element(object_id)

            # Check if the object is a glossary item
            if self._is_glossary_item(object):
                self._add_glossary_item(object)

        # Setup the pattern
        self._setup_pattern()

    # --------------------------------------------------------------------------
    # Method: update_on_add_object
    # Description: It adds a glossary item to the glossary.
    # Date: 09/01/2024
    # Version: 0.1
    # Author: José María Delgado Sánchez
    # --------------------------------------------------------------------------
    def update_on_add_object(self, object_id: ProteusID) -> None:
        """
        It adds a glossary item to the glossary. If the glossary item
        contains multiple words separated by commas, add each word as
        a glossary item.

        Triggered by: AddObjectEvent

        :param object_id: Object id to add
        """
        # Get the object
        object: Object = self._controller.get_element(object_id)

        # Check if the object is a glossary item
        if self._is_glossary_item(object):
            self._add_glossary_item(object)

        # Setup the pattern
        self._setup_pattern()

    # --------------------------------------------------------------------------
    # Method: update_on_delete_object
    # Description: It deletes a glossary item from the glossary.
    # Date: 09/01/2024
    # Version: 0.1
    # Author: José María Delgado Sánchez
    # --------------------------------------------------------------------------
    def update_on_delete_object(self, object_id: ProteusID) -> None:
        """
        It deletes a glossary item from the glossary.

        Triggered by: DeleteObjectEvent

        :param object_id: Object id to delete
        """
        self._delete_glossary_item(object_id)

        # Setup the pattern
        self._setup_pattern()

    # --------------------------------------------------------------------------
    # Method: update_on_modify_object
    # Description: It modifies stored glossary item.
    # Date: 09/01/2024
    # Version: 0.1
    # Author: José María Delgado Sánchez
    # --------------------------------------------------------------------------
    def update_on_modify_object(self, object_id: ProteusID) -> None:
        """
        It modifies a glossary item from the glossary. If the object
        was not a glossary item and now it is, it is added to the
        glossary. In the opposite case, it is deleted from the glossary.

        Triggered by: ModifyObjectEvent

        :param object_id: Object id to modify
        """
        # Delete the glossary item if exists
        self._delete_glossary_item(object_id)

        # Get the object
        object: Object = self._controller.get_element(object_id)

        # Check if the object is a glossary item
        if self._is_glossary_item(object):
            self._add_glossary_item(object)

        # Setup the pattern
        self._setup_pattern()

    # --------------------------------------------------------------------------
    # Method: _is_glossary_item
    # Description: It checks if the object is a glossary item.
    # Date: 09/01/2024
    # Version: 0.1
    # Author: José María Delgado Sánchez
    # --------------------------------------------------------------------------
    def _is_glossary_item(self, object: Object) -> bool:
        """
        Check if the object is a glossary item. It checks if the object
        is a paragraph and if it has the is-glossary property set to True.

        Property is-glossary must be a BooleanProperty.

        :param object: Object to check
        """
        # Check if the object is a paragraph
        if PARAGRAPH_CLASS not in object.classes:
            return False

        # Get is-glossary property
        glossary_property: BooleanProperty = object.get_property(GLOSSARY_PROPERTY)

        # Check if the property is correct
        if not isinstance(glossary_property, BooleanProperty):
            return False

        # Check if the property is True
        if not glossary_property.value:
            return False

        return True

    # --------------------------------------------------------------------------
    # Method: _add_glossary_item
    # Description: It adds a glossary item to the glossary.
    # Date: 09/01/2024
    # Version: 0.1
    # Author: José María Delgado Sánchez
    # --------------------------------------------------------------------------
    def _add_glossary_item(self, object: Object) -> None:
        """
        It adds a glossary item to the glossary. The description is stored
        by object id, previously converted from markdown to html. The item
        is stored by item name, adding the object id to the list of ids
        linked to the glossary item name (this allows multiple descriptions).

        Glossary items names are stripped and converted to lowercase.

        :param object: Object to add
        """
        # Get items
        items: str = object.get_property(PROTEUS_NAME).value

        # Get description and convert markdown to html
        _description: str = object.get_property("text").value
        description = markdown.markdown(
            _description,
            extensions=[
                "markdown.extensions.fenced_code",
                "markdown.extensions.codehilite",
                "markdown.extensions.tables",
                "markdown.extensions.toc",
            ],
        )

        # Split the items
        glossary_items: List[str] = [item.strip() for item in items.split(",")]

        # Add the items to the glossary
        for item in glossary_items:
            if item != "":
                # Store the description by id
                GlossaryHandler.items_descriptions[object.id] = description

                # Store the id by item
                lowercased_item = item.lower()
                id_list: MutableSet[ProteusID] = GlossaryHandler.object_ids_by_item.get(
                    lowercased_item, set()
                )
                id_list.add(object.id)
                GlossaryHandler.object_ids_by_item[lowercased_item] = id_list

    # --------------------------------------------------------------------------
    # Method: _delete_glossary_item
    # Description: It deletes a glossary item from the glossary.
    # Date: 09/01/2024
    # Version: 0.1
    # Author: José María Delgado Sánchez
    # --------------------------------------------------------------------------
    def _delete_glossary_item(self, object_id: ProteusID) -> None:
        """
        Delete a glossary item from the class attributed. It removes the
        description by id. It also removes the id from the item list.
        When an item list is empty, it is removed from the class attribute.

        :param object_id: Object id to delete
        """
        # Check if the description is in the stored descriptions by id
        if object_id in GlossaryHandler.items_descriptions:
            GlossaryHandler.items_descriptions.pop(object_id)

        # Check if the item is in the stored ids by item
        items_with_empty_ids: List[str] = []
        for item, ids in GlossaryHandler.object_ids_by_item.items():
            if object_id in ids:
                ids.remove(object_id)

            if len(ids) == 0:
                items_with_empty_ids.append(item)

        # Remove the items with empty ids
        for item in items_with_empty_ids:
            GlossaryHandler.object_ids_by_item.pop(item)

    def _setup_pattern(self) -> None:
        """
        It sets up the regex pattern to highlight the glossary items.

        The pattern is created from a list of glossary items. The list is
        is converted to a TrieRegEx object and then to a regex pattern.
        """
        old_pattern = GlossaryHandler.pattern
        try:
            GlossaryHandler.pattern = None

            # Get the glossary items
            glossary_items: List[str] = list(GlossaryHandler.object_ids_by_item.keys())

            if len(glossary_items) == 0:
                return

            # Order the items by length so items that contain other items are processed first
            glossary_items = sorted(glossary_items, key=len, reverse=True)

            tre = TRE(*glossary_items)

            # Create the pattern
            GlossaryHandler.pattern = re.compile(rf"\b(?<!-){tre.regex()}(?!-)\b", re.IGNORECASE)
        except Exception as e:
            log.error(f"There was an error while updating the glossary regex pattern: {e}")
            GlossaryHandler.pattern = old_pattern

    # --------------------------------------------------------------------------
    # Method: highlight_glossary_items (static)
    # Description: It highlights the glossary items in the text.
    # Date: 10/01/2024
    # Version: 0.1
    # Author: José María Delgado Sánchez
    # --------------------------------------------------------------------------
    @staticmethod
    def highlight_glossary_items(context, text: str) -> str:
        """
        It highlights the glossary items in the text.

        If the glossary item has multiple descriptions, all descriptions
        are displayed in the tooltip.

        Method used in the XSLT stylesheet.
        """
        input_text = text

        try:
            def highlight_item(match: re.Match) -> str:
                # Get the match
                match_text: str = match.group()

                # Get the item
                item = match_text.lower()

                # Get ids linked to the item
                item_linked_ids = GlossaryHandler.object_ids_by_item[item]
                descriptions: List[str] = [
                    GlossaryHandler.items_descriptions[item_id]
                    for item_id in item_linked_ids
                ]

                # Create the description and set the item id
                item_id = list(item_linked_ids)[0]
                description_html = ""
                for index, description in enumerate(descriptions):
                    # Insert space between descriptions if there are more than one
                    if index > 0:
                        description_html += "<hr></hr>"

                    # Add the description with a link to the item
                    description_html += f"{description}"

                return f'<a href="#{item_id}" onclick="selectAndNavigate(`{item_id}`, event)" data-tippy-content="{description_html}">{match_text}</a>'
            

            if GlossaryHandler.pattern is None:
                return text

            # Replace the items with the decorated items
            text = re.sub(GlossaryHandler.pattern, highlight_item, text)
        except Exception as e:
            log.error(f"There was an error while highlighting the glossary items in text {input_text}. Error: {e}")
            text = input_text

        return text