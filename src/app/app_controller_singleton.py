from __future__ import annotations

from src.core.controller.app import AppController
from typing import Optional


class AppControllerSingleton:
    _instance: Optional[AppControllerSingleton] = None

    def __new__(cls) -> AppControllerSingleton:
        if cls._instance is None:
            cls._instance = super(AppControllerSingleton, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self) -> None:
        self.app_controller: AppController = AppController()

    def get_app_controller(self) -> AppController:
        return self.app_controller
