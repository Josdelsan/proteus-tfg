# ==========================================================================
# File: delete_object.py
# Description: Controller to delete an object.
# Date: 03/06/2023
# Version: 0.1
# Author: José María Delgado Sánchez
# ==========================================================================

# --------------------------------------------------------------------------
# Standard library imports
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Third-party library imports
# --------------------------------------------------------------------------

from PyQt6.QtGui import QUndoCommand

# --------------------------------------------------------------------------
# Project specific imports (starting from root)
# --------------------------------------------------------------------------

from proteus.model import ProteusID
from proteus.model.object import Object
from proteus.model.abstract_object import ProteusState
from proteus.services.project_service import ProjectService
from proteus.views.utils.event_manager import EventManager, Event
from proteus.views.utils.state_manager import StateManager


# --------------------------------------------------------------------------
# Class: DeleteObjectCommand
# Description: Controller class delete an object.
# Date: 03/06/2023
# Version: 0.1
# Author: José María Delgado Sánchez
# --------------------------------------------------------------------------
class DeleteObjectCommand(QUndoCommand):
    """
    Controller class to delete an object.
    """

    # ----------------------------------------------------------------------
    # Method     : __init__
    # Description: Class constructor, invoke the parents class constructors.
    # Date       : 03/06/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def __init__(self, object_id: ProteusID, project_service: ProjectService):
        super(DeleteObjectCommand, self).__init__()

        # Dependency injection
        assert isinstance(
            project_service, ProjectService
        ), "Must provide a project service instance to the command"
        self.project_service = project_service

        # Command attributes
        self.before_clone_parent_state: ProteusState = None
        self.object: Object = self.project_service._get_element_by_id(object_id)
        self.old_object_state: ProteusState = self.object.state

    # ----------------------------------------------------------------------
    # Method     : redo
    # Description: Redo the command, deleting the object.
    # Date       : 03/06/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def redo(self):
        """
        Redo the command, deleting the object.
        """
        # Set redo text
        self.setText(f"Mark as DEAD object {self.object.id}")

        # Change the state of the cloned object and his children to FRESH
        self.project_service.change_state(self.object.id, ProteusState.DEAD)

        # Modify the parent state depending on its current state
        self.before_clone_parent_state = self.object.parent.state

        if self.before_clone_parent_state is ProteusState.CLEAN:
            after_clone_parent_state = ProteusState.DIRTY
        else:
            after_clone_parent_state = self.before_clone_parent_state

        self.object.parent.state = after_clone_parent_state

        # Deselect the object in case it was selected to avoid errors
        StateManager.deselect_object(self.object.id)

        # Emit the event to update the view
        EventManager.notify(Event.DELETE_OBJECT, element_id=self.object.id)

    # ----------------------------------------------------------------------
    # Method     : undo
    # Description: Undo the command, marking the object with its previous
    #              state.
    # Date       : 03/06/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def undo(self):
        """
        Undo the command, marking the object with its previous state.
        """
        # Set undo text
        self.setText(f"Revert delete object {self.object.id}")

        # Change the state of the cloned object and his children to the old state
        self.project_service.change_state(self.object.id, self.old_object_state)

        # Set the parent state to the old state
        self.object.parent.state = self.before_clone_parent_state

        # Emit the event to update the view
        EventManager.notify(Event.ADD_OBJECT, object=self.object)
