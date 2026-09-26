# Anki Obsidian Exporter Design

## Goal

Build an Anki add-on that exports cards or notes from a selected deck to a Markdown file for Obsidian.

## Requirements

- Let the user choose the destination folder at export time.
- Let the user choose the Markdown file name at export time.
- Export text only. External links remain functional. Images, audio, video, bracket artifacts, and other media references are removed.
- Support exporting all content from a deck or recently added content with an `added:N` search.
- Support note-based export and card-based export.
- Let the user choose one or more roles for each field for each note type: title, subtitle, or description.
- Let the user choose whether note/card metadata is included in the Markdown.
- Generate one Markdown file per export.

## Architecture

- `obsidian_exporter/models.py` contains plain dataclasses for notes, cards, export options, and note type field selections.
- `obsidian_exporter/text.py` converts Anki HTML field content into plain Markdown-friendly text and strips media.
- `obsidian_exporter/exporter.py` renders Markdown from normalized notes/cards.
- `obsidian_exporter/anki_bridge.py` reads Anki collection data and converts it into the normalized model.
- `obsidian_exporter/ui.py` owns Qt dialogs and the Anki menu action.
- `__init__.py` registers the add-on with Anki.

## Testing

Unit tests cover the pure Python text conversion and Markdown rendering. Anki UI integration is kept thin and documented for manual testing inside Anki.
