from __future__ import annotations

from typing import Any

import httpx

from app.config import get_settings
from app.database import movies_collection, pg_execute, pg_fetchall, pg_fetchone


def write_audit(user_id: int | None, action: str, details: str) -> None:
    pg_execute(
        """
        INSERT INTO audit_logs (user_id, action, details)
        VALUES (%s, %s, %s)
        """,
        (user_id, action, details),
    )


def genre_recommendation_score(preferred: set[str], movie_genres: list[str]) -> float:
    if not movie_genres:
        return 0.0
    preferred_norm = {g.strip().lower() for g in preferred}
    movie_norm = [g.strip().lower() for g in movie_genres]
    matches = sum(1 for g in movie_norm if g in preferred_norm)
    return round((matches / len(movie_norm)) * 100, 2)


def get_recommendations(user_id: int, limit: int = 10) -> list[dict[str, Any]]:
    prefs = pg_fetchall(
        "SELECT preferred_genre FROM user_preferences WHERE user_id = %s",
        (user_id,),
    )
    preferred = {row["preferred_genre"] for row in prefs}

    history = pg_fetchall(
        "SELECT movie_id FROM viewing_history WHERE user_id = %s",
        (user_id,),
    )
    watched = {row["movie_id"] for row in history}

    scored: list[dict[str, Any]] = []
    for movie in movies_collection().find({}, {"_id": 0}):
        movie_id = movie.get("movie_id")
        if movie_id in watched:
            continue
        genres = movie.get("genres") or []
        score = genre_recommendation_score(preferred, genres)
        if score <= 0:
            continue
        scored.append({**movie, "recommendation_score": score})

    scored.sort(key=lambda m: m["recommendation_score"], reverse=True)
    return scored[:limit]


async def tmdb_search(query: str) -> list[dict[str, Any]]:
    settings = get_settings()
    if not settings.tmdb_api_key:
        return []

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            f"{settings.tmdb_base_url}/search/movie",
            params={"api_key": settings.tmdb_api_key, "query": query},
        )
        response.raise_for_status()
        results = response.json().get("results", [])

    mapped = []
    for item in results[:10]:
        poster = item.get("poster_path")
        mapped.append(
            {
                "tmdb_id": item.get("id"),
                "title": item.get("title"),
                "description": item.get("overview") or "",
                "release_year": int(str(item.get("release_date") or "0")[:4] or 0) or None,
                "poster_url": f"https://image.tmdb.org/t/p/w500{poster}" if poster else None,
                "popularity": item.get("popularity"),
            }
        )
    return mapped


async def tmdb_movie_details(tmdb_id: int) -> dict[str, Any] | None:
    settings = get_settings()
    if not settings.tmdb_api_key:
        return None

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            f"{settings.tmdb_base_url}/movie/{tmdb_id}",
            params={"api_key": settings.tmdb_api_key},
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        item = response.json()

    poster = item.get("poster_path")
    genres = [g["name"] for g in item.get("genres", [])]
    return {
        "tmdb_id": item.get("id"),
        "title": item.get("title"),
        "description": item.get("overview") or "",
        "release_year": int(str(item.get("release_date") or "0")[:4] or 0) or None,
        "genres": genres,
        "tags": genres[:3],
        "poster_url": f"https://image.tmdb.org/t/p/w500{poster}" if poster else None,
        "runtime_minutes": item.get("runtime"),
    }


def next_movie_id() -> int:
    doc = movies_collection().find_one(sort=[("movie_id", -1)])
    if not doc:
        return 101
    return int(doc["movie_id"]) + 1


def import_movie(payload: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    tmdb_id = payload.get("tmdb_id")
    if tmdb_id is not None:
        existing = movies_collection().find_one({"tmdb_id": tmdb_id}, {"_id": 0})
        if existing:
            return existing

    movie_id = payload.get("movie_id") or next_movie_id()
    document = {
        "movie_id": int(movie_id),
        "title": payload["title"],
        "genres": payload.get("genres") or [],
        "description": payload.get("description") or "",
        "release_year": payload.get("release_year"),
        "tags": payload.get("tags") or [],
        "poster_url": payload.get("poster_url"),
        "tmdb_id": tmdb_id,
        "runtime_minutes": payload.get("runtime_minutes"),
    }
    movies_collection().insert_one(document)
    document.pop("_id", None)

    write_audit(
        admin_user_id,
        "MOVIE_IMPORT",
        f"Imported movie_id={document['movie_id']} title={document['title']}",
    )
    return document


def ensure_user_access(requester: dict, target_user_id: int) -> None:
    if requester["role"] == "Admin":
        return
    if requester["user_id"] != target_user_id:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's records",
        )


def get_user_or_404(user_id: int) -> dict:
    user = pg_fetchone(
        "SELECT user_id, username, role, created_at FROM users WHERE user_id = %s",
        (user_id,),
    )
    if not user:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
