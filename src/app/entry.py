from __future__ import annotations

import argparse
import sys
from time import sleep
from src.core.controller.app import AppController
from src.core.manager.recorder import RecorderManager

# from uploader.uploader import WebDAVUploader
from src.core.util.colorizer import Colorizer
from src.app.ui.start_gui import start_gui


# Usage example
help_text: str = f"""
{Colorizer.green('FullScreenTracer: Full Screen Recorder and WebDAV Uploader')}  
{Colorizer.yellow('Version:')} 0.0.1
{Colorizer.yellow('Author:')}  {Colorizer.red('@JeffZuo')}

{Colorizer.cyan('Description:')}  
    This program is used for screen recording and WebDAV file uploading.
    It automatically detects the screen resolution and records based on the configuration.
    The recorded files are split into specified time segments and uploaded to the WebDAV server.

{Colorizer.cyan('Example:')} 
    python script.py --start     # Start screen recording.
    python script.py --stop      # Stop recording.
    python script.py --sync      # Sync to WebDAV.

{Colorizer.cyan('config.json:')}  
    device_name - Name of the device for file organization.
    fps - Frames per second for recording.
    segment_duration - Segment Duration (in seconds) for slicing recordings.
    webdav.url - WebDAV server URL.
    webdav.username - WebDAV username.
    webdav.password - WebDAV password.
    storage.local_path - Local path to store recorded files.
"""


def parse_arguments() -> argparse.Namespace:
    """Command line argument parsing"""
    parser = argparse.ArgumentParser(add_help=False)

    # Main commands
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--gui", action="store_true", help="Start with GUI")
    group.add_argument(
        "--start", action="store_true", help="Start the recording system"
    )
    group.add_argument("--stop", action="store_true", help="Stop the ongoing recording")
    group.add_argument("--sync", action="store_true", help="Perform file sync")

    parser.add_argument(
        "-h", "--help", action="store_true", help="Show help information"
    )

    return parser.parse_args()


def start() -> None:
    """Main entry point for the application"""
    app_controller = AppController()
    args = parse_arguments()

    if args.help:
        print(help_text)
        return

    app_controller.setup_config()
    app_controller.setup_components()

    if args.gui or not any(vars(args).values()):
        start_gui(app_controller)
    elif args.start:
        app_controller.start_recording()
        app_controller.start_polling()
    elif args.stop:
        app_controller.cleanup()
    elif args.sync:
        app_controller.manual_upload()
    else:
        print(
            Colorizer.yellow(
                "⚠ Please specify the operation type (--start/--stop/--sync)"
            )
        )
        sys.exit(1)
