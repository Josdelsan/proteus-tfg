# ==========================================================================
# File: project_container.py
# Description: PyQT6 documents container component for the PROTEUS application
# Date: 25/05/2023
# Version: 0.1
# Author: José María Delgado Sánchez
# ==========================================================================

# --------------------------------------------------------------------------
# Standard library imports
# --------------------------------------------------------------------------

from typing import Dict, List
import logging
from pathlib import Path

# --------------------------------------------------------------------------
# Third-party library imports
# --------------------------------------------------------------------------

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QTabWidget
from PyQt6.QtGui import QIcon

# --------------------------------------------------------------------------
# Project specific imports
# --------------------------------------------------------------------------

from proteus.config import Config
from proteus.model import ProteusID
from proteus.model.object import Object
from proteus.views import ACRONYM_ICON_TYPE
from proteus.views.utils.event_manager import Event, EventManager
from proteus.views.utils.state_manager import StateManager
from proteus.views.components.document_tree import DocumentTree
from proteus.controller.command_stack import Controller

# logging configuration
log = logging.getLogger(__name__)


# --------------------------------------------------------------------------
# Class: DocumentsContainer
# Description: PyQT6 documents container class for the PROTEUS
#              application
# Date: 25/05/2023
# Version: 0.1
# Author: José María Delgado Sánchez
# --------------------------------------------------------------------------
class DocumentsContainer(QTabWidget):
    """
    Documents tab menu component for the PROTEUS application. It is used to
    display the documents of the project in a tab menu. It manages the
    creation of the document tree component for each document.
    """

    # ----------------------------------------------------------------------
    # Method     : __init__
    # Description: Class constructor, invoke the parents class constructors
    #              and create the component.
    # Date       : 27/05/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def __init__(
        self, parent=None, controller: Controller = None, *args, **kwargs
    ) -> None:
        """
        Class constructor, invoke the parents class constructors, create
        the component and connect update methods to the events.

        Store the tabs for each document in a dictionary to access them
        later. Also store the children components of each tab in a
        dictionary to delete when the tab is closed.
        """
        super().__init__(parent, *args, **kwargs)
        # Controller instance
        assert isinstance(
            controller, Controller
        ), "Must provide a controller instance to the documents container component"
        self._controller: Controller = controller

        # Tabs dictionary
        # TODO: Use QTabWidget tabBar to fetch the tabs instead of storing them
        self.tabs: Dict[ProteusID, QWidget] = {}

        # Tab children
        # NOTE: Store children components of each tab in a dictionary to
        #       delete them later
        self.tab_children: Dict[ProteusID, DocumentTree] = {}

        # Create the component
        self.create_component()

        # Subscribe to events
        EventManager.attach(Event.ADD_DOCUMENT, self.update_on_add_document, self)
        EventManager.attach(Event.DELETE_DOCUMENT, self.update_on_delete_document, self)
        EventManager.attach(Event.MODIFY_OBJECT, self.update_on_modify_object, self)

        # Call the current document changed method to update the document for the
        # first time
        if len(self.tabs) > 0:
            self.current_document_changed(index=0)

    # ----------------------------------------------------------------------
    # Method     : create_component
    # Description: Create the documents tab menu component
    # Date       : 25/05/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def create_component(self) -> None:
        """
        Create the documents tab menu component. It gets the project
        structure from the controller and creates a tab for each
        document.
        """
        # Handle tab reordering
        self.setMovable(True)
        self.tabBar().tabMoved.connect(self.tab_moved)

        # Get project structure from project service
        project_structure: List[Object] = self._controller.get_project_structure()

        # Add a document tab for each document in the project
        for document in project_structure:
            self.add_document(document)

        # Connect singal to handle document tab change
        self.currentChanged.connect(self.current_document_changed)

        log.info("Documents container tab component created")

    # ----------------------------------------------------------------------
    # Method     : add_document
    # Description: Add a document to the tab menu creating its child
    #              components (tree and render).
    # Date       : 25/05/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def add_document(self, document: Object, position: int = None) -> None:
        """
        Add a document to the tab menu creating its child component (document
        tree).
        """
        # Create document tab widget
        tab: QWidget = QWidget()
        tab_layout: QHBoxLayout = QHBoxLayout(tab)

        # Tree widget --------------------------------------------------------
        document_tree: DocumentTree = DocumentTree(self, document.id, self._controller)
        document_tree.setStyleSheet("background-color: #FFFFFF;")

        tab_layout.addWidget(document_tree)
        tab.setLayout(tab_layout)

        # Add tab to the dictionary with the document id as key
        self.tabs[document.id] = tab
        self.tab_children[document.id] = document_tree

        # Get acronym, add the tab and store the index given by the addTab method
        document_acronym: str = document.get_property("acronym").value
        if position is not None:
            tab_index = self.insertTab(position, tab, document_acronym)
        else:
            tab_index = self.addTab(tab, document_acronym)

        # Set the tab icon
        icon_path: Path = Config().get_icon(ACRONYM_ICON_TYPE, document_acronym)
        self.setTabIcon(tab_index, QIcon(icon_path.as_posix()))
        
    # ----------------------------------------------------------------------
    # Method     : delete_component
    # Description: Delete the component and its children components.
    # Date       : 09/08/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def delete_component(self) -> None:
        """
        Delete the component and its children components.
        Handle the detachment from the event manager.
        """
        # Detach from the event manager
        EventManager.detach(self)

        # Delete its children components
        for tab in self.tab_children.values():
            tab.delete_component()

        # Delete the component
        self.setParent(None)
        self.deleteLater()

        log.info("Documents container tab component deleted")

    # ======================================================================
    # Component update methods (triggered by PROTEUS application events)
    # ======================================================================

    # ----------------------------------------------------------------------
    # Method     : update_on_add_document
    # Description: Update the documents tab menu component when a new
    #              document is added to the project.
    # Date       : 06/06/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def update_on_add_document(self, *args, **kwargs) -> None:
        """
        Update the documents tab menu component when a new document is added
        to the project. It creates a new tab for the document using the add
        document method.

        Triggered by: Event.ADD_DOCUMENT
        """
        new_document: Object = kwargs.get("document")

        position: int = kwargs.get("position", None)

        # Check the document is instance of Object
        # Check the object is instance of Object
        assert isinstance(
            new_document, Object
        ), "Object is not instance of Object on ADD_DOCUMENT event"

        self.add_document(new_document, position=position)

    # ----------------------------------------------------------------------
    # Method     : update_on_delete_document
    # Description: Update the documents tab menu component when a document
    #              is deleted from the project.
    # Date       : 06/06/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def update_on_delete_document(self, *args, **kwargs) -> None:
        """
        Update the documents tab menu component when a document is deleted
        from the project. It deletes the tab from the tabs widget and
        deletes the child components.

        Triggered by: Event.DELETE_DOCUMENT
        """
        document_id: ProteusID = kwargs.get("element_id")

        # Check the element id is not None
        assert document_id is not None, "Element id is None on DELETE_OBJECT event"

        # Check there is a tab for the document
        assert (
            document_id in self.tabs
        ), f"Document tab not found for document {document_id} on DELETE_DOCUMENT event"

        # Delete tab from tabs widget
        document_tab: QWidget = self.tabs.pop(document_id)
        self.removeTab(self.indexOf(document_tab))

        # Delete child components
        child_component: DocumentTree = self.tab_children.pop(document_id)
        child_component.delete_component()

        # Delete tab object
        document_tab.parent = None
        document_tab.deleteLater()

    # ----------------------------------------------------------------------
    # Method     : update_on_modify_object
    # Description: Update the documents tab menu component when an object
    #              is modified.
    # Date       : 06/06/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def update_on_modify_object(self, *args, **kwargs) -> None:
        """
        Update the documents tab menu component when an object is modified.
        It changes the tab name with the new document name if the object
        modified is a document.

        Triggered by: Event.MODIFY_OBJECT
        """
        element_id: ProteusID = kwargs.get("element_id")

        # Check the element id is not None
        assert element_id is not None, "Element id is None on MODIFY_OBJECT event"

        # Check if exists a tab for the element
        if element_id in self.tabs:
            # Get document tab
            document_tab: QWidget = self.tabs.get(element_id)
            tab_index: int = self.indexOf(document_tab)

            # Get new acronym
            element: Object = self._controller.get_element(element_id)
            document_acronym: str = element.get_property("acronym").value
            self.setTabText(tab_index, document_acronym)

            # Get new icon
            icon_path: Path = Config().get_icon(ACRONYM_ICON_TYPE, document_acronym)
            self.setTabIcon(tab_index, QIcon(icon_path.as_posix()))
            

    # ======================================================================
    # Component slots methods (connected to the component signals)
    # ======================================================================

    # ----------------------------------------------------------------------
    # Method     : current_document_changed
    # Description: Slot triggered when the current document tab is changed.
    #              It updates the current document id in the state manager.
    # Date       : 06/06/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def current_document_changed(self, index: int) -> None:
        """
        Slot triggered when the current document tab is changed. It updates
        the current document id in the state manager.
        """
        # Get document id
        document_id: ProteusID = None
        if index >= 0:
            document_tab: QWidget = self.widget(index)
            # Get the document id (key) from the tab (value)
            document_id = list(self.tabs.keys())[
                list(self.tabs.values()).index(document_tab)
            ]

        # Update current document in the state manager
        StateManager.set_current_document(document_id)

    def tab_moved(self, new_index: int, old_index: int) -> None:
        # Get the current document id
        document_id: ProteusID = StateManager.get_current_document()

        # Get the project
        project = self._controller.get_current_project()

        log.debug(f"Moving document {document_id} from {old_index} to {new_index}")

        # Index adjusting to allow pop and insert without problems
        if new_index > old_index:
            new_index += 1

        self._controller.change_document_position(document_id, new_index)