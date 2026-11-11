-- StreamSphere PoC — PostgreSQL schema
-- Structured user/activity/governance data (polyglot persistence)

CREATE TABLE IF NOT EXISTS users (
    user_id       SERIAL PRIMARY KEY,
    username      VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(20) NOT NULL CHECK (role IN ('Viewer', 'Admin')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_preferences (
    preference_id   SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    preferred_genre VARCHAR(50) NOT NULL,
    UNIQUE (user_id, preferred_genre)
);

CREATE TABLE IF NOT EXISTS viewing_history (
    history_id SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    movie_id   INTEGER NOT NULL,
    watched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ratings (
    rating_id SERIAL PRIMARY KEY,
    user_id   INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    movie_id  INTEGER NOT NULL,
    rating    NUMERIC(2,1) NOT NULL CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, movie_id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    log_id     SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    action     VARCHAR(100) NOT NULL,
    details    TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_preferences_user ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_history_user ON viewing_history(user_id);
CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at DESC);
