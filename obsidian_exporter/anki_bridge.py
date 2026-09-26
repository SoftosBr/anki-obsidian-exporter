from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass

from .models import ExportCard, ExportNote


@dataclass(frozen=True)
class DeckSelection:
    notes: list[ExportNote]
    cards: list[ExportCard]
    field_map: dict[str, list[str]]


def deck_names(col) -> list[str]:
    try:
        return sorted(item.name for item in col.decks.all_names_and_ids())
    except Exception:
        return sorted(col.decks.all_names())


def current_deck_name(col) -> str:
    try:
        return col.decks.current()["name"]
    except Exception:
        names = deck_names(col)
        return names[0] if names else ""


def collect_deck_selection(col, deck_name: str, added_days: int | None = None) -> DeckSelection:
    query = _deck_query(deck_name, added_days)
    card_ids = col.find_cards(query)

    notes_by_id: OrderedDict[int, ExportNote] = OrderedDict()
    cards: list[ExportCard] = []
    field_map: OrderedDict[str, list[str]] = OrderedDict()

    for card_id in card_ids:
        card = col.get_card(card_id)
        note = col.get_note(card.nid)
        note_type_name = _note_type_name(note)
        fields = _note_fields(note)
        field_map.setdefault(note_type_name, list(fields.keys()))

        if note.id not in notes_by_id:
            notes_by_id[note.id] = ExportNote(
                note_id=int(note.id),
                note_type=note_type_name,
                deck=_card_deck_name(col, card, deck_name),
                fields=fields,
                tags=list(getattr(note, "tags", [])),
            )

        cards.append(
            ExportCard(
                card_id=int(card.id),
                note_id=int(note.id),
                deck=_card_deck_name(col, card, deck_name),
                template_name=_template_name(card),
                card_number=int(getattr(card, "ord", 0)) + 1,
            )
        )

    return DeckSelection(notes=list(notes_by_id.values()), cards=cards, field_map=dict(field_map))


def _deck_query(deck_name: str, added_days: int | None) -> str:
    query = f'deck:"{deck_name}"'
    if added_days is not None:
        query += f" added:{added_days}"
    return query


def _note_type_name(note) -> str:
    try:
        return note.note_type()["name"]
    except Exception:
        return note.model()["name"]


def _note_fields(note) -> dict[str, str]:
    try:
        return {name: note[name] for name in note.keys()}
    except Exception:
        model = note.model()
        names = [field["name"] for field in model["flds"]]
        return {name: note[name] for name in names}


def _card_deck_name(col, card, fallback: str) -> str:
    try:
        return col.decks.name(card.did)
    except Exception:
        return fallback


def _template_name(card) -> str:
    try:
        return card.template()["name"]
    except Exception:
        return f"Card {getattr(card, 'ord', 0) + 1}"
