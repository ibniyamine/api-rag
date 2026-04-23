# demarer l'application

uvicorn app.app:app --reload

# activation de l'extension vector une fois dans pgAdmin
- CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    question TEXT,
    answer TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stats (
    id SERIAL PRIMARY KEY,
    model TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    cost FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




# apres la connexion sur PgAdmin

\dt  pour les tables inserer

