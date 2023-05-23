# ==========================================================================
# File: project.py
# Description: a PROTEUS project
# Date: 07/08/2022
# Version: 0.2
# Author: Amador Durán Toro
# ==========================================================================
# Update: 15/09/2022 (Amador)
# Description:
# - Project now inherits from AbstractObject
# ==========================================================================
# Update: 15/04/2023 (José María)
# Description:
# - Project now lazy loads its documents.
#   Project now has a method to clone itself into a new directory.
# ==========================================================================

# for using classes as return type hints in methods
# (this will change in Python 3.11)
from __future__ import annotations # it has to be the first import

# --------------------------------------------------------------------------
# Standard library imports
# --------------------------------------------------------------------------
import os
import pathlib
import shutil
import logging
from typing import List

# --------------------------------------------------------------------------
# Third-party library imports
# --------------------------------------------------------------------------

import lxml.etree as ET

# --------------------------------------------------------------------------
# Project specific imports (starting from root)
# --------------------------------------------------------------------------
from proteus.model import DOCUMENT_TAG, DOCUMENTS_TAG, OBJECTS_REPOSITORY, PROJECT_TAG, ProteusID, PROJECT_FILE_NAME, PROTEUS_DOCUMENT
from proteus.model.abstract_object import AbstractObject, ProteusState
#if 'proteus.model.object' in sys.modules:
#    from proteus.model.object import Object
from proteus.model.object import Object

# logging configuration
log = logging.getLogger(__name__)

# --------------------------------------------------------------------------
# Class: Project
# Description: Class for PROTEUS projects
# Date: 07/08/2022
# Version: 0.2
# Author: Amador Durán Toro
# --------------------------------------------------------------------------

