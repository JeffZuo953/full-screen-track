# Standard library imports
from __future__ import annotations
import re
import types


class Colorizer:
    """
    A class for colorizing text using ANSI escape codes.
    """

    # Regular expression to match ANSI escape sequences
    ANSI_ESCAPE_RE: re.Pattern = re.compile(r"\x1b\[(\d+)m")

    def __new__(cls) -> types.ClassMethodDescriptorType:
        """Prevent instantiation of this class."""
        raise TypeError("This is a static class and cannot be instantiated.")

    @staticmethod
    def colorize(text: str, color_code: str) -> str:
        """
        Colorizes the given text with the specified ANSI color code.

        Args:
            text: The text to colorize.
            color_code: The ANSI color code to use.

        Returns:
            The colorized text.
        """
        return f"\033[{color_code}m{text}\033[0m"

    @staticmethod
    def green(text: str) -> str:
        """
        Colorizes the given text green.

        Args:
            text: The text to colorize.

        Returns:
            The green colorized text.
        """
        return Colorizer.colorize(text, "32")

    @staticmethod
    def yellow(text: str) -> str:
        """
        Colorizes the given text yellow.

        Args:
            text: The text to colorize.

        Returns:
            The yellow colorized text.
        """
        return Colorizer.colorize(text, "33")

    @staticmethod
    def cyan(text: str) -> str:
        """
        Colorizes the given text cyan.

        Args:
            text: The text to colorize.

        Returns:
            The cyan colorized text.
        """
        return Colorizer.colorize(text, "36")

    @staticmethod
    def red(text: str) -> str:
        """
        Colorizes the given text red.

        Args:
            text: The text to colorize.

        Returns:
            The red colorized text.
        """
        return Colorizer.colorize(text, "31")

    @staticmethod
    def ansi_to_html(text: str) -> str:
        """
        Converts ANSI escape sequences in the given text to HTML color spans.

        Args:
            text: The text containing ANSI escape sequences.

        Returns:
            The text with ANSI escape sequences replaced by HTML color spans.
        """

        def replace_ansi(match: re.Match) -> str:
            """
            Replaces ANSI escape sequences with HTML color spans.

            Args:
                match: re.Match object

            Returns:
                str: HTML color spans
            """
            color_code: str = match.group(1)
            if color_code == "91":
                return "<span style='color: red;'>"
            elif color_code == "92":
                return "<span style='color: green;'>"
            elif color_code == "93":
                return "<span style='color: yellow;'>"
            elif color_code == "96":
                return "<span style='color: cyan;'>"
            elif color_code == "0":
                return "</span>"
            return match.group(0)

        return Colorizer.ANSI_ESCAPE_RE.sub(replace_ansi, text)
