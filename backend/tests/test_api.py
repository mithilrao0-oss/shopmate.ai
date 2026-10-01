import json
import sqlite3
from unittest import mock

import requests
from fastapi.testclient import TestClient

from app.config import DATABASE_PATH
from app.main import app
from tests.test_reel_script import GOOD, NAME, PRICE

client = TestClient(app)


class FakeResponse:
    def __init__(self, text="", status_code=200):
        self._text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code}")

    def json(self):
        return {"response": self._text}


GENERATE_BODY = {
    "product_name": NAME,
    "category": "Home & Office",
    "price": PRICE,
    "content_type": "Reel Script",
    "tone": "Friendly",
    "highlights": ["LED light"],
}


def test_products_have_highlights():
    products = client.get("/api/products").json()

    assert len(products) == 4
    assert all(product["highlights"] for product in products)


def test_generate_reel_retries_with_feedback():
    bad = json.loads(json.dumps(GOOD))
    bad["scenes"][2]["voiceover"] = "Customers say it lasts 10 hours."

    prompts = []
    replies = [json.dumps(bad), json.dumps(GOOD)]

    def fake_post(url, json=None, timeout=None):
        prompts.append(json)
        return FakeResponse(replies[len(prompts) - 1])

    with mock.patch("requests.post", side_effect=fake_post):
        data = client.post("/api/ai/generate", json=GENERATE_BODY).json()

    assert data["attempts"] == 2
    assert data["revision_performed"] is True
    assert data["responsible_ai"]["passed"] is True
    assert len(data["structured"]["scenes"]) == 4
    assert data["estimated_seconds"] > 0
    assert "Voiceover:" in data["response"]

    first, second = prompts
    assert first["format"]["type"] == "object"
    assert "LED light" in first["prompt"]
    assert "rejected" in second["prompt"] and "10 hours" in second["prompt"]


def test_generate_reel_recovers_from_invalid_json():
    replies = ["this is not json", json.dumps(GOOD)]
    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append(json)
        return FakeResponse(replies[len(calls) - 1])

    with mock.patch("requests.post", side_effect=fake_post):
        data = client.post("/api/ai/generate", json=GENERATE_BODY).json()

    assert data["responsible_ai"]["passed"] is True
    assert "not valid JSON" in calls[1]["prompt"]


def test_generate_reel_gives_up_cleanly():
    with mock.patch("requests.post", return_value=FakeResponse("nope")):
        data = client.post("/api/ai/generate", json=GENERATE_BODY).json()

    assert data["attempts"] == 2
    assert data["structured"] is None
    assert data["response"] == ""
    assert data["responsible_ai"]["passed"] is False


def test_generate_reel_falls_back_to_plain_json_format():
    formats = []

    def fake_post(url, json=None, timeout=None):
        formats.append(json["format"])

        if len(formats) == 1:
            return FakeResponse("", status_code=400)

        return FakeResponse(__import__("json").dumps(GOOD))

    with mock.patch("requests.post", side_effect=fake_post):
        data = client.post("/api/ai/generate", json=GENERATE_BODY).json()

    assert formats[0] != "json" and formats[1] == "json"
    assert data["responsible_ai"]["passed"] is True


def test_text_content_types_still_work():
    with mock.patch("requests.post", return_value=FakeResponse("A handy lamp.")):
        data = client.post(
            "/api/ai/generate",
            json={**GENERATE_BODY, "content_type": "Product Caption"},
        ).json()

    assert data["response"] == "A handy lamp."
    assert data["structured"] is None


def test_check_reel_endpoint():
    ok = client.post(
        "/api/ai/check-reel",
        json={"product_name": NAME, "price": PRICE, "payload": GOOD},
    ).json()

    assert ok["passed"] and "Voiceover:" in ok["text"]

    bad_payload = json.loads(json.dumps(GOOD))
    bad_payload["scenes"][0]["voiceover"] = "[Upbeat music playing]"

    bad = client.post(
        "/api/ai/check-reel",
        json={"product_name": NAME, "price": PRICE, "payload": bad_payload},
    ).json()

    assert not bad["passed"]


def test_review_queue_stores_and_returns_structured_reels():
    created = client.post(
        "/api/reviews",
        json={
            "productName": NAME,
            "contentType": "Reel Script",
            "tone": "Friendly",
            "price": PRICE,
            "payload": GOOD,
        },
    )

    assert created.status_code == 200, created.text

    item = created.json()

    assert item["payload"]["hashtags"] == GOOD["hashtags"]
    assert "Scene 1 - Hook" in item["content"]

    listed = [row for row in client.get("/api/reviews").json() if row["id"] == item["id"]]

    assert listed[0]["payload"]["scenes"][3]["on_screen_text"] == "Check it out"


def test_review_queue_rejects_bad_reels():
    bad_payload = json.loads(json.dumps(GOOD))
    bad_payload["scenes"][2]["voiceover"] = "Customers say it lasts 10 hours."

    body = {"productName": NAME, "contentType": "Reel Script", "tone": "Friendly", "price": PRICE}

    assert client.post("/api/reviews", json={**body, "payload": bad_payload}).status_code == 422
    assert client.post("/api/reviews", json=body).status_code == 422


def test_review_queue_still_handles_plain_text():
    body = {"productName": NAME, "contentType": "Product Caption", "tone": "Friendly"}

    ok = client.post("/api/reviews", json={**body, "content": "A handy lamp."})

    assert ok.status_code == 200 and ok.json()["payload"] is None
    assert client.post("/api/reviews", json={**body, "content": "   "}).status_code == 422
    assert client.post("/api/reviews", json={**body, "content": "Guaranteed results!"}).status_code == 422


def test_old_database_gets_payload_column():
    from app.database import initialize_database

    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("DROP TABLE reviews")
    connection.execute(
        "CREATE TABLE reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, productName TEXT NOT NULL, "
        "contentType TEXT NOT NULL, tone TEXT NOT NULL, content TEXT NOT NULL, "
        "status TEXT NOT NULL DEFAULT 'Pending', createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
    )
    connection.execute(
        "INSERT INTO reviews (productName, contentType, tone, content) VALUES ('Old', 'Product Caption', 'Friendly', 'old text')"
    )
    connection.commit()
    connection.close()

    initialize_database()

    rows = client.get("/api/reviews").json()

    assert rows[-1]["content"] == "old text" and rows[-1]["payload"] is None
