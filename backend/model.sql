CREATE TABLE IF NOT EXISTS progress (
    id SERIAL PRIMARY KEY,
    mode VARCHAR(50),
    topic TEXT,
    score INT,
    attempt INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
