class Colorizer:
    def __new__(cls):
        raise TypeError("This is a static class and cannot be instantiated.")

    @staticmethod
    def colorize(text: str, color_code: str) -> str:
        return f"\033[{color_code}m{text}\033[0m"

    @staticmethod
    def green(text: str) -> str:
        return Colorizer.colorize(text, "32")

    @staticmethod
    def yellow(text: str) -> str:
        return Colorizer.colorize(text, "33")

    @staticmethod
    def cyan(text: str) -> str:
        return Colorizer.colorize(text, "36")

    @staticmethod
    def red(text: str) -> str:
        return Colorizer.colorize(text, "31")

    @staticmethod
    def ansi_to_html(text: str) -> str:
        def replace_ansi(match):
            color_code = match.group(1)
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
