from obsidian_exporter.exporter import render_markdown
from obsidian_exporter.models import ExportCard, ExportNote, ExportOptions, FieldRule


def test_render_markdown_generates_content_without_file_properties():
    note = ExportNote(
        note_id=10,
        note_type="Basic",
        deck="English",
        fields={"Front": "word"},
        tags=[],
    )
    options = ExportOptions(
        deck_name="English",
        mode="note",
        scope_label="all",
        field_rules={"Basic": FieldRule(title_fields=["Front"])},
    )

    markdown = render_markdown(notes=[note], cards=[], options=options)

    assert markdown.startswith("# Anki Export - English\n")
    assert "source: anki" not in markdown
    assert "exported:" not in markdown


def test_render_markdown_uses_title_subtitle_and_description_roles():
    note = ExportNote(
        note_id=10,
        note_type="Basic",
        deck="English",
        fields={
            "Front": "<b>word</b>",
            "AltTitle": "secondary",
            "Subtitle": "grammar",
            "Back": "meaning",
            "Example": "example sentence",
            "Extra": "ignored",
        },
        tags=["anki", "mining"],
    )
    options = ExportOptions(
        deck_name="English",
        mode="note",
        scope_label="all",
        include_metadata=False,
        field_rules={
            "Basic": FieldRule(
                title_fields=["Front", "AltTitle"],
                subtitle_fields=["Subtitle"],
                description_fields=["Back", "Example"],
            )
        },
    )

    markdown = render_markdown(notes=[note], cards=[], options=options)

    assert "# Anki Export - English" in markdown
    assert "## word" in markdown
    assert "## secondary" in markdown
    assert "### grammar" in markdown
    assert "meaning\n\nexample sentence" in markdown
    assert "**Front:**" not in markdown
    assert "Note ID:" not in markdown
    assert "ignored" not in markdown
    assert "Tags: #anki #mining" in markdown


def test_render_markdown_can_include_note_metadata():
    note = ExportNote(
        note_id=10,
        note_type="Basic",
        deck="English",
        fields={"Front": "word"},
        tags=[],
    )
    options = ExportOptions(
        deck_name="English",
        mode="note",
        scope_label="all",
        include_metadata=True,
        field_rules={"Basic": FieldRule(title_fields=["Front"])},
    )

    markdown = render_markdown(notes=[note], cards=[], options=options)

    assert "Note ID: `10`" in markdown
    assert "Type: `Basic`" in markdown
    assert "Deck: `English`" in markdown


def test_render_markdown_allows_same_field_in_multiple_roles():
    note = ExportNote(
        note_id=10,
        note_type="Basic",
        deck="English",
        fields={"Front": "word", "Back": "meaning"},
        tags=[],
    )
    options = ExportOptions(
        deck_name="English",
        mode="note",
        scope_label="all",
        field_rules={"Basic": FieldRule(title_fields=["Front"], description_fields=["Front", "Back"])},
    )

    markdown = render_markdown(notes=[note], cards=[], options=options)

    assert "## word" in markdown
    assert "word\n\nmeaning" in markdown


def test_render_markdown_adds_separator_between_notes():
    notes = [
        ExportNote(note_id=10, note_type="Basic", deck="English", fields={"Front": "one"}, tags=[]),
        ExportNote(note_id=11, note_type="Basic", deck="English", fields={"Front": "two"}, tags=[]),
    ]
    options = ExportOptions(
        deck_name="English",
        mode="note",
        scope_label="all",
        field_rules={"Basic": FieldRule(title_fields=["Front"])},
    )

    markdown = render_markdown(notes=notes, cards=[], options=options)

    assert "## one\n\n---\n\n## two" in markdown


def test_render_markdown_exports_cards_when_card_mode_is_selected():
    note = ExportNote(
        note_id=10,
        note_type="Basic",
        deck="English",
        fields={"Front": "word", "Back": "meaning"},
        tags=[],
    )
    card = ExportCard(card_id=99, note_id=10, deck="English", template_name="Card 1", card_number=1)
    options = ExportOptions(
        deck_name="English",
        mode="card",
        scope_label="all",
        include_metadata=True,
        field_rules={"Basic": FieldRule(title_fields=["Front"], description_fields=[])},
    )

    markdown = render_markdown(notes=[note], cards=[card], options=options)

    assert "## word" in markdown
    assert "Card Number: `1`" in markdown
    assert "Card ID: `99`" in markdown
    assert "Card Template: `Card 1`" in markdown
    assert "meaning" not in markdown
