from fastapi_hive.ioc_framework.decorators import component
from fastapi_hive.ioc_framework.registry import Inject


@component()
class NoteTextNormalizer:
    def normalize(self, text: str) -> str:
        return text.strip()


@component()
class NoteComposer:
    def __init__(self, normalizer: NoteTextNormalizer = Inject(NoteTextNormalizer)):
        self.normalizer = normalizer

    def compose(self, text: str) -> str:
        return " ".join(self.normalizer.normalize(text).split())
