from __future__ import annotations
import os
import subprocess

import imageio_ffmpeg
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional
from src.core.util.logger import logger

from src.core.recorder.audio_recorder import AudioRecorder
from src.core.recorder.screen_recorder import ScreenRecorder
from src.core.manager.config import ConfigManager

import win32process


class RecorderManager:
    """Main recorder coordinator"""

    def __init__(self, config_manager: ConfigManager) -> None:
        """
        Initializes the RecorderManager.

        Args:
            config_manager: The ConfigManager instance.
        """
        self.config_manager: ConfigManager = config_manager
        self.processes: List[subprocess.Popen] = []
        self.screen_recorder: ScreenRecorder = ScreenRecorder(
            self.config_manager)
        self.audio_recorders: List[AudioRecorder] = []
        self.show_ffmpeg_log: bool = config_manager.get_log_config().get(
            "ffmpeg", False)

    def get_audio_devices(self) -> List[str]:
        """Get available audio devices"""
        ffmpeg_exe: str = imageio_ffmpeg.get_ffmpeg_exe()
        try:
            # Add Windows specific process creation configuration
            startupinfo: subprocess.STARTUPINFO = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            result: subprocess.CompletedProcess = subprocess.run(
                [
                    ffmpeg_exe, "-list_devices", "true", "-f", "dshow", "-i",
                    "dummy"
                ],
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                startupinfo=startupinfo,
                creationflags=win32process.CREATE_NO_WINDOW,
            )
            devices: List[str] = []
            in_section: bool = False
            for line in result.stderr.splitlines():
                if "DirectShow audio devices" in line:
                    in_section = True
                    continue
                if in_section and '"' in line:
                    device: str = line[line.find('"') + 1:line.rfind('"')]
                    if not device.startswith(("@device_cm_", "dummy:")):
                        devices.append(device)
            return devices
        except Exception as e:
            logger.error(f"Failed to get audio devices: {e}")
            return []

    def start_recording(self) -> None:
        """Start all recording sessions"""
        now: str = datetime.now().strftime("%Y%m%d")
        base_folder: str = os.path.join(
            self.config_manager.get_storage_config()["local_path"],
            self.config_manager.get_device_name(),
            now,
        )

        audio_devices: List[str] = self.get_audio_devices()
        self.audio_recorders = [
            AudioRecorder(self.config_manager) for _ in audio_devices
        ]

        with ThreadPoolExecutor(max_workers=len(audio_devices) +
                                1) as executor:
            futures: List[Any] = []

            # Screen recording
            video_folder: str = os.path.join(base_folder, "screen")
            os.makedirs(video_folder, exist_ok=True)
            futures.append(
                executor.submit(self.screen_recorder.start_recording,
                                "FullScreen", video_folder))

            # Audio recordings
            audio_folder: str = os.path.join(base_folder, "audio")
            os.makedirs(audio_folder, exist_ok=True)
            for device, recorder in zip(audio_devices, self.audio_recorders):
                device_folder: str = os.path.join(
                    audio_folder, recorder._device_name_to_path(device))
                os.makedirs(device_folder, exist_ok=True)
                futures.append(
                    executor.submit(recorder.start_recording, device,
                                    audio_folder))
            # Collect successful processes
            self.processes = [
                f.result() for f in futures if f.result() is not None
            ]

    def stop_recording(self) -> None:
        """Stop all active recordings"""
        logger.debug("try to stop %d processes", len(self.processes))
        for process in self.processes:
            if process.poll() is None:
                logger.debug("try to stop process: %s", process.pid)
                process.terminate()
                process.wait()
                logger.debug("stopped process: %s", process.pid)
        self.processes.clear()
        logger.debug("All recording processes stopped")
        self._cleanup_temp_files()

    def restart_recording(self) -> None:
        """Restart all recordings"""
        self.stop_recording()
        self.start_recording()

    def list_processes(self) -> List[Dict[str, Any]]:
        """List active recording processes"""
        return [{
            "pid": p.pid,
            "runtime": self.screen_recorder._get_process_runtime(p),
            "output": self.screen_recorder._parse_output_path(p.args),
        } for p in self.processes if p and p.poll() is None]

    def _cleanup_temp_files(self) -> None:
        """
        Clean up temporary files in the .tmp directory.
        Moves completed recordings to their final destination.
        """
        base_path: str = self.config_manager.get_storage_config()["local_path"]
        device_path: str = os.path.join(base_path,
                                        self.config_manager.get_device_name())
        tmp_path: str = os.path.join(device_path, ".tmp")

        if os.path.exists(tmp_path):
            for file in os.listdir(tmp_path):
                if file.endswith((".mp4", ".mp3")):
                    temp_file: str = os.path.join(tmp_path, file)
                    self._move_completed_recording(temp_file, device_path)

    def _move_completed_recording(self, temp_file: str,
                                  device_path: str) -> Optional[str]:
        """Move completed recording to the device folder"""
        if not os.path.exists(temp_file):
            return None

        new_file: str = os.path.join(device_path, os.path.basename(temp_file))
        os.rename(temp_file, new_file)
        logger.info(f"Moved {temp_file} to {new_file}")
        return new_file
