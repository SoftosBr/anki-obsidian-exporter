from __future__ import annotations

import os
from pathlib import Path

from aqt import mw
from aqt.qt import (
    QAction,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from aqt.utils import showInfo, showWarning, tooltip

from .anki_bridge import collect_deck_selection, current_deck_name, deck_names
from .config import DeckSettings, config_with_deck_settings, deck_settings_from_config
from .exporter import render_markdown
from .models import ExportOptions, FieldRule


ADDON_PACKAGE = __name__.split(".")[0]


class ExportDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Export deck to Obsidian")
        self.resize(720, 620)
        self._field_roles: dict[str, dict[str, dict[str, QCheckBox]]] = {}
        self._config = self._read_config()
        self._build_ui()
        self._deck_changed()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.deck_combo = QComboBox()
        names = deck_names(mw.col)
        self.deck_combo.addItems(names)
        current_name = current_deck_name(mw.col)
        if current_name in names:
            self.deck_combo.setCurrentText(current_name)
        self.deck_combo.currentTextChanged.connect(self._deck_changed)
        form.addRow("Deck", self.deck_combo)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Export by note", "note")
        self.mode_combo.addItem("Export by card", "card")
        form.addRow("Mode", self.mode_combo)

        self.scope_combo = QComboBox()
        self.scope_combo.addItem("All", "all")
        self.scope_combo.addItem("Recently added", "recent")
        self.scope_combo.currentIndexChanged.connect(self._scope_changed)
        form.addRow("Scope", self.scope_combo)

        self.added_days = QSpinBox()
        self.added_days.setMinimum(1)
        self.added_days.setMaximum(3650)
        self.added_days.setValue(7)
        self.added_days.setEnabled(False)
        form.addRow("added:N", self.added_days)

        folder_row = QHBoxLayout()
        self.folder_input = QLineEdit()
        folder_button = QPushButton("Choose")
        folder_button.clicked.connect(self._choose_folder)
        folder_row.addWidget(self.folder_input, 1)
        folder_row.addWidget(folder_button)
        form.addRow("Folder", folder_row)

        self.file_input = QLineEdit("anki-export.md")
        form.addRow("File name", self.file_input)

        self.metadata_check = QCheckBox("Include note ID, note type, deck, and card data")
        self.metadata_check.setChecked(False)
        form.addRow("Metadata", self.metadata_check)

        layout.addLayout(form)

        self.fields_box = QGroupBox("Field roles by note type")
        fields_layout = QVBoxLayout(self.fields_box)
        self.fields_container = QWidget()
        self.fields_layout = QVBoxLayout(self.fields_container)
        self.fields_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.fields_container)
        fields_layout.addWidget(scroll)
        layout.addWidget(self.fields_box, 1)

        buttons = QHBoxLayout()
        refresh_button = QPushButton("Refresh fields")
        refresh_button.clicked.connect(self._reload_fields)
        export_button = QPushButton("Export")
        export_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(refresh_button)
        buttons.addStretch(1)
        buttons.addWidget(cancel_button)
        buttons.addWidget(export_button)
        layout.addLayout(buttons)

    def _read_config(self) -> dict:
        return mw.addonManager.getConfig(ADDON_PACKAGE) or {}

    def _deck_changed(self) -> None:
        self._reload_fields()
        self._apply_deck_settings()

    def _apply_deck_settings(self) -> None:
        settings = deck_settings_from_config(self._config, self.deck_combo.currentText())
        self.folder_input.setText(settings.folder)
        self.file_input.setText(settings.file_name)
        self.metadata_check.setChecked(settings.include_metadata)
        self.added_days.setValue(settings.added_days)
        self._set_combo_data(self.mode_combo, settings.mode)
        self._set_combo_data(self.scope_combo, settings.scope)
        self._scope_changed()
        self._apply_field_rules(settings.field_rules)

    def _apply_field_rules(self, field_rules: dict[str, FieldRule]) -> None:
        for note_type, rule in field_rules.items():
            roles = self._field_roles.get(note_type)
            if roles is None:
                continue
            for field_name, checks in roles.items():
                checks["title"].setChecked(field_name in rule.title_fields)
                checks["subtitle"].setChecked(field_name in rule.subtitle_fields)
                checks["description"].setChecked(field_name in rule.description_fields)

    def _set_combo_data(self, combo: QComboBox, value: str) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _scope_changed(self) -> None:
        self.added_days.setEnabled(self.scope_combo.currentData() == "recent")

    def _choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choose export folder", self.folder_input.text())
        if folder:
            self.folder_input.setText(folder)

    def _reload_fields(self) -> None:
        self._clear_fields()
        deck = self.deck_combo.currentText()
        if not deck:
            return

        try:
            selection = collect_deck_selection(mw.col, deck)
        except Exception as exc:
            showWarning(f"Could not read fields from the selected deck.\n\n{exc}")
            return

        for note_type, fields in selection.field_map.items():
            label = QLabel(f"<b>{note_type}</b>")
            self.fields_layout.addWidget(label)
            self._field_roles[note_type] = {}
            for index, field_name in enumerate(fields):
                row = QHBoxLayout()
                field_label = QLabel(field_name)
                field_label.setMinimumWidth(180)
                title_check = QCheckBox("Title")
                subtitle_check = QCheckBox("Subtitle")
                description_check = QCheckBox("Description")
                title_check.setChecked(index == 0)
                description_check.setChecked(index != 0)
                self._field_roles[note_type][field_name] = {
                    "title": title_check,
                    "subtitle": subtitle_check,
                    "description": description_check,
                }
                row.addWidget(field_label)
                row.addWidget(title_check)
                row.addWidget(subtitle_check)
                row.addWidget(description_check)
                row.addStretch(1)
                self.fields_layout.addLayout(row)
        self.fields_layout.addStretch(1)

    def _clear_fields(self) -> None:
        while self.fields_layout.count():
            item = self.fields_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            child_layout = item.layout()
            if child_layout is not None:
                while child_layout.count():
                    child = child_layout.takeAt(0)
                    child_widget = child.widget()
                    if child_widget is not None:
                        child_widget.deleteLater()
        self._field_roles = {}

    def selected_options(self) -> tuple[ExportOptions, Path]:
        folder = self.folder_input.text().strip()
        file_name = self.file_input.text().strip()
        if not folder:
            raise ValueError("Choose an export folder.")
        if not file_name:
            raise ValueError("Enter a file name.")
        if not file_name.lower().endswith(".md"):
            file_name += ".md"
            self.file_input.setText(file_name)

        settings = self.selected_settings()
        scope_label = settings.scope
        if settings.scope == "recent":
            scope_label = f"added:{settings.added_days}"

        options = ExportOptions(
            deck_name=self.deck_combo.currentText(),
            mode=settings.mode,
            scope_label=scope_label,
            field_rules=settings.field_rules,
            include_metadata=settings.include_metadata,
        )
        return options, Path(folder) / file_name

    def selected_settings(self) -> DeckSettings:
        return DeckSettings(
            folder=self.folder_input.text().strip(),
            file_name=self.file_input.text().strip(),
            mode=self.mode_combo.currentData(),
            scope=self.scope_combo.currentData(),
            added_days=int(self.added_days.value()),
            include_metadata=self.metadata_check.isChecked(),
            field_rules=self._selected_field_rules(),
        )

    def save_current_deck_settings(self) -> None:
        self._config = config_with_deck_settings(
            self._read_config(),
            self.deck_combo.currentText(),
            self.selected_settings(),
        )
        mw.addonManager.writeConfig(ADDON_PACKAGE, self._config)

    def _selected_field_rules(self) -> dict[str, FieldRule]:
        field_rules: dict[str, FieldRule] = {}
        for note_type, roles in self._field_roles.items():
            title_fields = [name for name, checks in roles.items() if checks["title"].isChecked()]
            subtitle_fields = [name for name, checks in roles.items() if checks["subtitle"].isChecked()]
            description_fields = [name for name, checks in roles.items() if checks["description"].isChecked()]
            field_rules[note_type] = FieldRule(
                title_fields=title_fields,
                subtitle_fields=subtitle_fields,
                description_fields=description_fields,
            )
        return field_rules

    def added_days_filter(self) -> int | None:
        if self.scope_combo.currentData() == "recent":
            return int(self.added_days.value())
        return None


def run_export_dialog() -> None:
    dialog = ExportDialog(mw)
    accepted = getattr(QDialog, "Accepted", None)
    if accepted is None:
        accepted = QDialog.DialogCode.Accepted
    if dialog.exec() != accepted:
        return

    try:
        options, output_path = dialog.selected_options()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        selection = collect_deck_selection(mw.col, options.deck_name, dialog.added_days_filter())
        markdown = render_markdown(selection.notes, selection.cards, options)
        output_path.write_text(markdown, encoding="utf-8")
        dialog.save_current_deck_settings()
    except Exception as exc:
        QMessageBox.critical(mw, "Export deck to Obsidian", str(exc))
        return

    tooltip(f"Exported to {os.fspath(output_path)}")
    showInfo(f"Exported file:\n{output_path}")


def register_actions() -> None:
    action = QAction("Export deck to Obsidian Markdown", mw)
    action.triggered.connect(run_export_dialog)
    mw.form.menuTools.addAction(action)
