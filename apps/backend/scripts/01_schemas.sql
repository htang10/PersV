--- PUBLIC ---
-- No role can USAGE/CREATE in the public schema by default — can't even "enter" it
REVOKE ALL ON SCHEMA PUBLIC
FROM
	PUBLIC;

-- No role can SELECT/INSERT/etc. on any existing table currently in public
REVOKE ALL ON ALL TABLES IN SCHEMA PUBLIC
FROM
	PUBLIC;

-- Any future table created in public won't auto-grant access either
ALTER DEFAULT PRIVILEGES IN SCHEMA PUBLIC
REVOKE ALL ON TABLES
FROM
	PUBLIC;

--- SCHEMAS ---
CREATE SCHEMA IF NOT EXISTS MIGRATION;

CREATE SCHEMA IF NOT EXISTS DEMO;