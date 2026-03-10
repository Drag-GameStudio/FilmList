**Project Overview – FilmList**

---

### 1. Project Title  
**FilmList – A Clean‑Architecture REST API for Movies, Reviews & Wish‑Lists**

---

### 2. Project Goal  
FilmList provides a lightweight, standards‑compliant RESTful service that lets users browse a catalogue of films, write reviews, and maintain personal wish‑lists. The API protects all write operations with JWT‑based authentication, enriches film data from The‑Movie‑Database (TMDB), and stores everything in a relational database via SQLAlchemy. By adhering to a layered (clean) architecture, the codebase remains modular, testable, and easy to evolve as new features or data sources are added.

---

### 3. Core Logic & Principles  

| Layer | Primary Modules | Responsibilities |
|-------|----------------|------------------|
| **Entry** | `app/main.py` | Instantiates the FastAPI ASGI app, registers versioned routers, and triggers the startup lifecycle. |
| **Router (API)** | `app/api/v1/endpoints/*.py` (`auth.py`, `film.py`, `review.py`, `wishlist.py`) | Translates HTTP requests into service calls, injects dependencies (`get_db`, `get_current_user`), and returns Pydantic‑validated responses. |
| **Service** | `AuthService`, `FilmService`, `ReviewService`, `WishListService` | Encapsulates business rules, input validation, and orchestration (e.g., calling the TMDB side‑API to enrich a film before persisting). |
| **Repository** | `BaseRepository`, `UserRepository`, `FilmRepository`, `ReviewRepository`, `WishListRepository` | Provides generic CRUD primitives using a scoped SQLAlchemy session; concrete repositories inherit from `BaseRepository`. |
| **Model** | `app/models/*.py` (`User`, `Film`, `Review`, `WishList`) | Declarative ORM mapping of tables; defines relationships and column constraints. |
| **Schema** | `app/schema/*.py` | Pydantic models that describe request bodies and response payloads, guaranteeing type safety across the stack. |
| **Core** | `core/config.py` (`Settings`), `core/dependencies.py` (`get_db`, `get_current_user`) | Central configuration (DB URL, JWT secret, token TTL) and reusable FastAPI dependencies for DB sessions and authentication. |
| **Database** | `db/database.py` (`engine`, `SessionLocal`, `Base`) | Creates the SQLAlchemy engine, session factory, and holds the metadata used by Alembic migrations. |
| **Utility** | `util/hash.py` | Secure password hashing/verification (e.g., `bcrypt` via PassLib). |
| **Side‑API** | `side_api/tmdb_api.py` | Thin wrapper around TMDB’s public REST endpoints; returns enriched film metadata (poster, overview, release date). |
| **Migrations** | `alembic/versions/*.py` | Version‑controlled DDL scripts; `alembic upgrade`/`downgrade` evolve the schema without data loss. |

#### Architectural Principles  

1. **Layered / Clean Architecture** – Each layer depends only on the one directly below it. Routers never talk to the database; they call services, which in turn use repositories. This separation enables isolated unit‑tests for services (mocked repositories) and for repositories (real DB session).  

2. **Dependency Injection** – FastAPI’s `Depends` mechanism supplies the current DB session (`get_db`) and the authenticated user (`get_current_user`) to any endpoint or service that needs them.  

3. **Stateless JWT Authentication** – On login, `AuthService.authenticate` validates credentials, then creates a signed JWT (`create_access_token`). The token is sent in the `Authorization: Bearer <token>` header; the `get_current_user` dependency decodes it, fetches the corresponding `User` model, and injects the user into the request pipeline.  

4. **Repository Pattern** – `BaseRepository` implements generic `add`, `get`, `list`, `update`, and `delete` methods. Domain‑specific repositories inherit from it, adding custom queries (e.g., `FilmRepository.search_by_title`). This centralises data‑access logic and keeps ORM usage confined to a single place.  

5. **External Data Enrichment** – `FilmService` can optionally call `tmdb_api.search` (or `detail`) to supplement a newly created film with rich metadata (poster URL, synopsis). The side‑API client is stateless and only used inside the service layer, keeping external calls isolated from core business logic.  

6. **Schema‑Driven Contracts** – All inbound payloads are validated against Pydantic schemas before reaching the service layer, and all outbound responses are serialized from Pydantic models, guaranteeing a consistent JSON contract for API consumers.  

7. **Database Migrations with Alembic** – The `Base` metadata is the source of truth for model definitions; Alembic scripts generate the incremental DDL required to keep the production database in sync with code changes.  

#### Typical Request Flow (e.g., “List Films”)  

```
HTTP GET /api/v1/films
   └─ Router → depends on get_current_user (JWT) & get_db
        └─ FilmService.get_all()
               └─ FilmRepository.get_all() → db.session.query(Film)
        └─ (optional) TMDB enrichment → tmdb_api.search(...)
   └─ Returns List[FilmRead] → FastAPI serialises to JSON
```

The same pattern applies to CRUD operations for reviews and wish‑lists, with the service layer enforcing ownership rules (e.g., only the creator may delete a review).

---

### 4. Key Features  

- **JWT‑Protected Authentication** – Secure login, token issuance, and per‑request user resolution.  
- **Film Catalogue** – Create, read, update, delete film records; optional TMDB enrichment for richer metadata.  
- **User Reviews** – CRUD endpoints for textual reviews tied to both a user and a film.  
- **Wish‑List Management** – Users can add/remove films to a personal wish‑list; retrieve the list with pagination.  
- **Layered Architecture** – Clean separation of concerns (router ↔ service ↔ repository ↔ model).  
- **Dependency Injection** – FastAPI `Depends` supplies DB sessions and authentication context automatically.  
- **Database Migration Workflow** – Alembic scripts version the schema; easy upgrades/downgrades.  
- **Typed Contracts** – Pydantic schemas guarantee request validation and response consistency.  
- **Extensible Side‑API Integration** – Centralised TMDB client allows future external data sources without touching core logic.  
- **Comprehensive Unit‑Testing Friendly** – Services can be tested with mock repositories; repositories can be tested against an in‑memory SQLite DB.  

---

### 5. Dependencies  

| Category | Packages | Purpose |
|----------|----------|---------|
| **Web Framework** | `fastapi`, `uvicorn` | ASGI server and routing layer. |
| **ORM & DB** | `sqlalchemy>=2.0`, `alembic` | Declarative models, session handling, migrations. |
| **Data Validation** | `pydantic` (bundled with FastAPI) | Request/response schema validation. |
| **Authentication** | `python-jose[cryptography]` (or `pyjwt`), `passlib[bcrypt]` | JWT creation/verification, password hashing. |
| **External API** | `httpx` or `requests` | HTTP client used by `side_api/tmdb_api.py`. |
| **Configuration** | `pydantic-settings` (or `python-dotenv`) | Load environment variables into `Settings`. |
| **Testing (optional)** | `pytest`, `pytest-asyncio`, `factory-boy` | Unit & integration test suite. |
| **Utilities** | `typing-extensions` (for Python <3.10) | Advanced type hints if needed. |
| **Database Driver** | `psycopg2-binary` (PostgreSQL) or `sqlite3` (development) | DB‑API driver for the chosen RDBMS. |

