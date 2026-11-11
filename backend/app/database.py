from contextlib import contextmanager
from typing import Any, Iterator

import psycopg
from psycopg.rows import dict_row
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from app.config import get_settings

_mongo_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    global _mongo_client
    if _mongo_client is None:
        settings = get_settings()
        _mongo_client = MongoClient(settings.mongo_uri)
    return _mongo_client


def get_mongo_db() -> Database:
    settings = get_settings()
    return get_mongo_client()[settings.mongo_db]


def movies_collection() -> Collection:
    return get_mongo_db()["movies"]


@contextmanager
def pg_conn() -> Iterator[psycopg.Connection]:
    settings = get_settings()
    with psycopg.connect(settings.postgres_dsn, row_factory=dict_row) as conn:
        yield conn


def pg_fetchall(query: str, params: tuple[Any, ...] | None = None) -> list[dict]:
    with pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            return list(cur.fetchall())


def pg_fetchone(query: str, params: tuple[Any, ...] | None = None) -> dict | None:
    with pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchone()


def pg_execute(query: str, params: tuple[Any, ...] | None = None) -> dict | None:
    with pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            row = None
            if cur.description is not None:
                row = cur.fetchone()
            conn.commit()
            return row
