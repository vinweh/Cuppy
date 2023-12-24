import urllib
from urllib.robotparser import RobotFileParser


class CustomRobotParser(RobotFileParser):
    """Custom robot parser that supports storing the robots.txt content for later reuse.
    """
    def __init__(self):
        super().__init__()
        self.robots_content = None

    def read(self) -> None:
        """Reads the robots.txt URL, stores it for later reuse, and feeds it to the parser."""
        try:
            f = urllib.request.urlopen(self.url)
        except urllib.error.HTTPError as err:
            if err.code in (401, 403):
                self.disallow_all = True
            elif err.code >= 400 and err.code < 500:
                self.allow_all = True
        else:
            raw = f.read()
            self.robots_content = raw.decode("utf-8")
            self.parse(self.robots_content.splitlines())

    def can_fetch(self, useragent: str, url: str) -> bool:
        return super().can_fetch(useragent, url)