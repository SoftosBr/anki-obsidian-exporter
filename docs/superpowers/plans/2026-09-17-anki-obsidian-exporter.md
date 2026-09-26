# Anki Obsidian Exporter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create an Anki add-on that exports selected deck content as text-only Markdown for Obsidian.

**Architecture:** Keep Anki-specific code in a thin bridge and UI layer. Keep rendering and text cleanup pure Python so they can be tested outside Anki.

**Tech Stack:** Python 3, Anki add-on API, PyQt through `aqt.qt`, pytest for local unit tests.

**Spec:** `docs/superpowers/specs/2026-09-17-anki-obsidian-exporter-design.md`

## Global Constraints

- Exported Markdown is text only.
- The user chooses the destination folder and file name at export time.
- Field role selection is per note type and allows multiple roles per field.
- Note/card metadata can be included optionally.
- The add-on writes a single `.md` file per export run.

---

### Task 1: Pure Export Core

**Files:**
- Create: `obsidian_exporter/models.py`
- Create: `obsidian_exporter/text.py`
- Create: `obsidian_exporter/exporter.py`
- Test: `tests/test_text.py`
- Test: `tests/test_exporter.py`

**Interfaces:**
- Produces: `html_to_text(value: str) -> str`
- Produces: `render_markdown(notes: list[ExportNote], cards: list[ExportCard], options: ExportOptions) -> str`

- [x] Write failing tests for media stripping, HTML cleanup, note export, and card export.
- [x] Implement the pure functions.
- [x] Run tests and verify they pass.

### Task 2: Anki Bridge and UI

**Files:**
- Create: `obsidian_exporter/anki_bridge.py`
- Create: `obsidian_exporter/ui.py`
- Create: `__init__.py`
- Create: `config.json`
- Create: `config.md`
- Create: `manifest.json`

**Interfaces:**
- Consumes: `ExportOptions`, `render_markdown`
- Produces: `register_actions() -> None`

- [x] Read deck, note type, note, card, field, and tag data from Anki.
- [x] Build a Qt dialog that lets the user select deck, scope, mode, folder, file name, and per-note-type fields.
- [x] Register the export action in Anki's Tools menu.

### Task 3: Documentation and Packaging

**Files:**
- Create: `README.md`
- Create: `pyproject.toml`
- Create: `.gitignore`

- [x] Document install, usage, and packaging.
- [x] Add pytest configuration.
- [x] Run final verification.
