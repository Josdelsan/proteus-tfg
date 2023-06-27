# ==========================================================================
# File: main_menu.py
# Description: PyQT6 main menubar for the PROTEUS application
# Date: 01/06/2023
# Version: 0.2
# Author: José María Delgado Sánchez
# ==========================================================================

# --------------------------------------------------------------------------
# Standard library imports
# --------------------------------------------------------------------------

from typing import List, Dict

# --------------------------------------------------------------------------
# Third-party library imports
# --------------------------------------------------------------------------

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QTabWidget,
    QDockWidget,
    QToolButton,
    QFileDialog,
    QMessageBox,
)

# --------------------------------------------------------------------------
# Project specific imports
# --------------------------------------------------------------------------

import proteus
from proteus.model import PROTEUS_ANY, ProteusID
from proteus.model.object import Object
from proteus.views.components.dialogs.new_project_dialog import NewProjectDialog
from proteus.views.components.dialogs.property_dialog import PropertyDialog
from proteus.views.components.dialogs.new_document_dialog import NewDocumentDialog
from proteus.views.components.dialogs.settings_dialog import SettingsDialog
from proteus.views.utils import buttons
from proteus.views.utils.buttons import ArchetypeMenuButton
from proteus.views.utils.event_manager import Event, EventManager
from proteus.views.utils.state_manager import StateManager
from proteus.views.utils.translator import Translator
from proteus.controller.command_stack import Controller


