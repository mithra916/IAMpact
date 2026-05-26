CREATE TABLE IF NOT EXISTS enriched_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    "user" VARCHAR(100),
    action VARCHAR(200),
    src_ip VARCHAR(50),
    result TEXT,
    ti_score INT,
    country VARCHAR(10),
    ip_score FLOAT,
    result_flag BOOLEAN,
    alert_score FLOAT,
    prelim_priority VARCHAR(50),
    ti_country VARCHAR(10),
    ti_asn VARCHAR(50)
);
