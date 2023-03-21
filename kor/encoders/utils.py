import re
from typing import Optional

# PUBLIC API


def wrap_in_tag(tag_name: str, content: str) -> str:
    """Wrap the content in an HTML style tag."""
    return f"<{tag_name}>{content}</{tag_name}>"


def unwrap_tag(tag_name: str, text: str) -> Optional[str]:
    """Extract content located inside a tag."""
    pattern = f"<{tag_name}>(.*?)</{tag_name}>"
    content = re.compile(pattern, re.DOTALL)
    match = content.search(text)
    if match:
        return match.group(1)
    else:
        return None
