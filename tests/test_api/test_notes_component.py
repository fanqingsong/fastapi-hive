from example.endpoints_package1.notes.service import NoteComposer, NoteTextNormalizer


def test_notes_component_is_scanned(test_client) -> None:
    hive = test_client.app.state.hive
    assert hive.has(NoteTextNormalizer)
    assert isinstance(hive.get(NoteTextNormalizer), NoteTextNormalizer)
    assert hive.get(NoteTextNormalizer).normalize("  hello  ") == "hello"


def test_note_composer_injects_normalizer(test_client) -> None:
    hive = test_client.app.state.hive
    composer = hive.get(NoteComposer)
    assert isinstance(composer, NoteComposer)
    assert composer.normalizer is hive.get(NoteTextNormalizer)
    assert composer.compose("  hello   world  ") == "hello world"
