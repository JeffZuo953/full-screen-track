from __future__ import annotations

import os
import time
from typing import Any, Dict, List

import imageio_ffmpeg
from src.core.recorder.base_recoder import BaseRecorder


class AudioRecorder(BaseRecorder):
    """Handles audio recording operations"""

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        audio_config: Dict[str, Any] = config.get("audio", {})
        self.sample_rate: int = audio_config.get("sample_rate", 44100)
        self.channels: int = audio_config.get("channels", 1)

    def _build_command(self, device: str, folder: str) -> List[str]:
        """Start audio recording session"""
        segment_duration = self.validate_segment_duration()
        clean_name = self._device_name_to_path(device)

        device_name = self.config.get_device_name()
        date_str = time.strftime("%Y%m%d")
        tmp_path = os.path.join(".tmp", device_name, date_str, "audio", clean_name)
        os.makedirs(tmp_path, exist_ok=True)

        output_template = self._get_ouput_template(tmp_path)

        cmd = [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-loglevel", "info",
            "-y",
            "-f", "dshow",
            "-i", f"audio={device}",
            "-ac", str(self.channels),
            "-ar", str(self.sample_rate),
        ]

        if segment_duration:
            cmd += [
                "-f", "segment",
                "-segment_time", str(segment_duration),
                "-strftime", "1",
                f"{output_template}.mp3",
            ]
        else:
            cmd.append(os.path.join(tmp_path, f"{int(time.time())}.mp3"))
        
        return cmd

    def get_recorder_type(self):
        return "audio"
