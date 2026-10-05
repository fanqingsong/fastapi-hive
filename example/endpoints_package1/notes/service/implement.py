from fastapi_hive.ioc_framework.decorators import component


@component()
class NoteTextNormalizer:
    def normalize(self, text: str) -> str:
        return text.strip()
