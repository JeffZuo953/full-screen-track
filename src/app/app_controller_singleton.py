from src.core.controller.app import AppController

class AppControllerSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppControllerSingleton, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance 

    def initialize(self):
        self.app_controller = AppController()

    def get_app_controller(self):
        return self.app_controller
