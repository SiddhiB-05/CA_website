import asyncio
import json
import os
from datetime import datetime, timezone

import requests
from fastapi import FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    psycopg = None
    dict_row = None


app = FastAPI(title="Biyani Dad & Co. API Backend")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "bhaiyya_website", "bhaiyaa website")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN", "").strip()
GOOGLE_ACCOUNT_ID = os.getenv("GOOGLE_ACCOUNT_ID", "").strip()
GOOGLE_LOCATION_ID = os.getenv("GOOGLE_LOCATION_ID", "").strip()
GOOGLE_SYNC_INTERVAL_SECONDS = int(os.getenv("GOOGLE_SYNC_INTERVAL_SECONDS", "3600"))
GOOGLE_REVIEWS_ENABLED = os.getenv("GOOGLE_REVIEWS_ENABLED", "true").lower() == "true"
SYNC_API_KEY = os.getenv("SYNC_API_KEY", "").strip()

last_sync_status = {
    "ok": False,
    "message": "Sync has not run yet.",
    "review_count": 0,
    "synced_at": None,
}
sync_task = None


STAR_RATINGS = {
    "ONE": 1,
    "TWO": 2,
    "THREE": 3,
    "FOUR": 4,
    "FIVE": 5,
}


CREATE_REVIEWS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS google_reviews (
    review_id TEXT PRIMARY KEY,
    reviewer_name TEXT NOT NULL,
    reviewer_photo_url TEXT,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT NOT NULL DEFAULT '',
    create_time TIMESTAMPTZ,
    update_time TIMESTAMPTZ,
    review_reply TEXT,
    raw JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_google_reviews_latest
ON google_reviews (is_deleted, update_time DESC NULLS LAST, create_time DESC NULLS LAST);
"""


def database_configured():
    return bool(DATABASE_URL)


def google_configured():
    return all(
        [
            GOOGLE_CLIENT_ID,
            GOOGLE_CLIENT_SECRET,
            GOOGLE_REFRESH_TOKEN,
            GOOGLE_ACCOUNT_ID,
            GOOGLE_LOCATION_ID,
        ]
    )


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured.")
    if psycopg is None:
        raise RuntimeError("psycopg is not installed. Run: pip install -r requirements.txt")
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_database():
    if not database_configured():
        return
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_REVIEWS_TABLE_SQL)

def parse_google_time(value):
    if not value:
        return None
    return value.replace("Z", "+00:00")


def relative_time(value):
    if not value:
        return ""
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    delta = datetime.now(timezone.utc) - value.astimezone(timezone.utc)
    days = max(delta.days, 0)
    if days < 1:
        return "today"
    if days < 30:
        return "a day ago" if days == 1 else f"{days} days ago"
    months = days // 30
    if months < 12:
        return "a month ago" if months == 1 else f"{months} months ago"
    years = days // 365
    return "a year ago" if years == 1 else f"{years} years ago"


def rating_to_int(value):
    if isinstance(value, int):
        return max(1, min(5, value))
    if isinstance(value, str):
        value = value.strip().upper()
        if value.isdigit():
            return max(1, min(5, int(value)))
        return STAR_RATINGS.get(value, 5)
    return 5


def review_from_google(raw_review):
    reviewer = raw_review.get("reviewer") or {}
    review_name = raw_review.get("name") or ""
    review_id = raw_review.get("reviewId") or review_name.rsplit("/", 1)[-1]
    reply = raw_review.get("reviewReply") or {}

    return {
        "review_id": review_id,
        "reviewer_name": reviewer.get("displayName") or "Google Reviewer",
        "reviewer_photo_url": reviewer.get("profilePhotoUrl"),
        "rating": rating_to_int(raw_review.get("starRating")),
        "comment": raw_review.get("comment") or "",
        "create_time": parse_google_time(raw_review.get("createTime")),
        "update_time": parse_google_time(raw_review.get("updateTime")),
        "review_reply": reply.get("comment"),
        "raw": raw_review,
    }


def get_google_access_token():
    response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "refresh_token": GOOGLE_REFRESH_TOKEN,
            "grant_type": "refresh_token",
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def fetch_google_reviews():
    if not google_configured():
        raise RuntimeError("Google Business Profile credentials are not configured.")

    access_token = get_google_access_token()
    parent = f"accounts/{GOOGLE_ACCOUNT_ID}/locations/{GOOGLE_LOCATION_ID}"
    url = f"https://mybusiness.googleapis.com/v4/{parent}/reviews"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"pageSize": 50, "orderBy": "updateTime desc"}

    reviews = []
    while True:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        reviews.extend(payload.get("reviews", []))

        next_page_token = payload.get("nextPageToken")
        if not next_page_token:
            break
        params["pageToken"] = next_page_token

    return reviews


def upsert_reviews(reviews):
    if not database_configured():
        raise RuntimeError("DATABASE_URL is not configured.")

    parsed_reviews = [review_from_google(review) for review in reviews]
    fetched_ids = [review["review_id"] for review in parsed_reviews if review["review_id"]]

    with get_connection() as conn:
        with conn.cursor() as cur:
            for review in parsed_reviews:
                if not review["review_id"]:
                    continue
                cur.execute(
                    """
                    INSERT INTO google_reviews (
                        review_id, reviewer_name, reviewer_photo_url, rating, comment,
                        create_time, update_time, review_reply, raw, is_deleted, fetched_at
                    )
                    VALUES (
                        %(review_id)s, %(reviewer_name)s, %(reviewer_photo_url)s, %(rating)s,
                        %(comment)s, %(create_time)s, %(update_time)s, %(review_reply)s,
                        %(raw)s::jsonb, FALSE, NOW()
                    )
                    ON CONFLICT (review_id) DO UPDATE SET
                        reviewer_name = EXCLUDED.reviewer_name,
                        reviewer_photo_url = EXCLUDED.reviewer_photo_url,
                        rating = EXCLUDED.rating,
                        comment = EXCLUDED.comment,
                        create_time = EXCLUDED.create_time,
                        update_time = EXCLUDED.update_time,
                        review_reply = EXCLUDED.review_reply,
                        raw = EXCLUDED.raw,
                        is_deleted = FALSE,
                        fetched_at = NOW();
                    """,
                    {**review, "raw": json.dumps(review["raw"])},
                )

            if fetched_ids:
                cur.execute(
                    """
                    UPDATE google_reviews
                    SET is_deleted = TRUE
                    WHERE review_id <> ALL(%s);
                    """,
                    (fetched_ids,),
                )

    return len(parsed_reviews)


def sync_google_reviews():
    init_database()
    google_reviews = fetch_google_reviews()
    count = upsert_reviews(google_reviews)
    last_sync_status.update(
        {
            "ok": True,
            "message": "Google reviews synced successfully.",
            "review_count": count,
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return last_sync_status


def read_reviews(limit=60):
    if not database_configured() or psycopg is None:
        return []

    init_database()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    review_id,
                    reviewer_name,
                    reviewer_photo_url,
                    rating,
                    comment,
                    create_time,
                    update_time
                FROM google_reviews
                WHERE is_deleted = FALSE
                  AND raw ? 'starRating'
                ORDER BY update_time DESC NULLS LAST, create_time DESC NULLS LAST, fetched_at DESC
                LIMIT %s;
                """,
                (limit,),
            )
            rows = cur.fetchall()

    reviews = []
    for row in rows:
        review_time = row["update_time"] or row["create_time"]
        reviews.append(
            {
                "id": row["review_id"],
                "name": row["reviewer_name"],
                "photoUrl": row["reviewer_photo_url"],
                "text": row["comment"] or "",
                "rating": row["rating"],
                "designation": "Google Reviewer",
                "reviewed": relative_time(review_time),
                "createTime": row["create_time"].isoformat() if row["create_time"] else None,
                "updateTime": row["update_time"].isoformat() if row["update_time"] else None,
            }
        )
    return reviews


