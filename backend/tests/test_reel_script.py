import copy

import pytest

from app.agent.reel_script import (
    normalize_reel,
    parse_reel_json,
    render_reel_text,
    validate_reel,
)

NAME = "LED Desk Lamp"
PRICE = 899

GOOD = {
    "scenes": [
        {"voiceover": "Tired of a dim, messy desk?", "on_screen_text": "Fix your desk"},
        {"voiceover": "Meet the LED Desk Lamp, made for desks.", "on_screen_text": "LED Desk Lamp"},
        {"voiceover": "Add LED light to your workspace.", "on_screen_text": "LED light"},
        {"voiceover": "Check out the LED Desk Lamp for \u20b9899.", "on_screen_text": "Check it out"},
    ],
    "caption": "Meet the LED Desk Lamp, a simple way to light up your desk.",
    "hashtags": ["#LEDLamp", "#DeskSetup", "#HomeOffice"],
}


def reel(**changes):
    data = copy.deepcopy(GOOD)
    data.update(changes)
    return data


def with_voiceover(scene_index, text):
    data = copy.deepcopy(GOOD)
    data["scenes"][scene_index]["voiceover"] = text
    return data


def test_good_script_passes():
    result = validate_reel(GOOD, NAME, PRICE)

    assert result["passed"], result["issues"]
    assert 8 <= result["estimated_seconds"] <= 30


def test_stage_directions_and_fake_testimonial_are_rejected():
    # Mirrors the real output the model produced for the Portable Blender.
    bad = with_voiceover(
        2, "[Visual: Customer testimonial] Love it! The best blender I've ever used!"
    )

    result = validate_reel(bad, NAME, PRICE)

    assert not result["passed"]
    assert "stage_directions" in result["matches"]
    assert "testimonial" in result["matches"]


@pytest.mark.parametrize(
    "text",
    [
        "Customers say it changed their evenings.",
        "I love how it lights my desk.",
        "Rated 5 stars by buyers.",
    ],
)
def test_testimonial_wording_is_rejected(text):
    assert "testimonial" in validate_reel(with_voiceover(2, text), NAME, PRICE)["matches"]


def test_quotes_and_emoji_in_voiceover_are_rejected():
    result = validate_reel(with_voiceover(0, "\u201cBest lamp\u201d \U0001F525"), NAME, PRICE)

    assert "quotes" in result["matches"]
    assert "emoji" in result["matches"]


def test_invented_numbers_are_rejected_but_price_is_allowed():
    result = validate_reel(with_voiceover(2, "Lasts 10 hours on one charge."), NAME, PRICE)

    assert "numbers" in result["matches"]
    assert "10" in result["matches"]["numbers"]

    # The price itself is fine in any common format.
    for text in ("Only 899 rupees.", "Just \u20b9899.", "Only \u20b9899."):
        assert validate_reel(with_voiceover(3, f"{text} LED Desk Lamp."), NAME, PRICE)["passed"]

    assert validate_reel(with_voiceover(3, "LED Desk Lamp for \u20b91,299."), "LED Desk Lamp", 1299)["passed"]
    assert "numbers" in validate_reel(with_voiceover(3, "LED Desk Lamp for \u20b91,299."), NAME, PRICE)["matches"]


def test_no_numbers_allowed_when_price_missing():
    assert "numbers" in validate_reel(GOOD, NAME, None)["matches"]


def test_unsupported_claims_are_rejected():
    for text in ("It is waterproof and powerful.", "Now 20% discount!", "Comes with a warranty."):
        result = validate_reel(with_voiceover(2, text), NAME, PRICE)

        assert "claims" in result["matches"] or "numbers" in result["matches"], text


def test_product_name_must_be_spoken():
    data = copy.deepcopy(GOOD)

    for scene in data["scenes"]:
        scene["voiceover"] = scene["voiceover"].replace("LED Desk Lamp", "this lamp")

    result = validate_reel(data, NAME, PRICE)

    assert not result["passed"]
    assert any("never said" in issue for issue in result["issues"])


def test_structure_rules():
    assert not validate_reel(reel(scenes=GOOD["scenes"][:3]), NAME, PRICE)["passed"]
    assert not validate_reel(reel(hashtags=["#one"]), NAME, PRICE)["passed"]
    assert not validate_reel(reel(caption=""), NAME, PRICE)["passed"]

    long_text = "word " * 25
    assert not validate_reel(with_voiceover(0, long_text), NAME, PRICE)["passed"]

    empty_scene = copy.deepcopy(GOOD)
    empty_scene["scenes"][1]["on_screen_text"] = ""
    assert not validate_reel(empty_scene, NAME, PRICE)["passed"]


def test_shared_responsible_ai_rules_apply():
    result = validate_reel(reel(caption="Guaranteed results for the LED Desk Lamp."), NAME, PRICE)

    assert not result["passed"]


def test_normalize_repairs_hashtags_and_ignores_extra_fields():
    data = normalize_reel(
        {
            "scenes": [{"voiceover": "  hi   there ", "on_screen_text": "x", "extra": 1}],
            "caption": " cap ",
            "hashtags": ["lamp", "#Lamp", " desk setup ", ""],
            "unknown": True,
        }
    )

    assert data["scenes"][0] == {"voiceover": "hi there", "on_screen_text": "x"}
    assert data["hashtags"] == ["#lamp", "#desksetup"]
    assert set(data) == {"scenes", "caption", "hashtags"}
    assert normalize_reel("nonsense") == {"scenes": [], "caption": "", "hashtags": []}


def test_parse_reel_json_variants():
    assert parse_reel_json('{"a": 1}') == {"a": 1}
    assert parse_reel_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_reel_json('Sure! {"a": 1} Hope that helps') == {"a": 1}

    for bad in ("", "no json here", '{"a": ', "[1, 2]"):
        with pytest.raises(ValueError):
            parse_reel_json(bad)


def test_render_text_contains_every_field():
    text = render_reel_text(NAME, GOOD)

    assert "Reel Script: LED Desk Lamp" in text
    assert text.count("Voiceover:") == 4
    assert text.count("On-screen text:") == 4
    assert "Caption:" in text and "#LEDLamp" in text
