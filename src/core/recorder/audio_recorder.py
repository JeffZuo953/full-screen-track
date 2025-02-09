from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional

import imageio_ffmpeg
from src.core.recorder.base_recoder import BaseRecorder


class AudioRecorder(BaseRecorder):
    """Handles audio recording operations"""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initializes the AudioRecorder.

        Args:
            config: Configuration dictionary.
        """
        super().__init__(config)
        audio_config: Dict[str, Any] = config.get("audio", {})
        self.sample_rate: int = audio_config.get("sample_rate", 44100)
        self.channels: int = audio_config.get("channels", 1)

    def _build_command(self, device: str, folder: str) -> List[str]:
        """
        Builds the FFmpeg command for audio recording.

        Args:
            device: The audio input device name.
            folder:  (Unused)

        Returns:
            The FFmpeg command as a list of strings.
        """
        segment_duration: Optional[int] = self.validate_segment_duration()
        clean_name: str = self._device_name_to_path(device)

        device_name: str = self.config.get("device_name", "default")
        date_str: str = time.strftime("%Y%m%d")
        tmp_path: str = os.path.join(".tmp", device_name, date_str, "audio", clean_name)
        os.makedirs(tmp_path, exist_ok=True)

        output_template: str = self._get_ouput_template(tmp_path)

        cmd: List[str] = [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-loglevel",
            "info",
            "-y",
            "-f",
            "dshow",
            "-i",
            f"audio={device}",
            "-ac",
            str(self.channels),
            "-ar",
            str(self.sample_rate),
        ]

        if segment_duration:
            cmd += [
                "-f",
                "segment",
                "-segment_time",
                str(segment_duration),
                "-strftime",
                "1",
                f"{output_template}.mp3",
            ]
        else:
            cmd.append(os.path.join(tmp_path, f"{int(time.time())}.mp3"))

        return cmd
    
    def get_recorder_type(self) -> str:
        """
        Returns the recorder type.
        """
        return "audio"
