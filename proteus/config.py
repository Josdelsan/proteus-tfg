# ==========================================================================
# File: config.py
# Description: the config paths for PROTEUS application
# Date: 11/10/2022
# Version: 0.2
# Author: Amador Durán Toro
#         Pablo Rivera Jiménez
#         José María Delgado Sánchez
# ==========================================================================
# Update: 22/06/2023 (José María Delgado Sánchez)
# Description:
# - Convert the Config class into a singleton class.
# ==========================================================================

# --------------------------------------------------------------------------
# Standard library imports
# --------------------------------------------------------------------------

from typing import Dict
from pathlib import Path
from configparser import ConfigParser
import logging

# --------------------------------------------------------------------------
# Third-party library imports
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Project specific imports
# --------------------------------------------------------------------------

import proteus

# logging configuration
log = logging.getLogger(__name__)

# --------------------------------------------------------------------------
# Constant declarations for PROTEUS configuration file keys
# --------------------------------------------------------------------------

CONFIG_FILE          : str = 'proteus.ini'

# Settings
SETTINGS             : str = 'settings'
LANGUAGE             : str = 'language'

# XSL templates
XSL_TEMPLATES        : str = 'xsl_templates'

# Directories
DIRECTORIES          : str = 'directories'
BASE_DIRECTORY       : str = 'base_directory'
ARCHETYPES_DIRECTORY : str = 'archetypes_directory'
RESOURCES_DIRECTORY  : str = 'resources_directory'
ICONS_DIRECTORY      : str = 'icons_directory'
XSLT_DIRECTORY       : str = 'xslt_directory'
I18N_DIRECTORY       : str = 'i18n_directory'

# --------------------------------------------------------------------------
# Class: Config
# Description: Class for the Configuration PROTEUS application
# Date: 11/10/2022
# Version: 0.2
# Author: Amador Durán Toro
#         Pablo Rivera Jiménez
#         José María Delgado Sánchez
# --------------------------------------------------------------------------

class Config:

    # Singleton instance
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        It creates a singleton instance for Config class.
        """
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        It initializes the config paths for PROTEUS application.
        """
        # Check if the instance has been initialized
        if self._initialized:
            return
        self._initialized = True

        # Application configuration
        self.config : ConfigParser = self._create_config_parser()

        # Application directories ------------------------------------------
        self.directories = self.config[DIRECTORIES]
        self.base_directory       : Path = proteus.PROTEUS_APP_PATH / self.directories[BASE_DIRECTORY]
        self.resources_directory  : Path = proteus.PROTEUS_APP_PATH / self.directories[RESOURCES_DIRECTORY]
        self.archetypes_directory : Path = proteus.PROTEUS_APP_PATH / self.directories[ARCHETYPES_DIRECTORY]
        self.icons_directory      : Path = self.resources_directory / self.directories[ICONS_DIRECTORY]
        self.xslt_directory       : Path = self.resources_directory / self.directories[XSLT_DIRECTORY]
        self.i18n_directory       : Path = self.resources_directory / self.directories[I18N_DIRECTORY]

        # XSL template routes ----------------------------------------------
        self.xslt_routes : Dict[str, Path] = self._create_xslt_routes()

        # Application settings ---------------------------------------------
        self.settings = self.config[SETTINGS]
        self.language : str = self.settings[LANGUAGE]

        # Current project --------------------------------------------------
        # TODO: This is set in the project service. Current project information
        # may be stored in a separate class. This is a workarround to access
        # assets folder.
        self.current_project_path: str = None

        # Check application directories
        self.check_application_directories()

    def save_user_settings(self, settings: Dict[str, str]) -> None:
        """
        It saves the user settings in the configuration file. The settings
        will apply the next time the application is started.
        """
        # Update settings
        for setting in settings:
            log.info(f"Setting {setting} updated to {settings[setting]}")
            self.config.set(SETTINGS, setting, settings[setting])

        # Save settings
        with open(proteus.PROTEUS_APP_PATH / CONFIG_FILE, 'w') as configfile:
            self.config.write(configfile)

    def _create_xslt_routes(self) -> Dict[str, Path]:
        """
        Private method that creates a dictionary with the XSLT routes.
        """
        # Initialize dictionary
        xslt_routes : Dict[str, Path] = {}

        # Get XSLT templates from config file
        templates = self.config[XSL_TEMPLATES]

        # Create XSLT route for each template, and add it to the dictionary
        # with the template name as key
        for template in templates:
            xslt_routes[template] = self.xslt_directory / templates[template]

        return xslt_routes

    def _create_config_parser(self) -> ConfigParser:
        """
        Private method that creates configuration parser and loads config file.
        """

        CONFIG_FILE_PATH : Path = proteus.PROTEUS_APP_PATH / CONFIG_FILE
        
        assert CONFIG_FILE_PATH.exists(), \
            f"PROTEUS configuration file {CONFIG_FILE} does not exist!"

        config_parser : ConfigParser = ConfigParser()
        config_parser.read(CONFIG_FILE_PATH)

        return config_parser

    def check_application_directories(self) -> None:
        """
        It checks that essential PROTEUS directories exist.
        """
        log.info("Checking PROTEUS directories...")

        # Check if resources directory exists
        assert self.resources_directory.is_dir(), \
            f"PROTEUS resources directory '{self.resources_directory}' does not exist!"

        log.info("  Resources directory OK")


        # Check if icons directory exists
        assert self.icons_directory.is_dir(), \
            f"PROTEUS icons directory '{self.icons_directory}' does not exist!"

        log.info("  Icons directory OK")


        # Check if archetypes directory exists
        assert self.archetypes_directory.is_dir(), \
            f"PROTEUS archetypes directory '{self.archetypes_directory}' does not exist!"

        log.info("  Archetypes directory OK")

        
        # Check if projects archetypes exists
        assert (self.archetypes_directory / "projects").is_dir(), \
            f"PROTEUS archetypes projects directory '{self.archetypes_directory / 'projects'}' does not exist!"

        log.info("  Archetypes projects directory OK")


        # Check if documents archetypes exists
        assert (self.archetypes_directory / "documents").is_dir(), \
            f"PROTEUS archetypes document directory '{self.archetypes_directory / 'documents'}' does not exist!"

        log.info("  Archetypes documents directory OK")


        # Check if objects archetypes exists
        assert (self.archetypes_directory / "objects").is_dir(), \
            f"PROTEUS archetypes objects directory '{self.archetypes_directory / 'objects'}' does not exist!"

        log.info("  Archetypes objects directory OK")

        # Check if xslt directory exists
        assert self.xslt_directory.is_dir(), \
            f"PROTEUS xslt directory '{self.xslt_directory}' does not exist!"
        
        log.info("  XSLT directory OK")
        
        # Check if default xsl templates exists in xslt dictionary
        assert "default" in self.xslt_routes, \
            f"PROTEUS xslt default template does not exist!"
        
        log.info("  XSLT default template OK")
        

        # Check xsl templates loaded
        for template in self.xslt_routes:
            assert self.xslt_routes[template].exists(), \
                f"PROTEUS xslt template '{self.xslt_routes[template]}' does not exist!"
        
        log.info("  XSLT templates directories OK")