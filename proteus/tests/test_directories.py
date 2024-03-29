# ==========================================================================
# File: test_directories.py
# Description: pytest file for the PROTEUS application directories
# Date: 10/10/2022
# Version: 0.1
# Author: Amador Durán Toro
# ==========================================================================

# --------------------------------------------------------------------------
# Standard library imports
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Project specific imports
# --------------------------------------------------------------------------
from proteus.utils.config import Config
# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------

def test_application_directories():
    """
    It tests that essential PROTEUS directories exist.
    """
    app : Config = Config()
    assert app.resources_directory.is_dir()
    assert app.icons_directory.is_dir()
    assert app.archetypes_directory.is_dir()
