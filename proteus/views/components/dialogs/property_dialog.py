# ==========================================================================
# File: property_dialog.py
# Description: PyQT6 properties form component for the PROTEUS application
# Date: 26/05/2023
# Version: 0.1
# Author: José María Delgado Sánchez
# ==========================================================================

# --------------------------------------------------------------------------
# Standard library imports
# --------------------------------------------------------------------------

from typing import Union, List, Dict

# --------------------------------------------------------------------------
# Third-party library imports
# --------------------------------------------------------------------------

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QDialogButtonBox,
    QFormLayout,
    QDialog,
    QLineEdit,
    QDateEdit,
    QTextEdit,
    QCheckBox,
)


# --------------------------------------------------------------------------
# Project specific imports
# --------------------------------------------------------------------------

from proteus.model import ProteusID
from proteus.model.project import Project
from proteus.model.object import Object
from proteus.model.properties import Property
from proteus.views.utils.input_factory import PropertyInputFactory
from proteus.controller.command_stack import Controller


# --------------------------------------------------------------------------
# Class: PropertyForm
# Description: Class for the PROTEUS application properties form component.
# Date: 27/05/2023
# Version: 0.1
# Author: José María Delgado Sánchez
# --------------------------------------------------------------------------
class PropertyDialog(QDialog):
    """
    Class for the PROTEUS application properties form component. It is used
    to display the properties of an element in a form. Properties are
    grouped by categories in tabs. Each property is displayed in a widget
    that is created using the PropertyInputFactory class.
    """

    # ----------------------------------------------------------------------
    # Method     : __init__
    # Description: Class constructor, invoke the parents class constructors
    #              and create the component.
    # Date       : 27/05/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def __init__(self, element_id=None, *args, **kwargs) -> None:
        """
        Class constructor, invoke the parents class constructors and create
        the component. Store the element id, reference to the element whose
        properties will be displayed.
        """
        super().__init__(*args, **kwargs)

        # Set the element id, reference to the element whose properties
        # will be displayed
        self.element_id: ProteusID = element_id

        # Create a dictionary to hold the input widgets for each property
        # NOTE: This is used to get the input values when the form is
        #       accepted
        self.input_widgets: Dict[
            str, Union[QLineEdit, QDateEdit, QTextEdit, QCheckBox]
        ] = {}

        # Create the component
        self.create_component()

    # ----------------------------------------------------------------------
    # Method     : create_component
    # Description: Create the component.
    # Date       : 27/05/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def create_component(self) -> None:
        """
        Create the component.
        """
        self.object: Union[Project, Object] = Controller.get_element(self.element_id)

        # Set the window name
        window_name: str = self.object.get_property("name").value
        self.setWindowTitle(window_name)

        # Create the form vertical layout
        form_layout: QVBoxLayout = QVBoxLayout(self)

        # Create a QTabWidget to organize properties by categories
        tab_widget: QTabWidget = QTabWidget()

        # Get the object's properties dictionary
        properties_dict: Dict[str, Property] = self.object.properties

        # Create a dictionary to hold category widgets
        category_widgets: Dict[str, QWidget] = {}

        # Iterate over the properties and create widgets for each category
        prop: Property = None
        for prop in properties_dict.values():
            # Get the category for the property
            category: str = prop.category

            # Create a QWidget for the category if it doesn't exist
            if category not in category_widgets:
                category_widget: QWidget = QWidget()
                category_layout: QFormLayout = QFormLayout(category_widget)
                category_widgets[category] = category_widget
            else:
                category_widget: QWidget = category_widgets[category]
                category_layout: QFormLayout = category_widget.layout()

            # Create the property input widget
            input_field_widget: Union[
                QLineEdit, QDateEdit, QTextEdit, QCheckBox
            ] = PropertyInputFactory.create(prop)
            category_layout.addRow(f"{prop.name}:", input_field_widget)

            # Add the input field widget to the input widgets dictionary
            # NOTE: This is used to retrieve the values of the widgets that changed
            self.input_widgets[prop.name] = input_field_widget

        # Add the category widgets as tabs in the tab widget
        category: str = None
        category_widget: QWidget = None
        for category, category_widget in category_widgets.items():
            tab_widget.addTab(category_widget, category)

        # Add the tab widget to the main form layout
        form_layout.addWidget(tab_widget)

        # Create Save and Cancel buttons
        button_box: QDialogButtonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_button_clicked)
        button_box.rejected.connect(self.cancel_button_clicked)
        form_layout.addWidget(button_box)

        self.setLayout(form_layout)

    # ======================================================================
    # Dialog slots methods (connected to the component signals)
    # ======================================================================

    # ----------------------------------------------------------------------
    # Method     : save_button_clicked
    # Description: Manage the save button clicked event. It gets the values
    #              of the input widgets and updates the properties of the
    #              element.
    # Date       : 27/05/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def save_button_clicked(self):
        """
        Manage the save button clicked event. It gets the values of the
        input widgets and updates the properties of the element.
        """
        # Empty dictionary to hold the properties to update
        update_list: List[Property] = []

        # Get the original object properties dictionary
        properties_dict = self.object.properties

        # Iterate over the input widgets and update the properties dictionary
        for prop_name in properties_dict.keys():
            # Get the property input value
            input_widget: Union[
                QLineEdit, QDateEdit, QTextEdit, QCheckBox
            ] = self.input_widgets[prop_name]

            new_prop_value: str = PropertyInputFactory.widget_to_value(input_widget)

            # Get the original property and its value
            original_prop: Property = properties_dict[prop_name]
            original_prop_value: str = original_prop.value

            # If the values are different, clone the original property with the new value
            if new_prop_value != original_prop_value:
                cloned_property: Property = original_prop.clone(new_prop_value)
                update_list.append(cloned_property)

        # Update the properties of the element if there are changes
        if len(update_list) > 0:
            Controller.update_properties(self.element_id, update_list)

        # Close the form window
        self.close()
        self.deleteLater()

    # ----------------------------------------------------------------------
    # Method     : cancel_button_clicked
    # Description: Manage the cancel button clicked event. It closes the
    #              form window without saving any changes.
    # Date       : 27/05/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def cancel_button_clicked(self):
        """
        Manage the cancel button clicked event. It closes the form window
        without saving any changes.
        """
        # Close the form window without saving any changes
        self.close()
        self.deleteLater()

    # ======================================================================
    # Dialog static methods (create and show the form window)
    # ======================================================================

    # ----------------------------------------------------------------------
    # Method     : object_property_dialog (static)
    # Description: Handle the creation and display of the form window.
    # Date       : 05/06/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    @staticmethod
    def object_property_dialog(element_id: ProteusID):
        """
        Handle the creation and display of the form window.

        :param element_id: The id of the element to edit.
        """
        # Create the form window
        form_window = PropertyDialog(element_id)

        # Show the form window
        form_window.exec()

    # ----------------------------------------------------------------------
    # Method     : project_property_dialog (static)
    # Description: Handle the creation and display of the form window.
    # Date       : 05/06/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    @staticmethod
    def project_property_dialog():
        """
        Handle the creation and display of the form window.
        """
        current_project_id: ProteusID = Controller.get_current_project().id

        # Create the form window
        form_window = PropertyDialog(current_project_id)

        # Show the form window
        form_window.exec()