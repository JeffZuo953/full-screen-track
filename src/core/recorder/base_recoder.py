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
        self.config = config
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
        pass

    @abstractmethod
    def get_recorder_type(self) -> str:
        pass

    def _get_process_pipes(self) -> Tuple[str, str]:
        if self.log_ffmpeg:
            return subprocess.PIPE, subprocess.PIPE
        return subprocess.DEVNULL, subprocess.DEVNULL

    def start_recording(self,
                        device: str = "",
                        output_path="") -> Optional[subprocess.Popen]:
        stdout, stderr = self._get_process_pipes()
        cmd = self._build_command(device, output_path)
        cmd_str = " ".join(cmd)
        type = self.get_recorder_type()
        try:
            logger.debug(
                f"Starting {self.get_recorder_type()} recording: {cmd_str}")
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            creation_flags = (
                win32process.CREATE_NO_WINDOW |  # 不创建控制台窗口
                win32con.DETACHED_PROCESS  # 分离进程
            )

            self.process = subprocess.Popen(cmd,
                                            stdout=stdout,
                                            stderr=stderr,
                                            startupinfo=startupinfo,
                                            creationflags=creation_flags)

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
        """Validate segment duration validity"""
        if self.segment_duration is not None:
            try:
                duration = int(self.segment_duration)
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
        """Monitor FFmpeg process output"""

        def _monitor_ffmpeg_output() -> None:
            while process.poll() is None:
                try:
                    line = process.stderr.readline().decode("utf-8")
                    if line:
                        logger.debug(
                            f"FFmpeg {type} output [{device_name}]: {line.strip()}"
                        )
                except Exception as e:
                    logger.debug(f"Error reading {type} output: {e}")
                time.sleep(0.1)

            remaining_output = process.stderr.read().decode("utf-8")
            if remaining_output:
                logger.debug(
                    f"Remaining {type} output [{device_name}]: {remaining_output.strip()}"
                )

        thread = threading.Thread(target=_monitor_ffmpeg_output, daemon=True)
        thread.start()
        return thread

    def _device_name_to_path(self, name: str) -> str:
        """Sanitize device name for filesystem use"""
        return re.sub(r'[\\/*?:"<>|]', "", name).strip()

    def _get_ouput_template(self, prefix: str = "") -> str:
        """Generate output filename template"""
        return os.path.join(prefix, "%Y%m%d_%H%M%S")

    def _parse_output_path(self, cmd_args: List[str]) -> str:
        """Extract output path from command arguments"""
        for arg in reversed(cmd_args):
            if arg.endswith((".mp4", ".mp3")):
                return os.path.abspath(arg)
        return "Unknown path"

    def _get_process_runtime(self, process: subprocess.Popen) -> str:
        """Calculate process runtime"""
        try:
            import psutil  # type: ignore

            create_time = psutil.Process(process.pid).create_time()
            return time.strftime("%H:%M:%S",
                                 time.gmtime(time.time() - create_time))
        except ImportError:
            return "Unknown time"

    def get_local_path(self) -> str:
        return self.local_path
