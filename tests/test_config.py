from obsidian_exporter.config import DeckSettings, config_with_deck_settings, deck_settings_from_config
from obsidian_exporter.models import FieldRule


def test_deck_settings_fall_back_to_legacy_global_defaults():
    config = {
        "default_export_folder": "/tmp/exports",
        "default_file_name": "anki.md",
    }

    settings = deck_settings_from_config(config, "English")

    assert settings == DeckSettings(
        folder="/tmp/exports",
        file_name="anki.md",
        mode="note",
        scope="all",
        added_days=7,
        include_metadata=False,
        field_rules={},
    )


def test_config_with_deck_settings_preserves_other_decks_and_serializes_fields():
    config = {
        "default_file_name": "anki.md",
        "deck_settings": {
            "Spanish": {
                "folder": "/tmp/spanish",
                "file_name": "spanish.md",
            }
        },
    }
    settings = DeckSettings(
        folder="/tmp/english",
        file_name="english.md",
        mode="card",
        scope="recent",
        added_days=14,
        include_metadata=True,
        field_rules={
            "Basic": FieldRule(
                title_fields=["Front"],
                subtitle_fields=["Pronunciation"],
                description_fields=["Back", "Example"],
            )
        },
    )

    updated = config_with_deck_settings(config, "English", settings)

    assert updated["deck_settings"]["Spanish"]["file_name"] == "spanish.md"
    assert updated["deck_settings"]["English"] == {
        "folder": "/tmp/english",
        "file_name": "english.md",
        "mode": "card",
        "scope": "recent",
        "added_days": 14,
        "include_metadata": True,
        "field_rules": {
            "Basic": {
                "title_fields": ["Front"],
                "subtitle_fields": ["Pronunciation"],
                "description_fields": ["Back", "Example"],
            }
        },
    }
    assert "English" not in config.get("deck_settings", {})


def test_deck_settings_are_loaded_for_the_selected_deck_only():
    config = {
        "deck_settings": {
            "English": {
                "folder": "/tmp/english",
                "file_name": "english.md",
                "mode": "card",
                "scope": "recent",
                "added_days": 30,
                "include_metadata": True,
                "field_rules": {
                    "Basic": {
                        "title_fields": ["Front"],
                        "subtitle_fields": [],
                        "description_fields": ["Back"],
                    }
                },
            },
            "Spanish": {
                "folder": "/tmp/spanish",
                "file_name": "spanish.md",
                "mode": "note",
            },
        }
    }

    settings = deck_settings_from_config(config, "English")

    assert settings == DeckSettings(
        folder="/tmp/english",
        file_name="english.md",
        mode="card",
        scope="recent",
        added_days=30,
        include_metadata=True,
        field_rules={
            "Basic": FieldRule(
                title_fields=["Front"],
                subtitle_fields=[],
                description_fields=["Back"],
            )
        },
    )
