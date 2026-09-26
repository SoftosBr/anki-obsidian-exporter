# Anki Obsidian Exporter

Anki add-on that exports the selected deck to a text-only Markdown file for Obsidian.

## Features

- Choose the deck to export.
- Choose whether to export by note or by card.
- Export all deck content or only recently added content with Anki's `added:N` search.
- Select the output folder at export time.
- Select the Markdown file name at export time.
- Select one or more roles for each field in each note type: title, subtitle, and description.
- Optionally include note/card metadata such as note ID, note type, deck, card ID, and card template.
- Keep external links functional while stripping images, audio, video, embeds, iframes, `[sound:...]` references, and bracket artifacts such as `Word[text1]:;[text2]`.
- Generate one `.md` file per export.

## Install for local testing

1. Open Anki.
2. Go to `Tools > Add-ons > View Files`.
3. Create a folder named `anki_obsidian_exporter`.
4. Copy this project's files into that folder.
5. Restart Anki.

The menu item will appear at:

`Tools > Export deck to Obsidian Markdown`

## Usage

1. Open Anki.
2. Click `Tools > Export deck to Obsidian Markdown`.
3. Select the deck.
4. Select `Export by note` or `Export by card`.
5. Choose `All` or `Recently added`.
6. Choose the destination folder and file name.
7. Choose whether to include metadata.
8. Check one or more roles for each field in each note type:
   - `Title`: render this field as `##`.
   - `Subtitle`: render this field as `###`.
   - `Description`: render this field as body text.
9. Click `Export`.

When more than one description field is selected, the add-on separates them with one blank line.

## Packaging

From inside this directory:

```bash
zip -r ../anki-obsidian-exporter.ankiaddon . -x '__pycache__/*' '*.pyc' '.pytest_cache/*'
```

Install the generated `.ankiaddon` with Anki's add-on installer.

## Local tests

This repository includes a dependency-free runner:

```bash
python tests/run.py
```

If `pytest` is available:

```bash
python -m pytest -q
```
