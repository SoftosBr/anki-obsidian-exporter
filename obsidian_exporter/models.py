from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FieldRule:
    title_fields: list[str] = field(default_factory=list)
    subtitle_fields: list[str] = field(default_factory=list)
    description_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ExportOptions:
    deck_name: str
    mode: str
    scope_label: str
    field_rules: dict[str, FieldRule] = field(default_factory=dict)
    include_tags: bool = True
    include_metadata: bool = False


@dataclass(frozen=True)
class ExportNote:
    note_id: int
    note_type: str
    deck: str
    fields: dict[str, str]
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ExportCard:
    card_id: int
    note_id: int
    deck: str
    template_name: str
    card_number: int | None = None
