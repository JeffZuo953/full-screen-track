from __future__ import annotations

from src.core.util.logger import logger

import os
import re
import subprocess
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from abc import ABC, abstractmethod
import win32process
import win32con


class BaseRecorder(ABC):
    """Base class for all recorders"""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initializes the BaseRecorder.

        Args:
            config: Configuration dictionary.
        """
        self.config: Dict[str, Any] = config
        self.process: Optional[subprocess.Popen] = None

        # Common configurations
        self.segment_duration: Optional[int] = self.config.get(
            "segment_duration")
        self.device_name: str = self.config.get("device_name", "default")

        # Storage configuration
        storage_config: Dict[str, Any] = self.config.get("storage", {})
        self.local_path: str = storage_config.get("local_path", "./")

        # Log configuration
        self.log: Dict[str, Any] = self.config.get("log", {})
        self.log_ffmpeg: bool = self.log.get("ffmpeg", False)

    @abstractmethod
    def _build_command(self, device: str, output_path: str) -> List[str]:
        """
        Abstract method to build the recording command.  Must be implemented by subclasses.

        Args:
            device: The device to record from.
            output_path: The output path.

        Returns:
            The command as a list of strings.
        """
        pass

    @abstractmethod
    def get_recorder_type(self) -> str:
        """
        Abstract method to get recorder type. Must be implemented by subclasses.

        Returns:
            The type of recorder (e.g., "audio", "video").
        """
        pass

    def _get_process_pipes(self) -> Tuple[Any, Any]:
        """
        Gets the appropriate pipes for the subprocess based on logging configuration.

        Returns:
            A tuple of (stdout, stderr) pipes.
        """
        if self.log_ffmpeg:
            return subprocess.PIPE, subprocess.PIPE
        return subprocess.DEVNULL, subprocess.DEVNULL

    def start_recording(self,
                        device: str = "",
                        output_path: str = "") -> Optional[subprocess.Popen]:
        """
        Starts the recording process.

        Args:
            device: The device to record from.
            output_path: The output path for the recording.

        Returns:
            The subprocess.Popen object if successful, None otherwise.
        """
        stdout, stderr = self._get_process_pipes()
        cmd: List[str] = self._build_command(device, output_path)
        cmd_str: str = " ".join(cmd)
        type: str = self.get_recorder_type()
        try:
            logger.debug(f"Starting {type} recording: {cmd_str}")
            startupinfo: subprocess.STARTUPINFO = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            creation_flags: int = (win32process.CREATE_NO_WINDOW
                                   | win32con.DETACHED_PROCESS)

            self.process = subprocess.Popen(
                cmd,
                stdout=stdout,
                stderr=stderr,
                startupinfo=startupinfo,
                creationflags=creation_flags,
            )

            if self.log_ffmpeg:
                self._start_monitoring_ffmpeg_log(
                    self.process,
                    type,
                    type.capitalize(),
                )
            return self.process
        except Exception as e:
            raise logger.exception(
                f"{type} recording failed ({device}): {str(e)}")

    def validate_segment_duration(self) -> Optional[int]:
        """
        Validates the segment duration and adjusts it if necessary.

        Returns:
            The validated segment duration, or None if invalid.
        """
        if self.segment_duration is not None:
            try:
                duration: int = int(self.segment_duration)
                if duration < 10:
                    logger.debug(
                        f"Warning: Segment duration {duration}s is too short, adjusted to 10s"
                    )
                    return 10
                return duration
            except ValueError:
                logger.debug(
                    "Error: Invalid segment duration, using continuous recording"
                )
                return None
        return None

    def _start_monitoring_ffmpeg_log(self, process: subprocess.Popen,
                                     device_name: str,
                                     type: str) -> Optional[threading.Thread]:
        """
        Starts a thread to monitor FFmpeg process output.

        Args:
            process: The FFmpeg subprocess.
            device_name: The name of the device being recorded.
            type: The type of recorder (e.g., "audio", "video").

        Returns:
            The monitoring thread.
        """

        def _monitor_ffmpeg_output() -> None:
            while process.poll() is None:
                try:
                    line: str = process.stderr.readline().decode(
                        "utf-8")  # type: ignore
                    if line:
                        logger.debug(
                            f"FFmpeg {type} output [{device_name}]: {line.strip()}"
                        )
                except Exception as e:
                    logger.debug(f"Error reading {type} output: {e}")
                time.sleep(0.1)

            remaining_output: str = process.stderr.read().decode(
                "utf-8")  # type: ignore
            if remaining_output:
                logger.debug(
                    f"Remaining {type} output [{device_name}]: {remaining_output.strip()}"
                )

        thread: threading.Thread = threading.Thread(
            target=_monitor_ffmpeg_output, daemon=True)
        thread.start()
        return thread

    def _device_name_to_path(self, name: str) -> str:
        """
        Sanitizes the device name for use in file system paths.

        Args:
            name: The device name.

        Returns:
            The sanitized device name.
        """
        return re.sub(r'[\\/*?:"<>|]', "", name).strip()

    def _get_ouput_template(self, prefix: str = "") -> str:
        """
        Generates the output filename template.

        Args:
            prefix: The prefix for the output path.

        Returns:
            The output filename template.
        """
        return os.path.join(prefix, "%Y%m%d_%H%M%S")

    def _parse_output_path(self, cmd_args: List[str]) -> str:
        """
        Extracts the output path from the command arguments.

        Args:
            cmd_args: The command arguments.

        Returns:
            The absolute output path.
        """
        for arg in reversed(cmd_args):
            if arg.endswith((".mp4", ".mp3")):
                return os.path.abspath(arg)
        return "Unknown path"

    def _get_process_runtime(self, process: subprocess.Popen) -> str:
        """
        Calculates the process runtime.

        Args:
            process: The subprocess.

        Returns:
            The process runtime as a string (HH:MM:SS) or "Unknown time".
        """
        try:
            import psutil  # type: ignore

            create_time: float = psutil.Process(process.pid).create_time()
            return time.strftime("%H:%M:%S",
                                 time.gmtime(time.time() - create_time))
        except ImportError:
            return "Unknown time"

    def get_local_path(self) -> str:
        """
        Gets the local storage path.

        Returns:
            local storage path
        """
        return self.local_path
