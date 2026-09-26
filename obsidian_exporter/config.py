from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Mapping

from .models import FieldRule


DEFAULT_FILE_NAME = "anki-export.md"
DEFAULT_MODE = "note"
DEFAULT_SCOPE = "all"
DEFAULT_ADDED_DAYS = 7


@dataclass(frozen=True)
class DeckSettings:
    folder: str = ""
    file_name: str = DEFAULT_FILE_NAME
    mode: str = DEFAULT_MODE
    scope: str = DEFAULT_SCOPE
    added_days: int = DEFAULT_ADDED_DAYS
    include_metadata: bool = False
    field_rules: dict[str, FieldRule] = field(default_factory=dict)


def deck_settings_from_config(config: Mapping[str, Any], deck_name: str) -> DeckSettings:
    global_defaults = DeckSettings(
        folder=_string(config.get("default_export_folder"), ""),
        file_name=_string(config.get("default_file_name"), DEFAULT_FILE_NAME),
    )

    deck_settings = config.get("deck_settings")
    if not isinstance(deck_settings, Mapping):
        return global_defaults

    raw_settings = deck_settings.get(deck_name)
    if not isinstance(raw_settings, Mapping):
        return global_defaults

    return DeckSettings(
        folder=_string(raw_settings.get("folder"), global_defaults.folder),
        file_name=_string(raw_settings.get("file_name"), global_defaults.file_name),
        mode=_choice(raw_settings.get("mode"), {"note", "card"}, DEFAULT_MODE),
        scope=_choice(raw_settings.get("scope"), {"all", "recent"}, DEFAULT_SCOPE),
        added_days=_positive_int(raw_settings.get("added_days"), DEFAULT_ADDED_DAYS),
        include_metadata=bool(raw_settings.get("include_metadata", False)),
        field_rules=_field_rules_from_config(raw_settings.get("field_rules")),
    )


def config_with_deck_settings(config: Mapping[str, Any], deck_name: str, settings: DeckSettings) -> dict[str, Any]:
    updated = deepcopy(dict(config))
    deck_settings = updated.get("deck_settings")
    if not isinstance(deck_settings, dict):
        deck_settings = {}
        updated["deck_settings"] = deck_settings

    deck_settings[deck_name] = {
        "folder": settings.folder,
        "file_name": settings.file_name,
        "mode": settings.mode,
        "scope": settings.scope,
        "added_days": settings.added_days,
        "include_metadata": settings.include_metadata,
        "field_rules": _field_rules_to_config(settings.field_rules),
    }
    return updated


def _field_rules_from_config(value: object) -> dict[str, FieldRule]:
    if not isinstance(value, Mapping):
        return {}

    field_rules: dict[str, FieldRule] = {}
    for note_type, raw_rule in value.items():
        if not isinstance(note_type, str) or not isinstance(raw_rule, Mapping):
            continue
        field_rules[note_type] = FieldRule(
            title_fields=_string_list(raw_rule.get("title_fields")),
            subtitle_fields=_string_list(raw_rule.get("subtitle_fields")),
            description_fields=_string_list(raw_rule.get("description_fields")),
        )
    return field_rules


def _field_rules_to_config(field_rules: Mapping[str, FieldRule]) -> dict[str, dict[str, list[str]]]:
    return {
        note_type: {
            "title_fields": list(rule.title_fields),
            "subtitle_fields": list(rule.subtitle_fields),
            "description_fields": list(rule.description_fields),
        }
        for note_type, rule in field_rules.items()
    }


def _string(value: object, default: str) -> str:
    if isinstance(value, str):
        return value
    return default


def _choice(value: object, allowed: set[str], default: str) -> str:
    if isinstance(value, str) and value in allowed:
        return value
    return default


def _positive_int(value: object, default: int) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int) and value > 0:
        return value
    return default


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]
