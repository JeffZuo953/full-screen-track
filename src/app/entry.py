from __future__ import annotations

from src.app.app_controller_singleton import AppControllerSingleton
from src.app.ui.start_gui import start_gui
from src.core.controller.app import AppController


def start() -> None:
    """Main entry point for the application"""
    app_controller: AppController = AppControllerSingleton(
    ).get_app_controller()
    app_controller.setup()
    app_controller.start_lock_monitor_thread()

    start_gui(app_controller)
