from __future__ import annotations

import json
from typing import Dict, Any, Optional


class ConfigManager:
    _instance: Optional[ConfigManager] = None
    _initialized: bool = False

    def __new__(cls, config_path: str = "config.json") -> ConfigManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: str = "config.json") -> None:
        # Only initialize once
        if not ConfigManager._initialized:
            self.config_path = config_path
            self.config: Dict[str, Any] = self.load_config()
            ConfigManager._initialized = True

    @classmethod
    def get_instance(cls, config_path: str = "config.json") -> ConfigManager:
        """Get singleton instance of ConfigManager"""
        if cls._instance is None:
            cls._instance = ConfigManager(config_path)
        return cls._instance

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from a JSON file."""
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # If the config file does not exist, create a new one with default values
            default_config = {
                "device_name": "pc",
                "fps": 1,
                "segment_duration": 10,
                "webdav": {
                    "url": "webav_url",
                    "username": "username",
                    "password": "password",
                    "remote_path": "fst"
                },
                "storage": {
                    "local_path": "./recordings"
                },
                "audio": {
                    "sample_rate": 22050
                },
                "log": {
                    "level": "info",
                    "ffmpeg": False
                }
            }
            self.save_config(default_config)
            return default_config
        except json.JSONDecodeError:
            raise Exception(
                f"Error decoding JSON in configuration file {self.config_path}."
            )

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to a JSON file."""
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the configuration, with a default."""
        return self.config.get(key, default)

    def get_webdav_config(self) -> Dict[str, str]:
        """Get the WebDAV configuration."""
        return self.config.get("webdav", {})

    def get_storage_config(self) -> Dict[str, str]:
        """Get the storage configuration."""
        return self.config.get("storage", {})

    def get_audio_config(self) -> Dict[str, Any]:
        """Get the audio configuration."""
        return self.config.get("audio", {})

    def get_device_name(self) -> str:
        """Get the device name for file organization."""
        return self.get("device_name", "default")

    def get_fps(self) -> int:
        """Get frames per second for recording."""
        return self.get("fps", 10)

    def get_segment_duration(self) -> Optional[int]:
        """Get segment duration for slicing recordings."""
        return self.get("segment_duration", None)

    def get_upload_throttle(self) -> float:
        """Get upload throttle duration"""
        return self.config.get("upload_throttle", 1.0)  # 默认1秒

    def get_log_config(self) -> Dict[str, Any]:
        """Get log configuration"""
        return self.config.get("log", {})
