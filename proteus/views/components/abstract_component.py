# ==========================================================================
# File: abstract_component.py
# Description: Abstract class for all the components in the PROTEUS application
# Date: 15/11/2023
# Version: 0.1
# Author: José María Delgado Sánchez
# ==========================================================================

# --------------------------------------------------------------------------
# Standard library imports
# --------------------------------------------------------------------------

import logging
from abc import ABC, abstractmethod
from typing import Type

# --------------------------------------------------------------------------
# Third-party library imports
# --------------------------------------------------------------------------

from PyQt6.QtWidgets import QWidget, QDialog
import PyQt6.sip

# --------------------------------------------------------------------------
# Project specific imports
# --------------------------------------------------------------------------

from proteus.config import Config
from proteus.views.utils.event_manager import EventManager
from proteus.views.utils.state_manager import StateManager
from proteus.views.utils.translator import Translator
from proteus.controller.command_stack import Controller

# logging configuration
log = logging.getLogger(__name__)


# --------------------------------------------------------------------------
# Class: AbstractWidgetMeta
# Description: Metaclass for ProteusComponent class
# Date: 15/11/2023
# Version: 0.1
# Author: José María Delgado Sánchez
# --------------------------------------------------------------------------
# NOTE: Workaround to allow multiple inheritance from QWidget and ABC
# https://stackoverflow.com/questions/28720217/multiple-inheritance-metaclass-conflict
class AbstractWidgetMeta(type(QWidget), type(ABC)):
    """
    Metaclass for ProteusComponent class. It defines the metaclass for
    ProteusComponent class. It is used to create an abstract class that
    inherits from QWidget and ABC.
    """

    pass


# --------------------------------------------------------------------------
# Class: ProteusComponent
# Description: ProteusComponent abstract class
# Date: 15/11/2023
# Version: 0.1
# Author: José María Delgado Sánchez
# --------------------------------------------------------------------------
class ProteusComponent(QWidget, ABC, metaclass=AbstractWidgetMeta):
    """
    ProteusComponent abstract class. It is the base class for all the
    components in the PROTEUS application.

    It provides the basic variables that every component needs to work
    (controller, config, translator, event_manager and state_manager).
    Performs the validation of the parameters and initializes the variables
    with default values if needed.

    When a component inherits from ProteusComponent, if it also inherits
    from other QWidget subclass, ProteusComponent must be placed after
    it to avoid metaclass conflicts.
    
    Example of class with multiple inheritance:
        - class MyComponent(QDialog, ProteusComponent):
        - class mro(MyComponent): [MyComponent, QDialog, ProteusComponent, QWidget,
        QObject, sip.wrapper, QPaintDevice, sip.simplewrapper, ABC, object]
    """

    # ----------------------------------------------------------------------
    # Method     : __init__
    # Description: Class constructor for ProteusComponent class.
    # Date       : 15/11/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def __init__(
        self,
        controller: Controller,
        parent: QWidget | None = None,
        config: Config = None,
        translator: Translator = None,
        event_manager: EventManager = None,
        state_manager: StateManager = None,
        *args,
        **kwargs,
    ) -> None:
        super(ProteusComponent, self).__init__(parent, *args, **kwargs)
        """
        Class constructor for ProteusComponent class. It manage the dependency
        injection. Validates the parameters showing logs messages
        and raises exceptions if needed. Some parameters will be initialized
        if they are not provided.

        :param controller: Controller instance.
        :param parent: Parent QWidget.
        :param config: App configuration instance.
        :param translator: Translator instance.
        :param event_manager: Event manager instance.
        :param state_manager: State manager instance.
        """
        # Controller --------------
        assert isinstance(
            controller, Controller
        ), f"Controller instance is required to create a ProteusComponent, current value type: {type(controller)}"
        self._controller: Controller = controller

        # Config ------------------
        if config is None:
            config = Config()
        else:
            log.debug(
                f"Custom Config instance provided for ProteusComponent {self.__class__.__name__}"
            )

        assert isinstance(
            config, Config
        ), f"Config instance is required to create a ProteusComponent, current value type: {type(config)}"
        self._config: Config = config

        # Translator -------------
        if translator is None:
            translator = Translator()
        else:
            log.debug(
                f"Custom Translator instance provided for ProteusComponent {self.__class__.__name__}"
            )

        assert isinstance(
            translator, Translator
        ), f"Translator instance is required to create a ProteusComponent, current value type: {type(translator)}"
        self._translator: Translator = translator

        # Event manager ----------
        if event_manager is None:
            event_manager = EventManager()
        else:
            log.debug(
                f"Custom EventManager instance provided for ProteusComponent {self.__class__.__name__}"
            )

        assert isinstance(
            event_manager, EventManager
        ), f"EventManager instance is required to create a ProteusComponent, current value type: {type(event_manager)}"
        self._event_manager: EventManager = event_manager

        # State manager ----------
        if state_manager is None:
            state_manager = StateManager()
        else:
            log.debug(
                f"Custom StateManager instance provided for ProteusComponent {self.__class__.__name__}"
            )

        assert isinstance(
            state_manager, StateManager
        ), f"StateManager instance is required to create a ProteusComponent, current value type: {type(state_manager)}"
        self._state_manager: StateManager = state_manager

    # ----------------------------------------------------------------------
    # Method     : create_component
    # Description: Create the component interface and setup logic.
    # Date       : 15/11/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    @abstractmethod
    def create_component(self) -> None:
        """
        Create the component interface and setup logic. This method must be
        implemented in the child class.
        """
        pass

    # ----------------------------------------------------------------------
    # Method     : subscribe
    # Description: Subscribe the component methods to the events.
    # Date       : 15/11/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def subscribe(self) -> None:
        """
        Subscribe the component methods to the events. Must be overriden in
        the child class.
        """
        pass

    # ----------------------------------------------------------------------
    # Method     : delete_component
    # Description: Delete the component and all its ProteusComponent children.
    # Date       : 15/11/2023
    # Version    : 0.1
    # Author     : José María Delgado Sánchez
    # ----------------------------------------------------------------------
    def delete_component(self) -> None:
        """
        Delete the component and all its ProteusComponent children.
        """
        # Look for ProteusComponent children
        child: ProteusComponent
        for child in self.findChildren(ProteusComponent):
            # Delete the child
            child.delete_component()

        # Detach from events
        self._event_manager.detach(self)

        # Delete the component
        self.setParent(None)
        self.deleteLater()

        log.debug(f"Component {self.__class__.__name__} deleted")
