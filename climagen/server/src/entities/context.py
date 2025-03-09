import hashlib
from dataclasses import dataclass

@dataclass
class Context:
    def __init__(self, source, page, link, content):
        self.source = source
        self.page = page
        self.link = link
        self.content = content
        self.hash = hashlib.sha256(content.encode()).hexdigest()