class Project(AbstractObject):
    """
    A PROTEUS project is a 'proteus.xml' file inside a directory with 'objects'
    and 'assets' directories. The 'proteus.xml' must describe the projects
    properties and the short UUIDs of their documents (which are PROTEUS objects
    of with class tag ':Proteus-Document'.

    A PROTEUS project can only be created by cloning another existing project,
    usually an archetype project.

    An already created project can be loaded by providing the path to its
    directory.
    """
    # ----------------------------------------------------------------------
    # Method: load (static)
    # Description: It loads a PROTEUS project from disk into memory
    # Date: 22/08/2022
    # Version: 0.1
    # Author: Amador Durán Toro
    # ----------------------------------------------------------------------

    @staticmethod
    def load(path: str) -> Project:
        """
        Static factory method for loading a PROTEUS project from a given path.
        
        :param path: path to the project file.
        :return: a PROTEUS project.
        """
        log.info(f"Loading a PROTEUS project from {path}.")

        # Check path is a directory
        assert os.path.isdir(path), \
            f"PROTEUS projects must be located in a directory. {path} is not a directory."

        # Change the current working directory
        os.chdir(path)

        # Complete path to project file
        project_file_path = f"./{PROJECT_FILE_NAME}"

        # Check project file exists
        assert os.path.isfile(project_file_path), \
            f"PROTEUS project file {project_file_path} not found in {path}."

        # Create and return the project object
        return Project(project_file_path)

    # ----------------------------------------------------------------------
    # Method     : __init__
    # Description: It initializes a PROTEUS project and builds it using an
    #              XML file.
    # Date       : 22/08/2022
    # Version    : 0.2
    # Author     : Amador Durán Toro
    # ----------------------------------------------------------------------

    def __init__(self, project_file_path: str) -> None:
        """
        It initializes and builds a PROTEUS project from an XML file.
        
        :param project_file_path: path to the project file.
        """

        # Initialize property dictionary in superclass
        # TODO: pass some arguments?
        super().__init__(project_file_path)

        # Save the project path as a project's attribute
        # TODO: probably this can be factored up to superclass
        self.path = project_file_path

        # Parse and load XML into memory
        root : ET.Element = ET.parse( project_file_path ).getroot()

        # Check root tag is <project>
        assert root.tag == PROJECT_TAG, \
            f"PROTUES project file {project_file_path} must have <{PROJECT_TAG}> as root element, not {root.tag}."

        # Get project ID from XML
        self.id = ProteusID(root.attrib['id'])

        # Load project's properties using superclass method
        super().load_properties(root)

        # Documents dictionary
        self._documents : List[Object] = None

    # ----------------------------------------------------------------------
    # Property   : documents
    # Description: Property documents getter. Loads children from XML file
    #              on demand.
    # Date       : 12/04/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    @property
    def documents(self) -> List[Object]:
        """
        Property documents getter. Loads documents from XML file on demand.
        :return: documents dictionary.
        """
        # Check if documents dictionary is not initialized
        if self._documents is None:
            # Initialize documents dictionary
            self._documents : List[Object] = []

            # Load documents from XML file
            self.load_documents()

        # Return documents dictionary
        return self._documents
    

    # ----------------------------------------------------------------------
    # Method     : load_documents
    # Description: It loads the documents of a PROTEUS project using an
    #              XML root element <project>.
    # Date       : 22/08/2022
    # Version    : 0.1
    # Author     : Amador Durán Toro
    # ----------------------------------------------------------------------

    def load_documents(self) -> None:
        """
        It loads a PROTEUS project's documents from an XML root element.
        :param root: XML root element.
        """
        # Parse and load XML into memory
        root : ET.Element = ET.parse( self.path ).getroot()

        # Check root is not None
        assert root is not None, \
            f"Root element is not valid in {self.path}."

        # Load documents
        documents_element : ET.Element = root.find(DOCUMENTS_TAG)

        # Check whether it has documents
        assert documents_element is not None, \
            f"PROTEUS project file {self.path} does not have a <{DOCUMENTS_TAG}> element."

        # Parse project's documents
        # TODO: check document_element tag is <document>
        document_element : ET.Element
        for document_element in documents_element:
            document_id : ProteusID = document_element.attrib.get('id', None)

            # Check whether the document has an ID
            assert document_id is not None, \
                f"PROTEUS project file {self.path} includes a document without ID."

            # Add the document to the documents dictionary and set the parent
            object = Object.load(document_id, self)
            object.parent = self
            self.documents.append(object)

    # ----------------------------------------------------------------------
    # Method     : get_descendants
    # Description: It returns a list with all the documents of a project.
    # Date       : 23/05/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def get_descendants(self) -> List:
        """
        It returns a list with all the documents of a project.
        :return: list with all the documents of a project.
        """
        # Return the list with all the descendants of an object
        return self.documents

    # ----------------------------------------------------------------------
    # Method     : add_descendants
    # Description: Adds a document to the project given a document and its
    #              position.
    # Date       : 26/04/2023
    # Version    : 0.2
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------

    def add_descendant(self, document: Object, position: int = None) -> None:
        """
        Method that adds a document to the project.
        
        :param document: Document to be added to the project.
        :param position: Position of the document in the project.
        """

        # If position is not specified, add the document at the end
        if position is None:
            position = len(self.documents)

        # Check if the document is a valid object
        assert isinstance(document, Object), \
            f"Document {document} is not a valid PROTEUS object."

        # Check if the document is already in the project
        assert PROTEUS_DOCUMENT in  document.classes, \
            f"The object is not a Proteus document. Object is class: {document.classes}"
        
        # Check if the document is already in the project
        assert document.id not in [o.id for o in self.documents], \
            f"Document {document.id} is already in the project {self.id}."

        # Add the document to the project
        self.documents.insert(position, document)
        document.parent = self

    # ----------------------------------------------------------------------
    # Method     : generate_xml
    # Description: It generates an XML element for the project.
    # Date       : 26/08/2022
    # Version    : 0.1
    # Author     : Amador Durán Toro
    # ----------------------------------------------------------------------

    def generate_xml(self) -> ET.Element:
        """
        It generates an XML element for the project.
        :return: an XML element for the project.
        """
        # Create <project> element and set ID
        project_element = ET.Element(PROJECT_TAG)
        project_element.set('id', self.id)

        # Create <properties> element
        super().generate_xml_properties(project_element)

        # Create <documents> element
        documents_element = ET.SubElement(project_element, DOCUMENTS_TAG)

        # Create <document> subelements
        for document in self.documents:
            if(document.state != ProteusState.DEAD):
                document_element = ET.SubElement(documents_element, DOCUMENT_TAG)
                document_element.set('id', document.id)

        return project_element

    # ----------------------------------------------------------------------
    # Method     : save_project
    # Description: It saves a project in the system.
    # Date       : 01/05/2023
    # Version    : 0.2
    # Author     : Pablo Rivera Jiménez
    #              José María Delgado Sánchez
    # ----------------------------------------------------------------------

    def save_project(self) -> None:
        """
        It saves a project in the system.
        """
        # Save all the documents
        documents = list(self.documents)
        for document in documents:
            document.save()

        # Persist the project only if it is DIRTY or FRESH
        if(self.state == ProteusState.DIRTY or self.state == ProteusState.FRESH):
            root = self.generate_xml()

            # Get the elementTree, save it in the project path and set state to clean
            tree = ET.ElementTree(root)
            tree.write(self.path, pretty_print=True, xml_declaration=True, encoding="utf-8")
            self.state = ProteusState.CLEAN

        
    # ----------------------------------------------------------------------
    # Method     : clone_project
    # Description: It clones a project into the selected system path.
    # Date       : 13/04/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez  
    # ----------------------------------------------------------------------
    
    def clone_project(self, filename_path_to_save: str, new_project_dir_name: str) -> Project:
        """
        Method that creates a new project from an existing project.
        
        :param filename: Path where we want to save the project.
        :param new_project_dir_name: Name of the new project directory.
        :return: The new project.
        """
        assert os.path.isdir(filename_path_to_save), \
            f"The given path is not a directory: {filename_path_to_save}"
        
        # Directory where we save the project
        target_dir = pathlib.Path(filename_path_to_save).resolve() / new_project_dir_name
        
        # Directory where the project is located
        project_dir = pathlib.Path(self.path).parent.resolve()

        # Check the objects directory and the project file exists (or project archetype file)
        assert os.path.isdir(project_dir / OBJECTS_REPOSITORY), \
            f"The objects directory does not exist: {project_dir / OBJECTS_REPOSITORY}"
        assert os.path.isfile(project_dir / PROJECT_FILE_NAME) \
            or os.path.isfile(project_dir / "project.xml"),    \
            f"The project file does not exist in {project_dir}"
        
        shutil.copytree(project_dir, target_dir)

        # Check if the project is an archetype then change the project file
        project_arquetype_file = target_dir / "project.xml"
        if os.path.isfile(project_arquetype_file):
            project_file = target_dir / PROJECT_FILE_NAME
            os.rename(project_arquetype_file, project_file)

        # Load the new project and return it
        return Project.load(target_dir)
    
    
    