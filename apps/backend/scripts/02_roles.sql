--- RUN MIGRATION BEFORE PROCEEDING ---

--- DEMO READER ---
SELECT 'CREATE ROLE demo_reader LOGIN'
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'demo_reader') \gexec

ALTER ROLE demo_reader WITH PASSWORD :'demo_password';
ALTER ROLE demo_reader SET search_path = demo;
GRANT USAGE ON SCHEMA demo TO demo_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA demo TO demo_reader;