from __future__ import annotations

import os
import time
from typing import Any, Dict, List

import imageio_ffmpeg
from src.core.recorder.base_recoder import BaseRecorder


class ScreenRecorder(BaseRecorder):
    """Handles screen recording operations"""

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self.fps: int = config.get("fps", 10)

    def _build_command(self, device: str, folder: str) -> List[str]:
        """Start screen recording session"""
        segment_duration = self.validate_segment_duration()

        # 构建临时文件夹路径
        device_name = self.config.get_device_name()
        date_str = time.strftime("%Y%m%d")
        tmp_path = os.path.join(".tmp", device_name, date_str, "screen")
        os.makedirs(tmp_path, exist_ok=True)

        output_template = self._get_ouput_template(tmp_path)

        cmd = [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-loglevel", "info",
            "-y",
            "-framerate", str(self.fps),
            "-f", "gdigrab",
            "-i", "desktop",
            "-vcodec", "libx264",
            "-preset", "fast",
            "-movflags", "+faststart",
        ]

        if segment_duration:
            cmd += [
                "-g", "1",
                "-f", "segment",
                "-segment_time", str(segment_duration),
                "-reset_timestamps", "1",
                "-strftime", "1",
                "-segment_format_options", "movflags=+empty_moov+faststart",
                f"{output_template}.mp4",
            ]
        else:
            cmd.append(os.path.join(tmp_path, f"{int(time.time())}.mp4"))

        return cmd

    def get_recorder_type(self):
        return "video"