async def review_sync_loop():
    while True:
        try:
            await asyncio.to_thread(sync_google_reviews)
        except Exception as exc:
            last_sync_status.update(
                {
                    "ok": False,
                    "message": str(exc),
                    "synced_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        await asyncio.sleep(GOOGLE_SYNC_INTERVAL_SECONDS)


@app.on_event("startup")
async def startup():
    global sync_task
    try:
        init_database()
    except Exception as exc:
        last_sync_status.update({"ok": False, "message": str(exc)})

    if GOOGLE_REVIEWS_ENABLED and database_configured() and google_configured() and psycopg is not None:
        sync_task = asyncio.create_task(review_sync_loop())


@app.on_event("shutdown")
async def shutdown():
    if sync_task:
        sync_task.cancel()


@app.get("/api/reviews")
def get_reviews(limit: int = 60):
    return read_reviews(max(1, min(limit, 100)))


@app.get("/api/reviews/status")
def get_review_status():
    return {
        "databaseConfigured": database_configured(),
        "postgresDriverInstalled": psycopg is not None,
        "googleConfigured": google_configured(),
        "googleSyncEnabled": GOOGLE_REVIEWS_ENABLED,
        "syncIntervalSeconds": GOOGLE_SYNC_INTERVAL_SECONDS,
        "lastSync": last_sync_status,
    }


@app.post("/api/reviews/sync")
async def sync_reviews_now(x_api_key: str | None = Header(default=None)):
    if SYNC_API_KEY and x_api_key != SYNC_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid sync API key.")
    if not database_configured():
        raise HTTPException(status_code=400, detail="DATABASE_URL is not configured.")
    if psycopg is None:
        raise HTTPException(status_code=400, detail="psycopg is not installed.")
    if not google_configured():
        raise HTTPException(status_code=400, detail="Google credentials are not configured.")

    try:
        return await asyncio.to_thread(sync_google_reviews)
    except requests.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    print(f"Warning: Static files directory '{static_dir}' not found.")
