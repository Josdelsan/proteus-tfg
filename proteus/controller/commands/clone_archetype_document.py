# ==========================================================================
# File: clone_archetype_document.py
# Description: Controller to clone an archetype document.
# Date: 03/06/2023
# Version: 0.1
# Author: José María Delgado Sánchez
# ==========================================================================

# --------------------------------------------------------------------------
# Standard library imports
# --------------------------------------------------------------------------

from typing import List

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
from proteus.services.archetype_service import ArchetypeService
from proteus.application.events import (
    AddDocumentEvent,
    DeleteDocumentEvent,
)

# --------------------------------------------------------------------------
# Class: CloneArchetypeDocumentCommand
# Description: Controller class to clone an archetype object.
# Date: 03/06/2023
# Version: 0.1
# Author: José María Delgado Sánchez
# --------------------------------------------------------------------------
class CloneArchetypeDocumentCommand(QUndoCommand):
    """
    Controller class to clone an archetype document.
    """

    # ----------------------------------------------------------------------
    # Method     : __init__
    # Description: Class constructor, invoke the parents class constructors.
    # Date       : 27/05/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def __init__(
        self,
        archetype_id: ProteusID,
        project_service: ProjectService,
        archetype_service: ArchetypeService,
    ):
        super(CloneArchetypeDocumentCommand, self).__init__()

        # Dependency injection
        assert isinstance(
            project_service, ProjectService
        ), "Must provide a project service instance to the command"
        assert isinstance(
            archetype_service, ArchetypeService
        ), "Must provide a archetype service instance to the command"
        self.project_service = project_service
        self.archetype_service = archetype_service

        # Command attributes
        self.archetype_id: ProteusID = archetype_id
        self.before_clone_parent_state: ProteusState = None
        self.after_clone_parent_state: ProteusState = None
        self.cloned_object: Object = None

    # ----------------------------------------------------------------------
    # Method     : redo
    # Description: Redo the command, cloning the archetype document.
    # Date       : 01/06/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def redo(self):
        """
        Redo the command, cloning the archetype document.
        """

        # NOTE: Must check if the operation was already performed once because
        #       cloning an object asigns a new ProteusID to the object, so if
        #       an edit operation is performed and undone we will not be able
        #       to redo if also undo is performed for the clone operation due
        #       to the ProteusID change.
        if self.cloned_object is None:
            # Set redo text
            self.setText(f"Clone archetype document {self.archetype_id}")

            # Get the parent and project object
            parent = self.project_service.project
            project = self.project_service.project

            # Save the parent state before clone
            self.before_clone_parent_state = parent.state

            # Clone the archetype object
            self.cloned_object = self.archetype_service.create_object(
                self.archetype_id, parent, project
            )

            # Save the parent state after clone
            self.after_clone_parent_state = parent.state
        else:
            # Set redo text
            self.setText(f"Mark as ALIVE cloned object {self.cloned_object.id}")

            # Change the state of the cloned object and his children to FRESH
            self.project_service.change_state(self.cloned_object.id, ProteusState.FRESH)

            # Set the parent state to the state after clone stored in the first redo
            parent = self.project_service.project
            parent.state = self.after_clone_parent_state

        # Emit the event to update the view
        AddDocumentEvent().notify(self.cloned_object.id)

    # ----------------------------------------------------------------------
    # Method     : undo
    # Description: Undo the command, deleting the cloned object.
    # Date       : 02/06/2023
    # Version    : 0.2
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def undo(self):
        """
        Undo the command, deleting the cloned document.
        """
        # Set undo text
        self.setText(f"Mark as DEAD cloned document {self.cloned_object.id}")

        # Change the state of the cloned object and his children to DEAD
        self.project_service.change_state(self.cloned_object.id, ProteusState.DEAD)

        # Set the parent state to the old state
        parent = self.project_service.project
        parent.state = self.before_clone_parent_state

        # Emit the event to update the view
        DeleteDocumentEvent().notify(self.cloned_object.id)