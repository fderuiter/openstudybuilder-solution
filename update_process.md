# Environment Update Process

This guide describes the technical steps required to deploy a new code
version to an environment. Steps are performed in order.

> **Prerequisites:** The commands below assume that `.env` files are
> in place with valid configuration, including database URLs, API
> endpoints, and credentials.

## 1. Deploy the New Code Version

- Deploy the target release to the environment.
- Ensure the environment is running the same code version as the
  migrations you are about to run.
- Use credentials that have the required write access to the database
  and API.

## 2. Initialize the Database

- Run database initialization **after** the new code is deployed and
  **before** migrations.
- The existing database is **not** cleared; initialization prepares it
  for migration.

From the `neo4j-mdr-db/` directory, run one of:

```sh
python init_neo4j.py   # for a plain Neo4j database
python init_aura.py    # for an Aura database
```

## 3. Run Database/Data Migrations

- Run migrations **after** the database is initialized.
- Migrations are executed against the new API version, not the old one.
- Migrations must be run using an execution context with proper
  service-level permissions (not ad-hoc/local DB users if those
  don't exist).
- Do not use export/import as part of migrations — migrations handle
  only schema and required data transformations.

From the `db-schema-migration/` directory, run:

```sh
pipenv run migrate
pipenv run verify
```

Migration and verification scripts are located in
`db-schema-migration/migrations/` and
`db-schema-migration/verifications/`.

## 4. Import Configuration Data

- After migrations, import configuration data:
  - **NeoDash dashboards**
  - **Feature flags**
- These are separate from schema migrations and from
  sponsor/reference data imports.

**NeoDash dashboards** — from the `neo4j-mdr-db/` directory:

```sh
pipenv run import_reports neodash/neodash_reports/
```

Dashboard definitions are stored as JSON files in
`neo4j-mdr-db/neodash/neodash_reports/`.

**Feature flags** — from the `studybuilder-import/` directory:

```sh
pipenv run import_feature_flags
```

## 5. Verify the Deployment

- After all deployment and import steps are complete, verify that the
  API and database are functioning correctly.
- Verification checks include confirming expected studies, library
  data, and codelist/term availability.

## 6. Run Post-Deployment Imports if Needed

- If new functionality requires new reference data (e.g. codelists, sponsor data):
  - Run these imports **after** deployment, migrations, config
    imports, and verification are complete.
  - Treat them as separate, explicit steps from migrations.

Import scripts are located in `studybuilder-import/` and invoked via
`pipenv`. For example, to import a specific codelist, from the
`studybuilder-import/` directory:

```sh
pipenv run codelistterms1 "Example Codelist"
pipenv run codelistterms2 "Example Codelist"
```

A full list of available import commands is defined in the
`studybuilder-import/Pipfile`.

## 7. Do Not Skip Versions

- Upgrade sequentially through versions.
- For each version:
  1. Deploy that version of the code.
  2. Run its corresponding migrations.
- Migrations are written and tested assuming they run with the
  matching code version.

