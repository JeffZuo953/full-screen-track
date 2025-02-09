from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional

import imageio_ffmpeg
from src.core.recorder.base_recoder import BaseRecorder


class ScreenRecorder(BaseRecorder):
    """Handles screen recording operations."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initializes the ScreenRecorder.

        Args:
            config: Configuration dictionary.
        """
        super().__init__(config)
        screen_config: Dict[str, Any] = config.get("screen", {})
        self.framerate: int = screen_config.get("framerate", 30)
        self.display_id: int = screen_config.get("display_id", 1)

    def _build_command(self, device: str, folder: str) -> List[str]:
        """
        Builds the FFmpeg command for screen recording.

        Args:
            device: The screen capture device name (ignored, uses display_id).
            folder: The base folder for storing recordings.

        Returns:
            The FFmpeg command as a list of strings.
        """
        segment_duration: Optional[int] = self.validate_segment_duration()
        device_name: str = self.config.get("device_name", "default")
        date_str: str = time.strftime("%Y%m%d")
        tmp_path: str = os.path.join(".tmp", device_name, date_str, "screen")
        os.makedirs(tmp_path, exist_ok=True)

        output_template: str = self._get_ouput_template(tmp_path)

        cmd: List[str] = [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-loglevel",
            "info",
            "-y",
            "-f",
            "gdigrab",
            "-framerate",
            str(self.framerate),
            "-i",
            f"desktop",
        ]
        #For multi-screen capture, use the following command
        # if self.display_id > 1:
        #     cmd.extend(["-offset_x", str((self.display_id-1)*1920),"-offset_y", "0"]) #Need to be modified according to the actual screen resolution
        # cmd.extend(["-video_size", "1920x1080"])

        if segment_duration:
            cmd.extend([
                "-f",
                "segment",
                "-segment_time",
                str(segment_duration),
                "-reset_timestamps",
                "1",
                "-strftime",
                "1",
                f"{output_template}.mp4",
            ])
        else:
            cmd.append(os.path.join(tmp_path, f"{int(time.time())}.mp4"))

        return cmd

    def get_recorder_type(self) -> str:
        return "screen"
