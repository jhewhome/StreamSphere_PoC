"""Seed PostgreSQL sample users/activity and MongoDB movie catalog."""

from __future__ import annotations

from app.auth import hash_password
from app.database import movies_collection, pg_conn, pg_fetchone
from app.services import write_audit

SAMPLE_MOVIES = [
    {
        "movie_id": 101,
        "title": "Neon Horizon",
        "genres": ["Action", "Science Fiction"],
        "description": "A courier races across a neon megacity to deliver a forbidden AI core.",
        "release_year": 2024,
        "tags": ["adventure", "future"],
        "poster_url": "https://picsum.photos/seed/neon/300/450",
    },
    {
        "movie_id": 102,
        "title": "Quiet Harbor",
        "genres": ["Drama", "Romance"],
        "description": "Two strangers reconnect in a coastal town after a decade apart.",
        "release_year": 2022,
        "tags": ["feel-good", "coastal"],
        "poster_url": "https://picsum.photos/seed/harbor/300/450",
    },
    {
        "movie_id": 103,
        "title": "Cipher Room",
        "genres": ["Thriller", "Mystery"],
        "description": "An analyst discovers a secret messaging network inside a bank.",
        "release_year": 2023,
        "tags": ["suspense", "crime"],
        "poster_url": "https://picsum.photos/seed/cipher/300/450",
    },
    {
        "movie_id": 104,
        "title": "Orbit Kids",
        "genres": ["Animation", "Family", "Adventure"],
        "description": "Children on a space station learn to navigate friendship and gravity.",
        "release_year": 2021,
        "tags": ["space", "kids"],
        "poster_url": "https://picsum.photos/seed/orbit/300/450",
    },
    {
        "movie_id": 105,
        "title": "Iron Circuit",
        "genres": ["Action", "Thriller"],
        "description": "A retired racer is pulled into an underground autonomous-car league.",
        "release_year": 2020,
        "tags": ["racing", "tech"],
        "poster_url": "https://picsum.photos/seed/iron/300/450",
    },
    {
        "movie_id": 106,
        "title": "Garden of Echoes",
        "genres": ["Drama", "Fantasy"],
        "description": "A botanist hears memories blooming from an abandoned greenhouse.",
        "release_year": 2019,
        "tags": ["magical", "nature"],
        "poster_url": "https://picsum.photos/seed/garden/300/450",
    },
    {
        "movie_id": 107,
        "title": "Midnight Protocol",
        "genres": ["Science Fiction", "Thriller"],
        "description": "A cybersecurity team races a zero-day exploit across three continents.",
        "release_year": 2024,
        "tags": ["cyber", "race"],
        "poster_url": "https://picsum.photos/seed/midnight/300/450",
    },
    {
        "movie_id": 108,
        "title": "Sunlit Kitchen",
        "genres": ["Comedy", "Romance"],
        "description": "Rival food-truck owners are forced to share one kitchen for a festival.",
        "release_year": 2018,
        "tags": ["food", "funny"],
        "poster_url": "https://picsum.photos/seed/kitchen/300/450",
    },
    {
        "movie_id": 109,
        "title": "Deep Archive",
        "genres": ["Mystery", "Drama"],
        "description": "A librarian finds a sealed collection that rewrites a city's history.",
        "release_year": 2022,
        "tags": ["books", "secrets"],
        "poster_url": "https://picsum.photos/seed/archive/300/450",
    },
    {
        "movie_id": 110,
        "title": "Cascade Point",
        "genres": ["Action", "Adventure"],
        "description": "Climbers chase a lost survey beacon through collapsing glaciers.",
        "release_year": 2023,
        "tags": ["survival", "outdoors"],
        "poster_url": "https://picsum.photos/seed/cascade/300/450",
    },
    {
        "movie_id": 111,
        "title": "Pixel Hearts",
        "genres": ["Animation", "Romance", "Comedy"],
        "description": "Two game NPCs fall in love while players keep resetting the world.",
        "release_year": 2021,
        "tags": ["games", "meta"],
        "poster_url": "https://picsum.photos/seed/pixel/300/450",
    },
    {
        "movie_id": 112,
        "title": "Northern Signal",
        "genres": ["Science Fiction", "Drama"],
        "description": "Researchers decode an aurora pattern that mirrors human memory.",
        "release_year": 2020,
        "tags": ["aurora", "science"],
        "poster_url": "https://picsum.photos/seed/northern/300/450",
    },
    {
        "movie_id": 113,
        "title": "Glass Market",
        "genres": ["Thriller", "Crime"],
        "description": "An undercover agent infiltrates a luxury auction of stolen artifacts.",
        "release_year": 2024,
        "tags": ["heist", "undercover"],
        "poster_url": "https://picsum.photos/seed/glass/300/450",
    },
    {
        "movie_id": 114,
        "title": "Paper Planets",
        "genres": ["Family", "Fantasy", "Adventure"],
        "description": "Siblings fold a paper map that opens doors to miniature worlds.",
        "release_year": 2017,
        "tags": ["whimsical", "siblings"],
        "poster_url": "https://picsum.photos/seed/paper/300/450",
    },
    {
        "movie_id": 115,
        "title": "Static Choir",
        "genres": ["Horror", "Mystery"],
        "description": "A radio host receives songs that predict accidents before they happen.",
        "release_year": 2023,
        "tags": ["radio", "dread"],
        "poster_url": "https://picsum.photos/seed/static/300/450",
    },
    {
        "movie_id": 116,
        "title": "Blue Commute",
        "genres": ["Drama", "Comedy"],
        "description": "Daily train riders form an unlikely support group during delays.",
        "release_year": 2019,
        "tags": ["city", "ensemble"],
        "poster_url": "https://picsum.photos/seed/blue/300/450",
    },
    {
        "movie_id": 117,
        "title": "Ash and Alloy",
        "genres": ["Action", "Fantasy"],
        "description": "A blacksmith forges a blade that binds rival clans into one army.",
        "release_year": 2022,
        "tags": ["epic", "forge"],
        "poster_url": "https://picsum.photos/seed/ash/300/450",
    },
    {
        "movie_id": 118,
        "title": "Latency",
        "genres": ["Science Fiction", "Thriller"],
        "description": "A pilot experiences delayed reality after a faster-than-light jump.",
        "release_year": 2025,
        "tags": ["time", "space"],
        "poster_url": "https://picsum.photos/seed/latency/300/450",
    },
    {
        "movie_id": 119,
        "title": "Harbor Lights",
        "genres": ["Romance", "Drama"],
        "description": "A ferry captain and a visiting chef rebuild a festival from scratch.",
        "release_year": 2021,
        "tags": ["festival", "coastal"],
        "poster_url": "https://picsum.photos/seed/lights/300/450",
    },
    {
        "movie_id": 120,
        "title": "Wildcard Circuit",
        "genres": ["Action", "Comedy"],
        "description": "Mismatched hackers enter a robotics tournament with a homemade bot.",
        "release_year": 2024,
        "tags": ["robots", "team"],
        "poster_url": "https://picsum.photos/seed/wildcard/300/450",
    },
    {
        "movie_id": 121,
        "title": "Silent Gallery",
        "genres": ["Mystery", "Thriller"],
        "description": "Paintings begin rearranging themselves after closing hours.",
        "release_year": 2018,
        "tags": ["art", "night"],
        "poster_url": "https://picsum.photos/seed/gallery/300/450",
    },
    {
        "movie_id": 122,
        "title": "Coral Run",
        "genres": ["Adventure", "Family"],
        "description": "Young divers race to map a reef before a storm season begins.",
        "release_year": 2020,
        "tags": ["ocean", "youth"],
        "poster_url": "https://picsum.photos/seed/coral/300/450",
    },
    {
        "movie_id": 123,
        "title": "Afterimage",
        "genres": ["Drama", "Science Fiction"],
        "description": "A photographer captures moments that belong to alternate timelines.",
        "release_year": 2023,
        "tags": ["photo", "timeline"],
        "poster_url": "https://picsum.photos/seed/afterimage/300/450",
    },
    {
        "movie_id": 124,
        "title": "Market Day",
        "genres": ["Comedy", "Family"],
        "description": "A chaotic weekend market becomes a neighborhood reconciliation.",
        "release_year": 2016,
        "tags": ["community", "funny"],
        "poster_url": "https://picsum.photos/seed/market/300/450",
    },
    {
        "movie_id": 125,
        "title": "Redshift Courier",
        "genres": ["Action", "Science Fiction"],
        "description": "Interplanetary mail must arrive before a colony loses contact.",
        "release_year": 2025,
        "tags": ["space", "delivery"],
        "poster_url": "https://picsum.photos/seed/redshift/300/450",
    },
    {
        "movie_id": 126,
        "title": "Broken Metronome",
        "genres": ["Drama", "Music"],
        "description": "A pianist recovers from injury by teaching street musicians.",
        "release_year": 2019,
        "tags": ["music", "healing"],
        "poster_url": "https://picsum.photos/seed/metronome/300/450",
    },
    {
        "movie_id": 127,
        "title": "Fog Line",
        "genres": ["Horror", "Thriller"],
        "description": "Highway patrol finds a stretch of road that loops after midnight.",
        "release_year": 2022,
        "tags": ["road", "loop"],
        "poster_url": "https://picsum.photos/seed/fog/300/450",
    },
    {
        "movie_id": 128,
        "title": "Canvas City",
        "genres": ["Animation", "Adventure", "Fantasy"],
        "description": "Street art comes alive and asks kids to finish an unfinished mural.",
        "release_year": 2021,
        "tags": ["art", "city"],
        "poster_url": "https://picsum.photos/seed/canvas/300/450",
    },
    {
        "movie_id": 129,
        "title": "Ledger of Dust",
        "genres": ["Western", "Drama"],
        "description": "A clerk inherits a mine claim and a town's unfinished conflicts.",
        "release_year": 2017,
        "tags": ["frontier", "legacy"],
        "poster_url": "https://picsum.photos/seed/ledger/300/450",
    },
    {
        "movie_id": 130,
        "title": "Signal Bloom",
        "genres": ["Science Fiction", "Romance"],
        "description": "Two operators fall in love while maintaining an orbital garden.",
        "release_year": 2024,
        "tags": ["orbit", "garden"],
        "poster_url": "https://picsum.photos/seed/bloom/300/450",
    },
]


