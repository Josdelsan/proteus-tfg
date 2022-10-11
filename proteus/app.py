# ==========================================================================
# File: app.py
# Description: the PROTEUS application
# Date: 09/10/2022
# Version: 0.1
# Author: Amador Durán Toro
# ==========================================================================

# --------------------------------------------------------------------------
# Standard library imports
# --------------------------------------------------------------------------

from pathlib import Path

# --------------------------------------------------------------------------
# Project specific imports
# --------------------------------------------------------------------------

import proteus
import lxml.etree as ET
from proteus.config import Config
from proteus.model.project import Project
from proteus.model.object import Object
from proteus.model.archetype_manager import ArchetypeManager
from proteus.model.archetype_proxys import DocumentArchetypeProxy, ProjectArchetypeProxy
from proteus.model.property import EnumProperty, Property, StringProperty

# --------------------------------------------------------------------------
# Class: ProteusApplication
# Description: Class for the PROTEUS application
# Date: 09/10/2022
# Version: 0.1
# Author: Amador Durán Toro
# --------------------------------------------------------------------------
# TODO: this should be a Qt application in the future
# --------------------------------------------------------------------------

class ProteusApplication:
    def __init__(self):
        """
        It initializes the PROTEUS application.
        """
        self.config : Config = Config()

    def run(self) -> int:
        """
        PROTEUS application main method.
        """

        proteus.logger.info(f"Current working directory: {Path.cwd()}")
        proteus.logger.info(f"Home directory: {Path.home()}")
        proteus.logger.info(f"{Path(__file__) = }")

        proteus.logger.info(f"{self.config.resources_directory = }")
        proteus.logger.info(f"{self.config.icons_directory = }")
        proteus.logger.info(f"{self.config.archetypes_directory = }")
        self._old_main_tests()
        return 0

    def _old_main_tests(self):
        project : Project = Project.load(self.config.base_directory / "tests" / "project")

        property : Property
        for property in project.properties.values():
            print( f"{property.__class__.__name__} {property.name} = {property.value}" )

        document : Object
        for document in project.documents.values():
            print( f"document {document.id=}" )

        print("project.xml")
        print("------------")

        print( ET.tostring(project.generate_xml(),
            xml_declaration=True,
            encoding='utf-8',
            pretty_print=True).decode() )

        for document in project.documents.values():
            print(f"{document.id}.xml")
            print("------------------")
            print( ET.tostring(document.generate_xml(),
                xml_declaration=True,
                encoding='utf-8',
                pretty_print=True).decode() )

            print("Document Properties Tests")
            print("------------")

            print(document.get_property("name").value)

            document.set_property(StringProperty("name", "NewName"))

            print(document.get_property("name").value)
            print("------------")

        print("Project Properties Tests")
        print("------------------------")

        enum_property : EnumProperty = project.get_property("stability")

        print(f"{enum_property.value=}")

        project.set_property(EnumProperty(enum_property.name, "baja", enum_property.get_choices_as_str()))

        print(project.get_property("stability").value)

        print("Archetype Object Test")
        print("------------------------")
        print(ArchetypeManager.load_object_archetypes())

        print("Archetype Document Test")
        print("------------------------")
        documents = DocumentArchetypeProxy.load()
        for document in documents:
            print(document.path, "\n", document.id, "\n", document.name, "\n", document.description)

        print("Archetype Project Test")
        print("------------------------")
        projects = ProjectArchetypeProxy.load()
        for project_arch in projects:
            print(project_arch.path, "\n", project_arch.id, "\n", project_arch.name, "\n", project_arch.description)

        # project.clone_project("../../clone_test/" + ArchetypeManager.load_project_archetypes()[1][1], ArchetypeManager.load_project_archetypes()[1][0])
        # project.state = ProteusState.DEAD
        
        
        object2 = Object(project, self.config.archetypes_directory / "objects" / "general" / "empty-section.xml")
        object2.clone_object(project)



        # BUG this won't work because the pointer is different from document.children 
        # object1 = Object(project, "../../proteus/tests/objects/64xM8FLyxtaE.xml")
        # object1.set_property(StringProperty("name", "NewName"))

        # On the other hand, this will work.
        # for document in project.documents.values():
        #     if(str(document.id) == "3fKhMAkcEe2C"):
        #         for child in document.children.values():
        #             print("HERE")
        #             print(child.id)
        #             child.set_property(StringProperty("name", "NewName"))

        # project.save_project()