# --------------------------------------------------------------------------
# Class: MainMenu
# Description: PyQT6 main menu class for the PROTEUS application
# Date: 01/06/2023
# Version: 0.2
# Author: José María Delgado Sánchez
# --------------------------------------------------------------------------
class MainMenu(QDockWidget):
    """
    Main menu component for the PROTEUS application. It is used to
    display the main option tab and object archetypes separated by
    classes separated by tabs.
    """

    # ----------------------------------------------------------------------
    # Method     : __init__
    # Description: Class constructor, invoke the parents class constructors
    #              and create the component.
    # Date       : 29/05/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def __init__(self, parent=None, *args, **kwargs) -> None:
        """
        Class constructor, invoke the parents class constructors, create
        the component and connect update methods to the events.

        Manage the creation of the instace variables to store updatable
        buttons (save, undo, redo, etc.) and the tab widget to display the
        different menus.
        """
        super().__init__(parent, *args, **kwargs)

        # Get translator instance
        self.translator = Translator()

        # Main menu buttons that are updated
        self.save_button: QToolButton = None
        self.undo_button: QToolButton = None
        self.redo_button: QToolButton = None
        self.project_properties_button: QToolButton = None
        self.add_document_button: QToolButton = None
        self.delete_document_button: QToolButton = None

        # Archetype menu buttons that are updated
        self.archetype_buttons: Dict[ProteusID, ArchetypeMenuButton] = {}

        # Tab widget to display app menus in different tabs
        self.tab_widget: QTabWidget = QTabWidget()

        # Create the component
        self.create_component()

        # Subscribe to events
        EventManager.attach(Event.STACK_CHANGED, self.update_on_stack_changed, self)
        EventManager.attach(Event.SELECT_OBJECT, self.update_on_select_object, self)
        EventManager.attach(Event.OPEN_PROJECT, self.update_on_open_project, self)
        EventManager.attach(
            Event.CURRENT_DOCUMENT_CHANGED,
            self.update_on_current_document_changed,
            self,
        )

    # ----------------------------------------------------------------------
    # Method     : create_component
    # Description: Create the object main tab menu component
    # Date       : 29/05/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def create_component(self) -> None:
        """
        Create the object archetype tab menu component. It creates a tab for
        each class of object archetypes and a main tab for the main menu.
        """

        # ------------------
        # Component settings
        # ------------------
        # Remove the tittle bar and set fixed height to prevent resizing
        self.setTitleBarWidget(QWidget())
        self.setFixedHeight(125)

        # --------------------
        # Create the component
        # --------------------
        # Add the main tab
        self.add_main_tab(self.translator.text("main_menu.tab.home.name"))

        # Get the object archetypes
        object_archetypes_dict: Dict[
            str, List[Object]
        ] = Controller.get_object_archetypes()
        # Create a tab for each class of object archetypes
        for class_name in object_archetypes_dict.keys():
            self.add_archetype_tab(class_name, object_archetypes_dict[class_name])

        # Set the tab widget as the main widget of the component
        self.setWidget(self.tab_widget)

        proteus.logger.info("Main menu component created")

    # ----------------------------------------------------------------------
    # Method     : add_main_tab
    # Description: Add the main tab to the tab widget.
    # Date       : 01/06/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def add_main_tab(self, tab_name: str) -> None:
        """
        Create the main menu tab and add it to the tab widget. It displays
        the main menu buttons of the PROTEUS application.
        """
        # Create the tab widget with a horizontal layout
        main_tab: QWidget = QWidget()
        tab_layout: QHBoxLayout = QHBoxLayout()

        # ---------
        # Project menu
        # ---------
        # New action
        new_button: QToolButton = buttons.new_project_button(self)
        new_button.clicked.connect(NewProjectDialog.create_dialog)

        # Open action
        open_button: QToolButton = buttons.open_project_button(self)
        open_button.clicked.connect(self.open_project)

        # Save action
        self.save_button: QToolButton = buttons.save_project_button(self)
        self.save_button.clicked.connect(Controller.save_project)

        # Project properties action
        self.project_properties_button: QToolButton = buttons.project_properties_button(
            self
        )
        self.project_properties_button.clicked.connect(
            PropertyDialog.project_property_dialog
        )

        # Add the buttons to the project menu widget
        project_menu: QWidget = buttons.button_group(
            "main_menu.button_group.project",
            [new_button, open_button, self.save_button, self.project_properties_button],
        )
        tab_layout.addWidget(project_menu)

        # ---------
        # Document menu
        # ---------
        # Add document action
        self.add_document_button: QToolButton = buttons.add_document_button(self)
        self.add_document_button.clicked.connect(NewDocumentDialog.create_dialog)

        # Delete document action
        self.delete_document_button: QToolButton = buttons.delete_document_button(self)
        self.delete_document_button.clicked.connect(self.delete_current_document)

        # Add the buttons to the document menu widget
        document_menu: QWidget = buttons.button_group(
            "main_menu.button_group.document",
            [self.add_document_button, self.delete_document_button],
        )
        tab_layout.addWidget(document_menu)

        # ---------
        # Action menu
        # ---------
        # Undo action
        self.undo_button: QToolButton = buttons.undo_button(self)
        self.undo_button.clicked.connect(Controller.undo)

        # Redo action
        self.redo_button: QToolButton = buttons.redo_button(self)
        self.redo_button.clicked.connect(Controller.redo)

        # Add the buttons to the action menu widget
        action_menu: QWidget = buttons.button_group(
            "main_menu.button_group.action",
            [self.undo_button, self.redo_button],
        )
        tab_layout.addWidget(action_menu)

        # ---------
        # Settings
        # ---------
        # Settings action
        self.settings_button: QToolButton = buttons.settings_button(self)
        self.settings_button.clicked.connect(SettingsDialog.create_dialog)

        # Add the buttons to the settings menu widget
        settings_menu: QWidget = buttons.button_group(
            "main_menu.button_group.settings",
            [self.settings_button],
        )

        tab_layout.addWidget(settings_menu)

        # ---------------------------------------------

        # Spacer to justify content left
        tab_layout.addStretch()

        # Add the main tab widget to the tab widget
        main_tab.setLayout(tab_layout)
        self.tab_widget.addTab(main_tab, tab_name)

    # ----------------------------------------------------------------------
    # Method     : add_archetype_tab
    # Description: Add a tab to the tab widget for a given class of object
    #              archetypes.
    # Date       : 29/05/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def add_archetype_tab(
        self, class_name: str, object_archetypes: List[Object]
    ) -> None:
        """
        Add a tab to the tab widget for a given class of object archetypes.
        """
        # Create the tab widget with a horizontal layout
        tab_widget: QWidget = QWidget()
        tab_layout: QHBoxLayout = QHBoxLayout()

        # Create a list to store archetype buttons to create the group
        buttons_list: List[ArchetypeMenuButton] = []

        # Add the archetype widgets to the tab widget
        archetype: Object = None
        for archetype in object_archetypes:
            # Create the archetype button
            archetype_button: ArchetypeMenuButton = ArchetypeMenuButton(self, archetype)

            # Add the archetype button to the archetype buttons dictionary
            self.archetype_buttons[archetype.id] = archetype_button

            # Connect the clicked signal to the clone archetype method
            archetype_button.clicked.connect(
                lambda checked, arg=archetype.id: Controller.create_object(
                    archetype_id=arg, parent_id=StateManager.get_current_object()
                )
            )

            # Add the archetype button to the buttons list
            buttons_list.append(archetype_button)

        # Create text code for button group and bar names
        # NOTE: This is part of the internationalization system. The text
        #       code is used to retrieve the text from the translation files.
        #       This has to be dynamic because archetype tabs are created
        #       dynamically.
        tab_name_code: str = f"main_menu.tab.{class_name}.name"
        group_name_code: str = f"main_menu.button_group.archetypes.{class_name}"

        # Create the archetype button group
        archetype_menu: QWidget = buttons.button_group(group_name_code, buttons_list)
        tab_layout.addWidget(archetype_menu)

        # Spacer to justify content left
        tab_layout.addStretch()

        # Set the tab widget layout as the main widget of the tab widget
        tab_widget.setLayout(tab_layout)
        self.tab_widget.addTab(tab_widget, self.translator.text(tab_name_code))

    # ======================================================================
    # Component update methods (triggered by PROTEUS application events)
    # ======================================================================

    # ----------------------------------------------------------------------
    # Method     : update_on_stack_changed
    # Description: Update the state of save, undo and redo buttons when the
    #              command stack changes.
    # Date       : 06/06/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def update_on_stack_changed(self, *args, **kwargs) -> None:
        """
        Update the state of save, undo and redo buttons when the command
        stack changes, enabling or disabling them depending on the state.

        Triggered by: Event.STACK_CHANGED
        """
        can_undo: bool = Controller._get_instance().canUndo()
        can_redo: bool = Controller._get_instance().canRedo()
        unsaved_changes: bool = not Controller._get_instance().isClean()

        self.undo_button.setEnabled(can_undo)
        self.redo_button.setEnabled(can_redo)
        self.save_button.setEnabled(unsaved_changes)

    # ----------------------------------------------------------------------
    # Method     : update_on_select_object
    # Description: Update the state of the archetype buttons when an object
    #              is selected.
    # Date       : 06/06/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def update_on_select_object(self, *args, **kwargs) -> None:
        """
        Update the state of the archetype buttons when an object is
        selected, enabling or disabling them depending on the accepted
        children of the selected object.

        Triggered by: Event.SELECT_OBJECT
        """
        # Get the selected object id and check if it is None
        selected_object_id: ProteusID = StateManager.get_current_object()

        # If the selected object is None, disable all the archetype buttons
        if selected_object_id is None:
            button: ArchetypeMenuButton = None
            for button in self.archetype_buttons.values():
                button.setEnabled(False)

        # If the selected object is not None, enable the archetype buttons
        # that are accepted children of the selected object
        else:
            # Get the selected object and its accepted children
            selected_object: Object = Controller.get_element(selected_object_id)
            accepted_children: str = selected_object.acceptedChildren.split()

            # Iterate over the archetype buttons
            for archetype_id in self.archetype_buttons.keys():
                # Get the archetype button
                archetype_button: ArchetypeMenuButton = self.archetype_buttons[
                    archetype_id
                ]

                # Get the archetype
                archetype: Object = Controller.get_archetype_by_id(archetype_id)

                assert (
                    type(archetype) is Object
                ), f"Archetype {archetype_id} is not an object"

                # Get the archetype class (last class in the class hierarchy)
                archetype_class: str = archetype.classes.split()[-1]

                # Enable or disable the archetype button
                archetype_button.setEnabled(
                    archetype_class in accepted_children
                    or PROTEUS_ANY in accepted_children
                )

    # ----------------------------------------------------------------------
    # Method     : update_on_open_project
    # Description: Enable the project properties and add document buttons
    #              when a project is opened.
    # Date       : 06/06/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def update_on_open_project(self, *args, **kwargs) -> None:
        """
        Enable the project properties and add document buttons when a
        project is opened.

        Triggered by: Event.OPEN_PROJECT
        """
        self.project_properties_button.setEnabled(True)
        self.add_document_button.setEnabled(True)

    # ----------------------------------------------------------------------
    # Method     : update_on_current_document_changed
    # Description: Update the state of the document buttons when the
    #              current document changes.
    # Date       : 06/06/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def update_on_current_document_changed(self, *args, **kwargs) -> None:
        """
        Update the state of the document buttons when the current document
        changes, enabling or disabling them depending on the state.

        Triggered by: Event.CURRENT_DOCUMENT_CHANGED
        """
        document_id: ProteusID = kwargs["document_id"]

        # Store if there is a document open
        is_document_open: bool = document_id is not None

        self.delete_document_button.setEnabled(is_document_open)

    # ======================================================================
    # Component slots methods (connected to the component signals)
    # ======================================================================

    # ----------------------------------------------------------------------
    # Method     : open_project
    # Description: Manage the open project action, open a project using a
    #              file dialog and loads it.
    # Date       : 16/05/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    # TODO: Consider moving this dialog to a separate class
    def open_project(self):
        """
        Manage the open project action, open a project using a file dialog
        and loads it.
        """
        # Open the file dialog
        directory_dialog: QFileDialog = QFileDialog(self)
        directory_path: str = directory_dialog.getExistingDirectory(
            None, self.translator.text("main_menu.open_project.caption"), ""
        )

        # Load the project from the selected directory
        if directory_path:
            try:
                Controller.load_project(project_path=directory_path)
            except Exception as e:
                proteus.logger.error(e)

                # Show an error message dialog
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Icon.Critical)
                error_dialog.setWindowTitle(
                    self.translator.text("main_menu.open_project.error.title")
                )
                error_dialog.setText(
                    self.translator.text("main_menu.open_project.error.text")
                )
                error_dialog.setInformativeText(str(e))
                error_dialog.exec()

    # ----------------------------------------------------------------------
    # Method     : delete_current_document
    # Description: Manage the delete current document action, delete the
    #              current document.
    # Date       : 06/06/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def delete_current_document(self):
        """
        Manage the delete current document action, delete the current
        document. Use a confirmation dialog to confirm the action.
        """
        # Get the current document
        document_id: ProteusID = StateManager.get_current_document()
        document: Object = Controller.get_element(document_id)
        document_name: str = document.get_property("name").value

        # Show a confirmation dialog
        confirmation_dialog = QMessageBox()
        confirmation_dialog.setIcon(QMessageBox.Icon.Warning)
        confirmation_dialog.setWindowTitle(
            self.translator.text("main_menu.delete_document.title")
        )
        confirmation_dialog.setText(
            self.translator.text("main_menu.delete_document.text", document_name)
        )
        confirmation_dialog.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        confirmation_dialog.setDefaultButton(QMessageBox.StandardButton.No)
        confirmation_dialog.accepted.connect(
            # Delete the document
            lambda arg=document.id: Controller.delete_document(arg)
        )
        confirmation_dialog.exec()
