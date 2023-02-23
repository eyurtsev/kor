"""Parse LLM Response."""

from html.parser import HTMLParser


class LLMTagParser(HTMLParser):
    def __init__(self) -> None:
        """A heavy-handed solution, but it's fast for prototyping."""
        super().__init__()
        self.current_tag = None
        self.data = {}
        self.success = True

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag

    def handle_endtag(self, tag):
        self.current_tag = None

    def handle_data(self, data):
        # The only data that's allowed is whitespace or a comma surrounded by whitespace
        if self.current_tag is None:
            if data.strip() not in (",", ""):
                self.success = False
        else:
            self.data[self.current_tag] = data


def parse_llm_response(response: str) -> dict[str, str]:
    """Parse llm response."""
    tag_parser = LLMTagParser()
    tag_parser.feed(response)
    if not tag_parser.success:
        return {}
    return tag_parser.data
