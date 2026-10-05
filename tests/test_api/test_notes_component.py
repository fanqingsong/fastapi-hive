from example.endpoints_package1.notes.service import NoteTextNormalizer


def test_notes_component_is_scanned(test_client) -> None:
    hive = test_client.app.state.hive
    assert hive.has(NoteTextNormalizer)
    assert isinstance(hive.get(NoteTextNormalizer), NoteTextNormalizer)
    assert hive.get(NoteTextNormalizer).normalize("  hello  ") == "hello"
