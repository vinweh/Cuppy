from html.parser import HTMLParser


class CupHTMLParser(HTMLParser):
    """HTML parser to extract canonical URL from HTML content"""
    def __init__(self):
        super().__init__()
        self.canonical_url = None
        self.og_url = None
        self.og_title = None
        self.in_title = False
        self.in_head = False
        self.title = None
        self.description = None

    @staticmethod
    def _lower_attrs(attrs: list[tuple[str, str | None]]) -> list[tuple[str, str | None]]:
        """Convert all attribute names to lower case"""
        return [(k.lower(), v) for k, v in attrs]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Handle start tag"""
        tag = tag.lower()
        attrs_dict = dict(CupHTMLParser._lower_attrs(attrs)) # lower attribute names
        if tag == "link":
            if attrs_dict.get("rel", "").lower() == "canonical":
                self.canonical_url = attrs_dict.get("href")

        if tag == "meta":
            if attrs_dict.get("property") == "og:url":
                self.og_url = attrs_dict.get("content")
            if attrs_dict.get("property") == "og:title":
                self.og_title = attrs_dict.get("content")
            if attrs_dict.get("name", "").lower()  == "description":
                self.description = attrs_dict.get("content")

        if tag == "head":
            self.in_head = True
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "head":
            self.in_head = False
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title and self.in_head:
            self.title = data
            print(f"Title: {self.title}")