*All dependencies are declared in `requirements.txt` / `pyproject.toml` and can be installed with `pip install -r requirements.txt`.*

---

**In summary**, FilmList is a well‑structured FastAPI service that follows clean‑architecture best practices, offering authenticated CRUD operations for movies, reviews, and wish‑lists while leveraging external TMDB data and robust database migrations. The layered design, explicit dependency injection, and typed contracts make the codebase maintainable, testable, and ready for future expansion.

## Executive Navigation Tree

- 📂 **Database Migrations**
  - [Alembic Env Config](#alembic-env-config)
  - [Alembic Engine Initialization](#alembic-engine-initialization)
  - [Alembic Config Role](#alembic-config-role)
  - [Alembic Visible Interactions](#alembic-visible-interactions)
  - [Alembic Logic Flow](#alembic-logic-flow)
  - [Alembic Data Contract](#alembic-data-contract)
  - [Migration 2fdbf025e50c](#migration-2fdbf025e50c)
  - [Migration 3253066141e8](#migration-3253066141e8)
  - [Migration 3ba776aed6c5](#migration-3ba776aed6c5)
  - [Upgrade Drop Schema](#upgrade-drop-schema)
  - [Downgrade Rebuild Schema](#downgrade-rebuild-schema)
  - [Downgrade Schema Recreation](#downgrade-schema-recreation)
  - [Migration Upgrade](#migration-upgrade)
  - [Migration Downgrade](#migration-downgrade)
  - [Migration B8613fd000d0 Upgrade](#migration-b8613fd000d0-upgrade)
  - [Migration B8613fd000d0 Downgrade](#migration-b8613fd000d0-downgrade)
  - [Migration C6fa346e2960 Upgrade](#migration-c6fa346e2960-upgrade)
  - [Migration C6fa346e2960 Downgrade](#migration-c6fa346e2960-downgrade)
  - [Migration F63a5988397e Upgrade](#migration-f63a5988397e-upgrade)
  - [Migration F63a5988397e Downgrade](#migration-f63a5988397e-downgrade)
  - [DB URL Config](#db-url-config)

- ⚙️ **API Endpoints**
  - [Auth Endpoints](#auth-endpoints)
  - [Film Endpoints](#film-endpoints)
  - [Review Endpoints](#review-endpoints)
  - [Router Aggregation](#router-aggregation)

- 📄 **Data Models**
  - [Model Film](#model-film)
  - [Model Wishlist](#model-wishlist)
  - [Model Filmsreview](#model-filmsreview)
  - [Model User](#model-user)

- 📂 **Repositories**
  - [Repository Base](#repository-base)
  - [Repository Film](#repository-film)
  - [Repository Review](#repository-review)
  - [Repository User](#repository-user)
  - [Repository Wishlist Update](#repository-wishlist-update)

- 🛠️ **Services**
  - [Review Service](#review-service)
  - [Wishlist Service](#wishlist-service)

- 🌐 **External Integrations**
  - [TMDB API](#tmdb-api)

- 🔧 **Utilities**
  - [Hash Util](#hash-util)

 

<a name="alembic-env-config"></a>
## Alembic Env Configuration & Execution Flow

**Purpose** – Sets up Alembic’s migration context for the **FilmList** project, wiring the SQLAlchemy `Base` metadata and the runtime DB URL from `core.config.settings`.

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `config` | `alembic.context.Config` | Holds Alembic configuration (including `alembic.ini`). | Re‑assigned after import to expose `settings`. |
| `target_metadata` | `MetaData` | Source of schema definitions for autogeneration. | Obtained from `db.database.Base.metadata`. |
| `settings` | `core.config.Settings` | Provides `DB_URL` (the live database connection string). | Injected into Alembic config via `set_main_option`. |
| `engine_from_config` | function | Creates SQLAlchemy engine from the merged config. | Uses `pool.NullPool` to avoid connection pooling in migrations. |
| `run_migrations_offline` / `run_migrations_online` | functions | Execute migrations in offline or online mode respectively. | Offline emits SQL scripts; online runs against a live DB. |

**Logic Flow**

1. Import `Base` from `db.database` and expose its `metadata` as `target_metadata`.  
2. Load `settings` and overwrite Alembic’s `sqlalchemy.url` with `settings.DB_URL`.  
3. Define `run_migrations_offline()` – configures context with URL only, enabling script generation.  
4. Define `run_migrations_online()` – builds an engine via `engine_from_config`, connects, and passes the live connection to `context.configure`.  
5. At module load, evaluate `context.is_offline_mode()` to dispatch to the appropriate runner.  

> **⚠️ Critical Assumption** – The file assumes `core.config.settings` is importable at import time; any import‑time failure aborts migration execution.

**Side‑Effects**

- Prints `Base.metadata.tables.keys()` (debug output).  
- May invoke `context.run_migrations()` which executes the migration scripts defined in each revision file.  

**Dependencies**

- `db.database.Base` (ORM model registry).  
- `core.config.settings` (environment‑specific DB URL).  

This fragment is the bridge between Alembic’s generic tooling and the **FilmList** project’s concrete database configuration. 
<a name="alembic-engine-initialization"></a>
## Alembic Engine Initialization & Mode Dispatch  

**Component Responsibility**  
Bridges Alembic’s generic migration runner with the *FilmList* concrete database configuration. It creates a live SQLAlchemy engine from the project’s `core.config.settings`, binds it to the Alembic migration context, and selects the execution path (offline vs. online) at import time.

**Visible Interactions**  
- Imports `settings` from `core.config` (provides `SQLALCHEMY_DATABASE_URL`).  
- Imports `Base` from `db.database` to expose ORM table metadata.  
- Calls `engine_from_config` (Alembic helper) with the URL from `settings`.  
- Executes `context.configure(connection=engine.connect(), target_metadata=Base.metadata, ...)`.  
- Evaluates `context.is_offline_mode()`; if *True* → runs `run_offline()`, else → runs `run_online()`.  
- Emits a debug `print(Base.metadata.tables.keys())` before configuration.

**Technical Logic Flow**  

1. **Import time** – module loads, pulling `settings` and `Base`.  
2. **Engine creation** – `engine = engine_from_config(config.get_section(config.config_ini_section), prefix='sqlalchemy.')`.  
3. **Debug output** – `print(Base.metadata.tables.keys())`.  
4. **Context configuration** – `context.configure(connection=engine.connect(), target_metadata=Base.metadata, ...)`.  
5. **Mode dispatch** – `if context.is_offline_mode(): run_offline(); else: run_online()`.  
6. **Migration execution** – the selected runner invokes `context.run_migrations()` which processes all revision scripts.

**Data Contract**  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `settings` | `core.config.Settings` | Source of DB URL (`SQLALCHEMY_DATABASE_URL`) | Import‑time availability required; failure aborts migration run. |
| `Base` | `declarative_base()` | Container of ORM table definitions | Used for `target_metadata` to enable autogeneration. |
| `engine` | `sqlalchemy.Engine` | Live DB connection factory | Built via `engine_from_config`. |
| `connection` | `Engine.connect()` | Active DB connection passed to Alembic | Scoped for the migration run. |
| `context` | Alembic `MigrationContext` | Orchestrates migration execution | Determines offline/online mode, runs migrations. |
| `run_offline()` / `run_online()` | Callable | Execute migration scripts in respective mode | Both ultimately call `context.run_migrations()`. |

> **⚠️ Critical Assumption** – The fragment assumes `core.config.settings` can be imported without side‑effects; any import‑time error halts the entire migration process. 
<a name="alembic-config-role"></a>
## Alembic Configuration File – Role & Scope  

The **`alembic.ini`** file defines static settings for Alembic’s migration engine. It is read exclusively by the project‑maintained `env.py` script and by the Alembic CLI (`alembic upgrade`, `alembic revision`, …). Its purpose is to locate migration scripts, configure the database URL, and set logging and post‑write hook behavior for generated revision files. 
<a name="alembic-visible-interactions"></a>
## Interaction Surface with Project Layers  

- **`core/db/database.py`** supplies the actual SQLAlchemy engine; Alembic reads `sqlalchemy.url` only when `env.py` builds its own engine.  
- **CLI Commands** (`alembic upgrade`, `alembic revision`) invoke the Alembic API, which parses this INI to resolve `script_location`, `version_locations`, and `prepend_sys_path`.  
- **`alembic/env.py`** accesses the `[alembic]` and `[loggers]` sections to configure the migration context and logging output. 
<a name="alembic-logic-flow"></a>
## Configuration Flow  

1. Alembic loads `alembic.ini` via `ConfigParser`.  
2. `[alembic]` keys are stored in the `Config` object.  
3. `env.py` calls `config.get_main_option("sqlalchemy.url")` to obtain the DB URL (`sqlite:///test.db`).  
4. Migration script location is resolved from `script_location = %(here)s/alembic`.  
5. Optional hooks (e.g., Black, Ruff) are read from `[post_write_hooks]` but remain disabled by default.  
6. Logging configuration under `[loggers]`, `[handlers]`, `[formatters]` is applied to the Alembic logger hierarchy. 
<a name="alembic-data-contract"></a>
## Data Contract – Configuration Keys  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `script_location` | str | Path to migration scripts | Relative to the ini file (`%(here)s/alembic`). |
| `prepend_sys_path` | str | Sys.path augmentation | Defaults to `.` (project root). |
| `sqlalchemy.url` | str | Database connection URL | Currently `sqlite:///test.db`; can be overridden by env vars in `env.py`. |
| `path_separator` | str | List delimiter for multi‑path options | Set to `os` (uses `os.pathsep`). |
| `timezone` | str (optional) | Timezone for timestamp rendering | Blank → local time. |
| `file_template` | str (optional) | Revision filename pattern | Commented out; defaults to `%(rev)s_%(slug)s`. |
| `revision_environment` | bool | Force env execution on `revision` command | Default `false`. |
| `post_write_hooks.*` | str | Hook definitions for formatting/linting generated scripts | All entries commented out. |
| Logging sections (`[loggers]`, `[handlers]`, `[formatters]`) | dict | Configure Alembic’s log output | Levels: `WARNING` (root), `INFO` (alembic). |

> **Critical:** The file contains **no executable code**; any change to keys directly influences migration behavior. Ensure consistency between this INI and `core/config.Settings` if the DB URL is altered elsewhere. 
<a name="migration-2fdbf025e50c"></a>
## Migration **2fdbf025e50c** – `добавил_таблицу_users1` (Stub)

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `revision` | `str` | Identifier used by Alembic | `'2fdbf025e50c'` |
| `down_revision` | `str` | Parent migration | `'1f52a288fbdd'` |
| `upgrade()` | `Callable[[], None]` | Apply forward changes | Currently `pass` – no schema alteration |
| `downgrade()` | `Callable[[], None]` | Revert changes | Currently `pass` – no schema alteration |

**Responsibility** – Placeholder migration; reserves a revision slot for a future *users1* table creation.  
**Interactions** – Imported by Alembic’s environment script; `op` and `sa` are loaded but not invoked.  
**Logic Flow** – Alembic calls `upgrade()` during `alembic upgrade head`; function returns immediately. 
<a name="migration-3253066141e8"></a>
## Migration **3253066141e8** – `change_password` (Stub)

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `revision` | `str` | Alembic identifier | `'3253066141e8'` |
| `down_revision` | `str` | Parent migration | `'a1a82c21698d'` |
| `upgrade()` | `Callable[[], None]` | Intended password‑field changes | `pass` – no operation |
| `downgrade()` | `Callable[[], None]` | Intended rollback | `pass` – no operation |

**Responsibility** – Reserved for future password column modifications.  
**Visible Interactions** – No DB commands executed; only module import side‑effects (none).  
**Logic Flow** – Alembic invokes `upgrade()`/`downgrade()`; immediate return. 
<a name="migration-3ba776aed6c5"></a>
## Migration **3ba776aed6c5** – `change_filmbase` (Schema Reset)

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `revision` | `str` | Alembic identifier | `'3ba776aed6c5'` |
| `down_revision` | `str` | Parent migration | `'640dd27b82b8'` |
| `upgrade()` | `Callable[[], None]` | Drop legacy tables & indexes | Calls `op.drop_index` / `op.drop_table` for `users`, `films_base`, `films`, `films_reviews`, `session` |
| `downgrade()` | `Callable[[], None]` | Re‑create dropped schema | Uses `op.create_table` & `op.create_index` to restore all tables and indexes |

**Responsibility** – Clears the previous film‑related schema, preparing a clean slate.  
**Visible Interactions** – Directly manipulates the DB via Alembic’s `op` API; no external services.  
**Logic Flow** –  
1. `upgrade()` iterates through drop commands, removing indexes then tables.  
2. `downgrade()` executes creation commands in reverse order, rebuilding columns, constraints, and indexes.  

> **⚠️ Critical Assumption** – The fragment assumes `core.config.settings` can be imported without side‑effects; any import‑time error halts the entire migration process. 
<a name="upgrade-drop-schema"></a>
## Upgrade — Schema Tear‑Down  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `films` | Table | Stores film records | Dropped via `op.drop_table('films')` |
| `wish_list_films` | Table | Junction for wish‑list ↔ film | Dropped after `films` |
| `users` | Table | Application users | Dropped after dependent tables |
| `films_reviews` | Table | Review ↔ film linkage | Dropped after `reviews` |
| `wish_list` | Table | User‑specific wish‑list | Dropped after `users` |
| `session` | Table | JWT session cache | Dropped last |
| `ix_films_id`, `ix_users_id`, `ix_users_username`, `ix_films_reviews_review_id`, `ix_session_id` | Index | Speed up look‑ups | All removed with `op.drop_index` |

> **⚠️ Critical Assumption** – The fragment assumes `core.config.settings` can be imported without side‑effects; any import‑time error halts the entire migration process.

**Logic Flow (upgrade)**  
1. Remove index `ix_films_id` on `films.id`.  
2. Drop tables in dependency order: `films` → `wish_list_films` → `users` (after its indexes) → `films_reviews` → `wish_list` → `session`.  
3. Each `op.drop_*` call is executed sequentially; failures abort further steps. 
<a name="downgrade-rebuild-schema"></a>
## Downgrade — Re‑creation of Columns, Constraints & Indexes  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `session` | Table | Holds session id & `user_id` FK | PK `id`; FK → `users.id` |
| `wish_list` | Table | One‑to‑one list per user | PK `user_id`; FK → `users.id` |
| `films_reviews` | Table | Review data linking users & films | PK `review_id`; FKs → `films.id`, `users.id` |
| `users` | Table | Auth data | Columns `id`, `username`, `_password`; PK `id` |
| `wish_list_films` | Table | Many‑to‑many wish‑list ↔ film | Composite PK (`wish_list_id`, `film_id`); FKs → `wish_list.user_id`, `films.id` |
| `films` | Table | Core film catalogue | Columns `id`, `title`, `image`; PK `id` |
| Indexes (`ix_session_id`, `ix_users_username`, `ix_users_id`, `ix_films_reviews_review_id`, `ix_films_id`) | Index | Restore query performance | Created after their tables |

**Logic Flow (downgrade)**  
1. Re‑create `session` table, then its index `ix_session_id`.  
2. Build `wish_list` (FK to `users`).  
3. Construct `films_reviews` with columns, primary key, and foreign keys; add index on `review_id`.  
4. Create `users` table, then unique index on `username` (`unique=1`) and non‑unique on `id`.  
5. Define `wish_list_films` junction table with composite primary key and foreign keys.  
6. Build `films` table and finally its index on `id`.  

All operations mirror the original schema, ensuring a clean rollback to the pre‑upgrade state. 
<a name="downgrade-schema-recreation"></a>
## Downgrade Schema Recreation

**Responsibility**  
Re‑establish the original database layout that the *upgrade* removed. It rebuilds the `users`, `session`, `films_reviews`, `films_base`, and `films` tables, then restores their indexes and constraints so a full rollback returns the schema to its pre‑upgrade state.

**Visible Interactions**  
- Calls **Alembic operations** (`op.create_table`, `op.create_index`) which emit DDL against the active DB engine.  
- Relies on **SQLAlchemy column objects** for type definitions; no external services are invoked.

**Logic Flow**  
1. `op.create_table('users', …)` → defines `id`, `username`, `_password`; adds PK on `id`.  
2. `op.create_index('ix_users_username', 'users', ['username'], unique=1)` → unique index on `username`.  
3. `op.create_index('ix_users_id', 'users', ['id'], unique=False)` → non‑unique index on `id`.  
4. Recreates `session` with FK to `users.id` and its index.  
5. Builds `films_reviews` with FK to `films_base.id` and `users.id`; PK on `review_id`; adds index on `review_id`.  
6. Constructs `films_base` (single PK `id`) and its index.  
7. Creates `films` with columns `model_id` (PK), `id`, `user_id`, `title`, `image`; FK `user_id → users.id`.  
8. Adds index `ix_films_model_id` on `films.model_id`.

**Data Contract**

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `users.id` | `INTEGER` | Primary Key | Auto‑generated identifier |
| `users.username` | `VARCHAR(256)` | Unique login handle | Unique index (`unique=1`) |
| `users._password` | `VARCHAR(300)` | Stored hash | Nullable per original schema |
| `session.id` | `VARCHAR(32)` | PK & session token | Indexed non‑unique |
| `session.user_id` | `INTEGER` | FK → `users.id` | Nullable |
| `films_reviews.review_id` | `INTEGER` | PK | Indexed non‑unique |
| `films_reviews.user_id` | `INTEGER` | FK → `users.id` | Nullable |
| `films_reviews.film_id` | `INTEGER` | FK → `films_base.id` | Nullable |
| `films_base.id` | `INTEGER` | PK | Indexed non‑unique |
| `films.model_id` | `INTEGER` | PK | Indexed non‑unique |
| `films.id` | `INTEGER` | Optional external ID | Nullable |
| `films.user_id` | `INTEGER` | FK → `users.id` | Nullable |
| `films.title` | `VARCHAR` | Film title | Nullable |
| `films.image` | `VARCHAR` | Image URL | Nullable |

> **Critical assumption:** The downgrade does **not** repopulate data; it only restores table structures and indexes. Any existing data will be lost when the preceding `upgrade` drops the tables. 
<a name="migration-upgrade"></a>
## Upgrade – Schema Teardown  

The `upgrade()` function dismantles the legacy data model by **dropping** all tables and their associated indexes that were introduced in earlier revisions. No data migration or transformation occurs; the operation is purely destructive.

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `ix_films_base_id` | Index | Remove index on `films_base.id` | Auto‑generated name via `op.f` |
| `films_base` | Table | Remove legacy film base table | Contains `id`, `title`, `image` |
| `ix_films_reviews_review_id` | Index | Remove index on `films_reviews.review_id` | |
| `films_reviews` | Table | Remove review association table | Links `review_id` → `films_base.id` |
| `ix_films_model_id` | Index | Remove index on `films.model_id` | |
| `films` | Table | Remove primary film table | Primary key `model_id` |
| `ix_session_id` | Index | Remove index on `session.id` | |
| `session` | Table | Remove user session table | Stores JWT session IDs |
| `ix_users_id` | Index | Remove non‑unique index on `users.id` | |
| `ix_users_username` | Index | Remove unique index on `users.username` | |
| `users` | Table | Remove user account table | Holds credentials |

> **Critical assumption:** The downgrade does **not** repopulate data; it only restores table structures and indexes. Any existing data will be lost when the preceding `upgrade` drops the tables. 
<a name="migration-downgrade"></a>
## Downgrade – Schema Restoration  

The `downgrade()` function recreates the dropped schema, re‑establishing tables, columns, primary keys, foreign keys, and indexes exactly as they existed before the `upgrade`. No default data is inserted.

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `users` | Table | Restores user accounts | Columns: `id` (PK, `INTEGER`), `username` (`VARCHAR(256)`), `_password` (`VARCHAR(300)`); PK on `id` |
| `ix_users_username` | Index | Unique index on `users.username` | `unique=1` |
| `ix_users_id` | Index | Non‑unique index on `users.id` | |
| `session` | Table | Restores session tracking | Columns: `id` (`VARCHAR(32)` PK), `user_id` (`INTEGER` FK → `users.id`) |
| `ix_session_id` | Index | Non‑unique index on `session.id` | |
| `films` | Table | Restores main film entity | Columns: `model_id` (PK, `INTEGER`), `id` (`INTEGER`), `user_id` (`INTEGER` FK → `users.id`), `title` (`VARCHAR`), `image` (`VARCHAR`) |
| `ix_films_model_id` | Index | Non‑unique index on `films.model_id` | |
| `films_reviews` | Table | Restores review linkage | Columns: `review_id` (PK, `INTEGER`), `user_id` (`INTEGER` FK → `users.id`), `film_id` (`INTEGER` FK → `films_base.id`), `content` (`VARCHAR`), `rate` (`INTEGER`) |
| `ix_films_reviews_review_id` | Index | Non‑unique index on `films_reviews.review_id` | |
| `films_base` | Table | Restores base film data | Columns: `id` (PK, `INTEGER`), `title` (`VARCHAR`), `image` (`VARCHAR`) |
| `ix_films_base_id` | Index | Non‑unique index on `films_base.id` | |

**Interaction Summary**  
- `upgrade()` is invoked when migrating **forward** to this revision, ensuring the obsolete schema is removed.  
- `downgrade()` is invoked when rolling **back** to the previous revision, rebuilding the exact former structure to keep compatibility with older application code.  

All operations rely exclusively on Alembic’s `op` API; no external libraries or custom logic are introduced. 
<a name="migration-b8613fd000d0-upgrade"></a>
## `b8613fd000d0_add_film_review` – Upgrade Actions  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `ix_session_id` | Index | **Removed** | `op.drop_index` on table **session** |
| `session` | Table | **Removed** | Stores JWT session IDs |
| `ix_users_id` | Index | **Removed** | Non‑unique index on **users.id** |
| `ix_users_username` | Index | **Removed** | Unique index on **users.username** |
| `users` | Table | **Removed** | Holds user credentials |
| `ix_films_model_id` | Index | **Removed** | Non‑unique index on **films.model_id** |
| `films` | Table | **Removed** | Primary film entity (model‑id PK) |

> **Critical assumption:** The upgrade runs only when migrating forward to this revision; it irrevocably drops the listed tables and indexes, causing permanent data loss for those entities.

**Visible Interactions** – The fragment talks exclusively to Alembic’s `op` API, which in turn emits DDL statements to the underlying PostgreSQL/MySQL engine. No application code is invoked.

**Technical Logic Flow**  
1. `upgrade()` is called by Alembic.  
2. Sequential `op.drop_index` calls remove each index, referencing the target table name.  
3. Sequential `op.drop_table` calls delete the tables after their indexes are gone.  
4. Function returns `None`; the migration is considered successful if no exception is raised. 
<a name="migration-b8613fd000d0-downgrade"></a>
## `b8613fd000d0_add_film_review` – Downgrade Restoration  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `films` | Table | Restored | Columns: `model_id` (PK), `id`, `user_id` (FK → `users.id`), `title`, `image` |
| `ix_films_model_id` | Index | Restored | Non‑unique on `films.model_id` |
| `users` | Table | Restored | Columns: `id` (PK), `username` (`VARCHAR(256)`), `_password` (`VARCHAR(300)`) |
| `ix_users_username` | Index | Restored | Unique on `users.username` |
| `ix_users_id` | Index | Restored | Non‑unique on `users.id` |
| `session` | Table | Restored | Columns: `id` (`VARCHAR(32)` PK), `user_id` (FK → `users.id`) |
| `ix_session_id` | Index | Restored | Non‑unique on `session.id` |

> **Warning:** Downgrade recreates schema **without** repopulating data; any rows lost during the upgrade remain absent.

**Visible Interactions** – Uses `op.create_table` and `op.create_index` to emit DDL that rebuilds the previous schema. No data migration logic is present.

**Technical Logic Flow**  
1. `downgrade()` invoked when rolling back.  
2. `op.create_table` builds `films`, `users`, and `session` with their columns, primary keys, and foreign‑key constraints.  
3. Corresponding `op.create_index` calls re‑establish each index.  
4. Function completes, leaving the database in the pre‑upgrade state. 
<a name="migration-c6fa346e2960-upgrade"></a>
## `c6fa346e2960_change_session_realtions` – Upgrade Actions  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `ix_users_id` | Index | Removed | Non‑unique on `users.id` |
| `ix_users_username` | Index | Removed | Unique on `users.username` |
| `users` | Table | Removed | User accounts table |
| `ix_session_id` | Index | Removed | Non‑unique on `session.id` |
| `session` | Table | Removed | JWT session tracking table |

**Visible Interactions** – Same as above; only Alembic `op` commands are executed.

**Technical Logic Flow** – Mirrors the pattern in `b8613fd000d0` upgrade: drop indexes first, then tables, returning `None`. 
<a name="migration-c6fa346e2960-downgrade"></a>
## `c6fa346e2960_change_session_realtions` – Downgrade Restoration  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `session` | Table | Restored | Columns: `id` (`VARCHAR(32)` PK), `user` (`INTEGER` FK → `users.id`) |
| `ix_session_id` | Index | Restored | Non‑unique on `session.id` |
| `users` | Table | Restored | Columns: `id` (PK), `username` (`VARCHAR(256)`), `_password` (`VARCHAR(300)`) |
| `ix_users_username` | Index | Restored | Unique on `users.username` |
| `ix_users_id` | Index | Restored | Non‑unique on `users.id` |

> **Critical assumption:** The downgrade recreates the exact former schema; no row data is inserted.

**Visible Interactions** – Again limited to Alembic’s DDL generation via `op.create_table`/`op.create_index`.

**Technical Logic Flow** – Re‑creates `session` (with foreign key `user` → `users.id`) and `users`, then reinstates their indexes, completing the rollback. 
<a name="migration-f63a5988397e-upgrade"></a>
## `f63a5988397e_change_films_rel` – Upgrade Operations  

**Component role** – Alembic **upgrade** script that removes the legacy *users*, *films* and *session* tables together with their indexes, preparing the database for a new relational design.

**Visible interactions**  
- `op.drop_index(op.f('ix_session_id'), table_name='session')` – deletes the non‑unique index on `session.id`.  
- `op.drop_table('session')`, `op.drop_table('films')`, `op.drop_table('users')` – emit `DROP TABLE` DDL.  
- `op.drop_index(..., table_name='users')` – removes `ix_users_id` and `ix_users_username` before the tables are dropped.  

**Technical logic flow**  
1. Migration engine invokes `upgrade()`.  
2. Index on `session.id` is removed to avoid dependency errors.  
3. `session` table is dropped.  
4. `films` table is dropped.  
5. User‑related indexes are removed, then the `users` table is dropped.  
6. Function returns `None`; schema now lacks the three tables. 
<a name="migration-f63a5988397e-downgrade"></a>
## `f63a5988397e_change_films_rel` – Downgrade Restoration  

**Component role** – Alembic **downgrade** script that recreates the exact pre‑upgrade schema, allowing a rollback without data restoration.

**Visible interactions**  
- `op.create_table('users', ...)` – issues `CREATE TABLE` with columns `id`, `username`, `_password`.  
- `op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=1)` and `op.create_index(... 'ix_users_id')` – re‑establish user indexes.  
- `op.create_table('films', ...)` – recreates `films` with FK `user_id → users.id`.  
- `op.create_table('session', ...)` – recreates `session` with FK `user_id → users.id`.  
- `op.create_index(op.f('ix_session_id'), 'session', ['id'], unique=False)` – restores session index.

**Technical logic flow**  
1. `downgrade()` is called during a rollback.  
2. `users` table and its indexes are created first (no FK dependencies).  
3. `films` table is created, referencing `users.id`.  
4. `session` table is created, also referencing `users.id`.  
5. Index on `session.id` is added.  
6. Function ends, leaving the DB in its original state.

---

### Data Contract

| Entity | Type   | Role       | Notes |
|--------|--------|------------|-------|
| `users`   | Table   | Restored   | Columns: `id` (PK), `username` (VARCHAR 256, nullable), `_password` (VARCHAR 300, nullable). |
| `ix_users_username` | Index | Restored | Unique on `users.username`. |
| `ix_users_id` | Index | Restored | Non‑unique on `users.id`. |
| `films`   | Table   | Restored   | Columns: `id` (PK), `user_id` (FK → `users.id`), `title` (VARCHAR), `image` (VARCHAR). |
| `session` | Table   | Restored   | Columns: `id` (PK, VARCHAR 32), `user_id` (FK → `users.id`). |
| `ix_session_id` | Index | Restored | Non‑unique on `session.id`. |

> **Warning:** The downgrade script **does not** repopulate any rows; all data removed during the upgrade is lost. 
<a name="db-url-config"></a>
## DB URL Configuration – INI & `core/config.Settings`  

*The actual definition of `core.config.Settings` and any external INI file is **not present** in the supplied fragments.*  
Consequently, the documentation can only state:

- `Settings` is expected to expose a `DATABASE_URL` used by `db/database.py` to create the SQLAlchemy engine.  
- If the DB URL is overridden elsewhere (e.g., via an `.ini` file or environment variable), the change must occur **before** the first import of `engine` so that all `SessionLocal` instances point to the new database.  
- No runtime re‑initialisation of `engine` is shown; altering the URL after import will have **no effect** on existing sessions.  

> **Warning:** Ensure any external configuration is loaded **prior** to `app.db.database` import to avoid silent connection to an outdated database. 
<a name="auth-endpoints"></a>
## Auth Endpoints – Registration, Login, Session Check & Logout  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `UserInfo` | Pydantic model | Request body for **/regist** and **/login** | Contains `username`, `password` (fields not shown) |
| `SessionSearchingParams` | Pydantic model | Parameter for **/logout** | Holds `id` (session identifier) |
| `verify_user` | FastAPI dependency | Auth guard for **/check_auth** and **/logout** | Returns `{"status": bool, "message": str, "user_id": int, "session_id": int}` |
| `AuthService` | Service class | Business logic for `regist`, `login`, `logout` | Instantiated with `UserRepository(SessionLocal)` |
| `UserRepository` | Repository | CRUD on `User` ORM model | Receives a **SQLAlchemy session factory** (`SessionLocal`) |

**Logic Flow**  
1. Endpoint receives request → creates `AuthService` with a fresh `UserRepository`.  
2. `regist` → calls `AuthService.regist(user_info)`. On success returns `{"status":"success","message":created_object}`; on conflict returns error message.  
3. `login` → `AuthService.login(user_params)`. If successful, sets cookie `custom_session_id` with token value; returns success flag.  
4. `check_auth` → dependency `verify_user` validates cookie, returns status/message.  
5. `logout` → after dependency passes, calls `AuthService.logout(SessionSearchingParams(...))`; returns success or error.

**Data Contract**  

| Entity | Input | Output | Side‑effects |
|--------|-------|--------|--------------|
| `/regist` | `UserInfo` JSON | `{status, message}` | Inserts new `User` row if username free |
| `/login` | `UserInfo` JSON, `Response` object | Cookie set + `{status}` | No DB write, reads `User` |
| `/check_auth` | – | `{status}` or `{status, message}` | Reads session store |
| `/logout` | – | `{status}` or `{status, message}` | May delete session record | 
<a name="film-endpoints"></a>
## Film Endpoints – Search, Wish‑List Management & Detail Retrieval  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `verify_user` | Dependency | Auth guard for all routes | Same shape as above |
| `FilmSerchingParams` | Pydantic | Input for **/film/{film_id}** | Holds `id` |
| `AddToWishList` / `WishListCreator` | Pydantic | Payload for wish‑list ops | Carry `user_id`, `film_id` |
| `FilmService` / `WishListService` | Service | Business logic | Instantiated with respective repositories |
| `FilmRepository` / `WishListRepository` | Repository | DB access | Use `SessionLocal` |

**Logic Flow**  
1. Auth dependency validates request.  
2. `search_film` → `FilmService.find_film_by_name(q=query)` → returns list of films.  
3. `add_film_to_wish_list` / `del_film_from_wish_list` → `WishListService` adds or removes record via `WishListRepository`.  
4. `get_wish_list` → retrieves list, reverses order before returning.  
5. `get_info_about_film` → `FilmService.get_info_about_film(FilmSerchingParams(id))` → returns film details.

**Data Contract**  

| Endpoint | Input | Output | Side‑effects |
|----------|-------|--------|--------------|
| `GET /film/search_film` | `query` string | `{status, result: films[]}` | Read‑only |
| `POST /film/wish_list/{film_id}` | Path `film_id` | `{status, result}` or error | Insert wish‑list row |
| `DELETE /film/wish_list/{film_id}` | Path `film_id` | `{status}` or error | Delete wish‑list row |
| `GET /film/wish_list` | – | `{status, result: list}` | Read‑only |
| `GET /film/{film_id}` | Path `film_id` | `{status, result}` or error | Read‑only | 
<a name="review-endpoints"></a>
## Review API – Add / List / My‑Reviews / Delete  

**Component Responsibility**  
`app/api/v1/endpoints/review.py` implements the *public HTTP façade* for user‑generated film reviews. It translates validated FastAPI request data into **service layer** calls (`ReviewService`) and returns plain JSON responses. No ORM objects are touched directly; persistence is delegated to `FilmReviewRepository` via a fresh `SessionLocal` instance per request.

**Visible Interactions**  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `router` | `APIRouter` | Registers `/review` routes under the *v1* router | Tags: `["review"]` |
| `verify_user` | Dependency | Auth guard – extracts session cookie, validates via `AuthService` | Returns `{status, user_id, session_id, message}` |
| `ReviewService` | Service | Business logic for add, get, delete reviews | Constructed with `FilmReviewRepository(SessionLocal)` |
| `FilmReviewRepository` | Repository | Low‑level CRUD using a **new** `SessionLocal` session | Not injected via FastAPI DI, instantiated per endpoint |
| `Review`, `ReviewForAdd`, `ReviewSearchingParams` | Pydantic models | Input validation & response shaping | `ReviewForAdd` supplied by client, `Review` used internally |

**Technical Logic Flow**  

1. **Auth** – `verify_user` reads the `session_id` cookie. If absent, returns `status=False`.  
2. **Add Review (`POST /review/{film_id}`)**  
   - Receives `review_info: ReviewForAdd`.  
   - On successful auth, creates `ReviewService` → `add_review(Review(...))`.  
   - `Review` is built from `review_info` plus `user_id` from auth data.  
   - Service returns `(status, review_object)`.  
   - Success → `{"status":"success","result":review_object}`; otherwise error with auth message.  
3. **List All Reviews (`GET /review/`)**  
   - Optional query params resolved into `ReviewSearchingParams` via FastAPI `Depends()`.  
   - Auth check → service `get_reviews(filters)`.  
   - Returns list under `result`.  
4. **List My Reviews (`GET /review/my`)**  
   - Builds `ReviewSearchingParams(user_id=auth_user_id)` and reuses `get_reviews`.  
   - Returns `results` (note plural key).  
5. **Delete Review (`DELETE /review/{review_id}`)**  
   - Auth check → service `delete_review(ReviewSearchingParams(review_id, user_id))`.  
   - If service reports success → `{"status":"success"}`; else auth error.  

**Endpoint Data Contract**  

| Endpoint | Input | Output | Side‑effects |
|----------|-------|--------|--------------|
| `POST /review/{film_id}` | JSON body `ReviewForAdd` (`film_id`, `content`, `rate`) + session cookie | `{"status":"success","result":<Review>}` or `{"status":"error","message":…}` | Inserts a new `Review` row (if auth passes) |
| `GET /review/` | Query parameters mapped to `ReviewSearchingParams` (optional filters) + session cookie | `{"status":"success","result":[<Review>,…]}` or error | Read‑only DB query |
| `GET /review/my` | Session cookie only | `{"status":"success","results":[<Review>,…]}` or error | Read‑only DB query filtered by current `user_id` |
| `DELETE /review/{review_id}` | Path `review_id` + session cookie | `{"status":"success"}` or `{"status":"error","message":…}` | Deletes matching `Review` row belonging to the authenticated user |

> **⚠️ Assumption Notice** – The fragment creates a *new* `SessionLocal` for each endpoint rather than re‑using the `get_db` dependency; this may lead to multiple concurrent sessions per request. No transaction handling beyond the repository’s `add/commit` is shown. 
<a name="router-aggregation"></a>
## Router Aggregation – v1 Inclusion  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `router` (in `app/api/v1/routes.py`) | `APIRouter` | Top‑level router with prefix `/v1` | Includes `auth.router`, `film.router`, `review.router` |
| `router.tags = router.tags.append("v1")` | Statement | Attempts to add `"v1"` tag to each sub‑router | **Incorrect usage** – `list.append` returns `None`; tags become `None`. No runtime error but tags are lost. |

**Technical Flow**  
- FastAPI app (`app/main.py`) imports `routers` and calls `app.include_router(v1_api_router)`.  
- Each sub‑router (including the **Review** router) becomes reachable under `/v1/...`.  

**Critical Warning** – The tag‑mutation line mutates `router.tags` incorrectly; the intended effect of adding a `"v1"` tag does not occur. This may affect autogenerated OpenAPI documentation.  

---  

*All information above is derived exclusively from the provided source files; no external assumptions have been introduced.* 
<a name="model-film"></a>
## Film Model  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `Film` | `SQLAlchemy` ORM class | Represents a catalogue entry. | Columns: `id` (PK), `title`, `image`. | 
<a name="model-wishlist"></a>
## WishList Model  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `WishList` | `SQLAlchemy` ORM class | Holds a user’s desired films. | PK `user_id` → `users.id`; relationship `films` via association table `wish_list_films`. |
| `wish_list_films` | `Table` | Association between `WishList` and `Film`. | Composite PK (`wish_list_id`, `film_id`). |
| `WishList.get_films()` | method | Returns list of film IDs in the list. | Implements `list(map(lambda obj: obj.id, list(self.films)))`. | 
<a name="model-filmsreview"></a>
## FilmReview Model  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `FilmReview` | `SQLAlchemy` ORM class | Stores a single user rating for a film. | PK `review_id`; FK `user_id` → `users.id`; FK `film_id` → `films.id`; fields `content`, `rate`. |
| `UniqueConstraint('user_id','film_id')` | DB constraint | Enforces one review per user‑film pair. | 
<a name="model-user"></a>
## User & Session Models  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `User` | `SQLAlchemy` ORM class | Authenticated principal. | Columns `id`, `username`, `_password`; property `password` hashes on set; `check_password()` verifies. |
| `Session` | `SQLAlchemy` ORM class | Simple token store for cookie‑based auth. | PK `id` generated via `get_rand_hash`; FK `user_id` → `users.id`. |
| `User.wish_list` | relationship | One‑to‑one `WishList`. | `cascade="all, delete-orphan"`. | 
<a name="repository-base"></a>
## BaseRepository  

Implements generic CRUD using a supplied `session_factory` and target `model`.  

| Method | Input | Output | Side‑effects |
|--------|-------|--------|--------------|
| `get_session()` | – | `Session` instance | Lazily creates per‑repo session. |
| `create(schema)` | Pydantic model | `(bool success, ORM instance)` | `add`, `commit`, `refresh`; rolls back on exception. |
| `read_by_options(schema, eager=False)` | Pydantic filter model | `{"all": list, "query": Query}` | Builds dynamic `filter` chain. |
| `read_by_id(schema, eager=False)` | PK schema | ORM instance or `None` | Calls `read_by_options`. |
| `update_element_by_id(id_schema, change_schema)` | PK + changes | Updated ORM or `None` | Sets attrs, commits, refreshes per field. |
| `delete_object(schema)` | PK schema | `bool` | Deletes and commits. |
| `__del__()` | – | – | Closes open session. | 
<a name="repository-film"></a>
## FilmRepository  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `FilmRepository` | subclass of `BaseRepository` | Dedicated repo for `Film`. | Constructor passes `Film` model to base. | 
<a name="repository-review"></a>
## FilmReviewRepository  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `FilmReviewRepository` | subclass of `BaseRepository` | Handles CRUD for `FilmReview`. | Uses `FilmReview` model. | 
<a name="repository-user"></a>
## UserRepository & SessionRepository  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `UserRepository` | subclass of `BaseRepository` | CRUD for `User`. | |
| `SessionRepository` | subclass of `BaseRepository` | CRUD for `Session`. | |

> **Critical Note** – Each repository maintains its own session via `self.session_factory()`. If instantiated per request, this aligns with the FastAPI `get_db` pattern; otherwise multiple concurrent sessions could arise, potentially causing transaction overlap. 
<a name="repository-wishlist-update"></a>
## `WishListRepository.update_element_films`  

**Component Role**  
Implements an in‑place mutation of a `WishList` entity’s film collection. It bridges the service layer request (an `UpdateWishList` Pydantic model) to the persistence layer, ensuring supplied film IDs are materialized as `Film` ORM objects before being attached to the target `WishList`.

**Visible Interactions**  
- Calls `BaseRepository.get_session()` → obtains a scoped SQLAlchemy `Session`.  
- Invokes `BaseRepository.read_by_id(schema_id)` to fetch the target `WishList`.  
- Uses the injected `session` to query the `Film` model (`session.query(Film).filter(Film.id.in_(value))`).  
- Persists changes via `session.commit()` / `session.refresh()`.  
- Propagates exceptions back as a `(False, None)` tuple.

**Logic Flow**  
1. Acquire a DB session.  
2. Retrieve the existing `WishList` (`curr_object`). If missing → `return None`.  
3. Convert the incoming `update_schema` (`UpdateWishList`) to a plain dict (`model_dump()`).  
4. Iterate over each field:  
   - When the key is `"films"`, replace the list of IDs with the corresponding `Film` ORM instances fetched in step 3.  
   - Assign the resolved value to the attribute on `curr_object`.  
5. Attempt to `commit` the transaction; on success `refresh` the object, otherwise `rollback` and return `(False, None)`.  
6. Return `(True, curr_object)` on success.

**Data Contract**

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `schema_id` | Pydantic model (e.g., `WishListCreator` or ID schema) | Identifier of the `WishList` to update | Passed to `read_by_id`. |
| `update_schema` | `UpdateWishList` (`list[int]` for `films`) | Desired new state for mutable fields | Only `films` currently processed. |
| `session` | `SQLAlchemy Session` | Unit‑of‑work for DB operations | Created lazily per repo. |
| `curr_object` | `WishList` ORM instance | Target entity being mutated | May be `None` if not found. |
| Return | `Tuple[bool, WishList | None]` | Success flag and refreshed object | `None` also returned when target missing. |

> **Warning** – The method assumes `update_schema` contains a `films` list of existing `Film.id` values; missing or invalid IDs will result in an empty collection without explicit validation. 
<a name="review-service"></a>
## ReviewService – Review Management  

**Responsibility** – Orchestrates review creation and retrieval, delegating persistence to `FilmReviewRepository` and film validation to `FilmService`.  

### Data Contract  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `review_info` | `Review` (Pydantic) | Input DTO for `add_review` | Must contain `film_id` |
| `film_review_repository` | `FilmReviewRepository` | Dependency | Provides `create`, `read_by_options`, `delete_object` |
| `film_service` | `FilmService` | Dependency | Validates film existence via `get_info_about_film` |
| Return (add) | `Tuple[bool, Review | None]` | Success flag & persisted ORM object | `False, None` if film missing |
| `review_info` (get) | `ReviewSearchingParams` | Filter DTO for `get_reviews` | Returns list from `read_by_options(...).get("all")` |
| `review_info` (delete) | `ReviewSearchingParams` | Filter DTO for `delete_review` | Returns boolean status |

> **Logic Flow** – `add_review` → `FilmService.get_info_about_film` (fails → abort) → `FilmReviewRepository.create` → return. `get_reviews` simply forwards repository query. `delete_review` forwards deletion request. 
<a name="wishlist-service"></a>
## WishListService – Wish‑list Operations  

**Responsibility** – Handles creation, auto‑creation, and mutation of user wish‑lists, using `WishListRepository` for persistence and `FilmService` for film lookup/creation.  

### Data Contract  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `wish_list_creator` | `WishListCreator` | Input for `create_wish_list` / `auto_create_wish_list` | Contains `user_id` |
| `add_info` / `remove_info` | `AddToWishList` | DTO with `user_id`, `film_id` for mutation | Same schema used for add/remove |
| `wish_list_repository` | `WishListRepository` | Dependency | Provides `create`, `read_by_id`, `update_element_films` |
| `film_service` | `FilmService` | Dependency | Provides `auto_create_film` |
| Return (mutations) | `Tuple[bool, WishList | None]` | Success flag & updated object | `True` with updated object; `False, None` on failure |
| Return (`get_wish_list`) | `Tuple[bool, list[int] | None]` | Success flag & list of film IDs | `False, None` if auto‑creation fails |

> **Logic Flow** – `add_film_to_wish_list` → `FilmService.auto_create_film` (ensures film exists) → `auto_create_wish_list` (ensures wish‑list exists) → merge film IDs → `WishListRepository.update_element_films`.  
> `remove_film_from_wish_list` follows analogous steps, removing the ID before update. 
<a name="tmdb-api"></a>
## TMDB – External Film Data Provider  

**Responsibility** – Wraps TMDB REST endpoints; converts raw JSON to `FilmInfo` Pydantic models via `Movie` helper.  

### Data Contract  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `api_key` | `str` (default from `settings.TMDB_API_KEY`) | Authentication header | Injected at construction |
| `q` | `str` | Query string for `find_the_films` | Returns list of `FilmInfo` |
| `film_id` | `int` | Identifier for `find_film_by_id` | Returns single `FilmInfo` or `None` |
| Return (`find_the_films`) | `list[FilmInfo]` | Collection of matching films | No pagination handling |
| Return (`find_film_by_id`) | `FilmInfo | None` | Exact match or `None` on error |

> **Warning** – The `Movie.image` property uses a double‑quoted string inside an f‑string; syntax error will raise at import time.  

*All interactions are confined to the shown methods; no external caching or retry logic is present.* 
<a name="hash-util"></a>
## Password‑Hash Utilities (`app/util/hash.py`)

**Responsibility** – Provides deterministic helpers for generating random identifiers and securely hashing user passwords. These functions are consumed by the authentication layer (`AuthService`) and any component that needs a unique token (e.g., email verification). No I/O or database access occurs here.

### Data Contract  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `length` | `int` (default = 32) | Input for `get_rand_hash` | Truncates a UUID‑4 hex string. |
| `rnd_hash` | `str` | Return of `get_rand_hash` | Random alphanumeric token, not cryptographically secure. |
| `password` | `str` | Input for `hash_password` | Plain‑text credential. |
| `hashed` | `str` | Return of `hash_password` | bcrypt hash encoded as UTF‑8 string. |
| `plain_password` | `str` | Input for `verify_password` | Candidate password. |
| `hashed_password` | `str` | Input for `verify_password` | bcrypt hash produced by `hash_password`. |
| `bool` | – | Return of `verify_password` | `True` if passwords match, else `False`. |

> **Warning** – `get_rand_hash` uses `uuid.uuid4()`; it is suitable for identifiers but **not** for cryptographic purposes.

### Visible Interactions  

* Imports `uuid` and `bcrypt`; relies on the external **bcrypt** library already present in the environment.  
* Exposes three pure functions; callers receive only the return values—no side effects, no logging, no DB sessions.

### Technical Logic Flow  

1. **`get_rand_hash(length=32)`**  
   1.1 Call `uuid.uuid4()` → generate a UUID‑4 object.  
   1.2 Access `.hex` → 32‑character hexadecimal string.  
   1.3 Slice to `length` (default 32) → `rnd_hash`.  
   1.4 Return `rnd_hash`.  

2. **`hash_password(password)`**  
   2.1 Generate a fresh salt via `bcrypt.gensalt()`.  
   2.2 Encode `password` to UTF‑8 bytes.  
   2.3 Compute bcrypt hash with `bcrypt.hashpw`.  
   2.4 Decode resulting bytes back to UTF‑8 string.  
   2.5 Return the hash string.  

3. **`verify_password(plain_password, hashed_password)`**  
   3.1 Encode both arguments to UTF‑8 bytes.  
   3.2 Call `bcrypt.checkpw`; bcrypt internally extracts the salt from `hashed_password`.  
   3.3 Return the boolean outcome.  

These utilities constitute the low‑level security primitive for the **FilmList** authentication pipeline. 
