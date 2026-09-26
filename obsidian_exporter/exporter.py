from __future__ import annotations

from .models import ExportCard, ExportNote, ExportOptions, FieldRule
from .text import heading_text, html_to_text


def render_markdown(
    notes: list[ExportNote],
    cards: list[ExportCard],
    options: ExportOptions,
) -> str:
    lines: list[str] = []

    lines.extend([f"# Anki Export - {options.deck_name}", ""])

    if options.mode == "card":
        lines.extend(_render_cards(notes, cards, options))
    else:
        lines.extend(_render_notes(notes, options))

    return "\n".join(lines).rstrip() + "\n"


def _render_notes(notes: list[ExportNote], options: ExportOptions) -> list[str]:
    lines: list[str] = []
    for index, note in enumerate(sorted(notes, key=lambda item: item.note_id)):
        if index:
            lines.extend(["---", ""])
        lines.extend(_render_note_content(note, options))
        if options.include_metadata:
            lines.extend(["", f"Note ID: `{note.note_id}`", f"Type: `{note.note_type}`", f"Deck: `{note.deck}`"])
        if options.include_tags and note.tags:
            lines.extend(["", "Tags: " + " ".join(f"#{tag}" for tag in note.tags)])
        lines.append("")
    return lines


def _render_cards(
    notes: list[ExportNote],
    cards: list[ExportCard],
    options: ExportOptions,
) -> list[str]:
    notes_by_id = {note.note_id: note for note in notes}
    lines: list[str] = []
    rendered_count = 0
    for card in sorted(cards, key=lambda item: item.card_id):
        note = notes_by_id.get(card.note_id)
        if note is None:
            continue
        if rendered_count:
            lines.extend(["---", ""])
        lines.extend(_render_note_content(note, options))
        rendered_count += 1
        if options.include_metadata:
            metadata = []
            if card.card_number is not None:
                metadata.append(f"Card Number: `{card.card_number}`")
            metadata.extend(
                [
                    f"Card ID: `{card.card_id}`",
                    f"Card Template: `{card.template_name}`",
                    f"Note ID: `{note.note_id}`",
                    f"Type: `{note.note_type}`",
                    f"Deck: `{card.deck}`",
                ]
            )
            lines.extend(
                [""] + metadata
            )
        if options.include_tags and note.tags:
            lines.extend(["", "Tags: " + " ".join(f"#{tag}" for tag in note.tags)])
        lines.append("")
    return lines


def _render_note_content(note: ExportNote, options: ExportOptions) -> list[str]:
    rule = options.field_rules.get(note.note_type)
    if rule is None:
        rule = FieldRule(
            title_fields=[next(iter(note.fields.keys()), "")],
            description_fields=list(note.fields.keys())[1:],
        )

    lines: list[str] = []
    title_values = _field_values(note, rule.title_fields)
    if title_values:
        for title in title_values:
            lines.append(f"## {heading_text(title)}")
    else:
        lines.append(f"## Note {note.note_id}")

    subtitle_values = _field_values(note, rule.subtitle_fields)
    if subtitle_values:
        lines.append("")
        for subtitle in subtitle_values:
            lines.append(f"### {html_to_text(subtitle)}")

    description_values = [html_to_text(value) for value in _field_values(note, rule.description_fields)]
    description_values = [value for value in description_values if value]
    if description_values:
        lines.append("")
        lines.append("\n\n".join(description_values))

    return lines


def _field_values(note: ExportNote, field_names: list[str]) -> list[str]:
    return [note.fields[field_name] for field_name in field_names if field_name in note.fields]
