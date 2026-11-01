# Local schema setup

The local API creates tables from the SQLAlchemy models on startup
(`AUTO_CREATE_SCHEMA=true`). This is convenient for a disposable SQLite
development database and does not insert seed/demo records.

The production PostgreSQL schema still needs a reviewed migration history
before deployment. Keep changes represented as versioned migrations and test
them against PostgreSQL; do not rely on `create_all` as a production migration
strategy.