USERS = [
    {
        "username": "admin",
        "password": "admin123",
        "role": "Admin",
        "genres": ["Action", "Science Fiction", "Thriller"],
    },
    {
        "username": "viewer1",
        "password": "viewer123",
        "role": "Viewer",
        "genres": ["Action", "Adventure", "Comedy"],
    },
    {
        "username": "viewer2",
        "password": "viewer123",
        "role": "Viewer",
        "genres": ["Drama", "Romance", "Comedy"],
    },
    {
        "username": "viewer3",
        "password": "viewer123",
        "role": "Viewer",
        "genres": ["Mystery", "Thriller", "Horror"],
    },
    {
        "username": "viewer4",
        "password": "viewer123",
        "role": "Viewer",
        "genres": ["Animation", "Family", "Fantasy"],
    },
]


def seed_movies() -> int:
    collection = movies_collection()
    if collection.count_documents({}) > 0:
        return collection.count_documents({})
    collection.insert_many(SAMPLE_MOVIES)
    collection.create_index("movie_id", unique=True)
    collection.create_index("tmdb_id", sparse=True)
    return len(SAMPLE_MOVIES)


def seed_users_and_activity() -> None:
    existing = pg_fetchone("SELECT user_id FROM users LIMIT 1")
    if existing:
        return

    with pg_conn() as conn:
        with conn.cursor() as cur:
            user_ids: dict[str, int] = {}
            for user in USERS:
                cur.execute(
                    """
                    INSERT INTO users (username, password_hash, role)
                    VALUES (%s, %s, %s)
                    RETURNING user_id
                    """,
                    (user["username"], hash_password(user["password"]), user["role"]),
                )
                user_id = cur.fetchone()["user_id"]
                user_ids[user["username"]] = user_id
                for genre in user["genres"]:
                    cur.execute(
                        """
                        INSERT INTO user_preferences (user_id, preferred_genre)
                        VALUES (%s, %s)
                        """,
                        (user_id, genre),
                    )

            # Sample viewing history and ratings for viewer1
            v1 = user_ids["viewer1"]
            for movie_id in (101, 105, 120):
                cur.execute(
                    """
                    INSERT INTO viewing_history (user_id, movie_id)
                    VALUES (%s, %s)
                    """,
                    (v1, movie_id),
                )
            cur.execute(
                """
                INSERT INTO ratings (user_id, movie_id, rating)
                VALUES (%s, %s, %s), (%s, %s, %s)
                """,
                (v1, 101, 4.5, v1, 105, 4.0),
            )

            v2 = user_ids["viewer2"]
            for movie_id in (102, 108, 119):
                cur.execute(
                    """
                    INSERT INTO viewing_history (user_id, movie_id)
                    VALUES (%s, %s)
                    """,
                    (v2, movie_id),
                )

            conn.commit()

    write_audit(user_ids["admin"], "SEED_COMPLETE", "Sample users, preferences, and activity loaded")


def run_seed() -> dict:
    movie_count = seed_movies()
    seed_users_and_activity()
    return {"movies": movie_count, "status": "ok"}
