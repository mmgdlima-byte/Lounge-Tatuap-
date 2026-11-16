-- Esquema de referência para PostgreSQL.
CREATE TABLE IF NOT EXISTS "order" (
    id SERIAL PRIMARY KEY,
    region VARCHAR(100) NOT NULL,
    carrier VARCHAR(100) NOT NULL,
    tracking_code VARCHAR(100) UNIQUE NOT NULL,
    order_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Em andamento',
    occurrence VARCHAR(255)
);
