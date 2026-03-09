**Project Overview – FilmList**

---

### 1. Project Title
**FilmList – FastAPI‑Driven Personal Film Catalogue & Review Service**

---

### 2. Project Goal
FilmList provides a robust backend for film‑enthusiasts to discover movies via The‑Movie‑Database (TMDB), store personal collections, write and manage reviews, and keep wish‑lists.  
It solves the common pain‑points of disparate data sources by:

* Centralising user authentication and session handling.  
* Persistently caching film metadata locally to minimise external API calls.  
* Offering a clean, typed API (FastAPI + Pydantic) that can be consumed by web, mobile or CLI clients.  

---

### 3. Core Logic & Principles  

| Layer | Responsibility | Key Concepts |
|-------|----------------|--------------|
| **Entry Point** (`app/main.py`) | Instantiates a `FastAPI` app, configures CORS, creates DB tables, and mounts the versioned router (`/api/v1`). | *Single source of truth* – all request processing starts here. |
| **API Layer** (`app/api/v1/*`) | Declares routers (`auth`, `film`, `review`, `wishlist`) and endpoint functions. Handles request validation, response modelling, and dependency injection (e.g., `verify_user`). | *FastAPI* automatically translates Pydantic schemas into OpenAPI docs. |
| **Service Layer** (`app/services/*`) | Encapsulates business rules: authentication flow, TMDB interaction, review handling, wish‑list management. Each service delegates persistence to the repository layer and calls external APIs when required. | *Separation of concerns* – services are stateless, reusable, and unit‑testable. |
| **Repository Layer** (`app/repositories/*` + `base_repository.py`) | Provides generic CRUD operations, eager‑loading helpers, and concrete repositories for each domain model. Uses a scoped SQLAlchemy session (`SessionLocal`) supplied via FastAPI dependencies. | *Repository pattern* – abstracts ORM details from services. |
| **Database Layer** (`app/db/database.py`) | Sets up the SQLAlchemy engine, session factory, and declarative base (`Base`). Exposes `get_db` dependency for per‑request session handling. | *Unit of work* – each HTTP request gets its own DB transaction. |
| **External API Wrapper** (`app/services/tmdb_side_api.py`) | Thin HTTP client (via `httpx`/`requests`) that calls TMDB *search* and *detail* endpoints, returning typed dictionaries. | *Fail‑fast* – any TMDB error is raised early, allowing the service to decide on fallback logic. |
| **Utility Layer** (`app/util/hash.py`) | Secure password hashing (`bcrypt`/`passlib`) and verification helpers. | *Security* – passwords never stored in plain text. |
| **Configuration** (`app/core/config.py`) | Loads environment variables into a `Settings` object (DB URL, TMDB API key, JWT secrets, etc.). | *Single configuration source* – accessed globally without circular imports. |
| **Schemas** (`app/schemas/*.py`) | Pydantic models that define request and response contracts for every endpoint. | *Data validation* – guarantees inbound data integrity before it reaches the service layer. |

#### Core Functional Flows  

1. **Authentication**  
   *A request hits an endpoint that depends on `verify_user`.*  
   - `verify_user` extracts the session cookie, calls `AuthService.check_auth`.  
   - `AuthService` queries `SessionRepository` → validates session status and returns `{status, user_id}`.  
   - Protected endpoints receive the authenticated `user_id`.  

2. **Film Retrieval / Caching**  
   - `FilmService.get_info_about_film(film_id)` first looks up the film in the local `Film` table via `FilmRepository`.  
   - If missing, the service calls `TMDBSideAPI.find_film_by_id`, persists the result (`FilmRepository.create`), and returns the freshly cached model.  

3. **Review Management**  
   - `ReviewService.add_review` receives a validated `ReviewForAdd` schema and the `user_id`.  
   - It ensures the associated film exists (using the film flow above), then creates a `FilmReview` row through `FilmReviewRepository`.  

4. **Wish‑List Operations**  
   - `WishListService.add_film_to_wish_list` guarantees a `WishList` record for the user (`auto_create_wish_list`) and a `Film` row (`auto_create_film`).  
   - The film ID is merged into the list, deduplicated, and persisted via `WishListRepository.update_element_films`.  

All endpoints follow the same **request → dependency → service → repository → commit → response** pipeline, which yields a predictable, testable flow and isolates side‑effects to the repository layer.

---

### 4. Key Features  

- **User Management**  
  - Register, login, logout, and session validation via secure cookies.  
  - Password hashing with industry‑standard algorithms.  

- **TMDB Integration**  
  - Search movies by title, retrieve detailed information, and automatically cache results locally.  

- **Film Catalogue**  
  - CRUD‑style endpoints for films (read‑only from external source, write‑only for cached entries).  

- **Review System**  
  - Add, list, and delete reviews; each review is uniquely tied to a user‑film pair.  

- **Personal Wish‑List**  
  - Create a per‑user wish‑list, add or remove films, and auto‑populate missing film entries.  

- **Layered Architecture**  
  - Clear separation between API, service, repository, and DB layers, facilitating maintenance and unit testing.  

- **Automatic Database Migrations**  
  - Alembic scripts manage schema evolution, ensuring production‑grade DB versioning.  

- **OpenAPI Documentation**  
  - FastAPI generates interactive Swagger UI & ReDoc automatically from Pydantic schemas.  

- **CORS & Security**  
  - Configurable CORS middleware; session cookies are `HttpOnly` and `Secure` (when deployed over HTTPS).  

---

### 5. Dependencies  

| Category | Library / Tool | Purpose |
|----------|----------------|---------|
| **Web Framework** | `fastapi` | ASGI‑compatible API layer, automatic validation, OpenAPI generation. |
| **Server** | `uvicorn[standard]` | Production ASGI server. |
| **ORM** | `sqlalchemy` (>=1.4) | Declarative models, session management, migrations. |
| **Migrations** | `alembic` | Database schema version control. |
| **Pydantic** | `pydantic` (>=2.0) | Data validation & serialization. |
| **Authentication & Hashing** | `passlib[bcrypt]` or `bcrypt` | Secure password hashing and verification. |
| **HTTP Client** | `httpx` (or `requests`) | Communicate with TMDB external API. |
| **Environment Management** | `python-dotenv` | Load `.env` files into `Settings`. |
| **CORS Middleware** | `fastapi[all]` (includes `starlette`) | Enable cross‑origin requests. |
| **Testing** *(optional but typical)* | `pytest`, `pytest-asyncio`, `httpx` (test client) | Unit and integration tests. |
| **Database Driver** | `psycopg2-binary` (PostgreSQL) / `asyncpg` (if async) | Connect to the relational DB. |
| **Logging** | `loguru` or standard `logging` | Structured application logs. |

*All dependencies are declared in `requirements.txt` / `pyproject.toml` and pinned to specific versions to guarantee reproducible builds.*

---

**FilmList** thus delivers a clean, maintainable, and extensible backend that can serve modern front‑ends while keeping external API usage efficient through local caching and a well‑structured service‑repository architecture.

## Executive Navigation Tree
- 📂 Alembic & Migrations
  - [Alembic Env Config](#alembic-env-config)
  - [Alembic Ini Constraints](#alembic-ini-constraints)
  - [Alembic Ini Data Contract](#alembic-ini-data-contract)
  - [Alembic Ini Interactions](#alembic-ini-interactions)
  - [Alembic Ini Purpose](#alembic-ini-purpose)
  - [Alembic Ini Usage Tips](#alembic-ini-usage-tips)
  - [Add Film Review Migration](#add-film-review-migration)
  - [Change Session Relations Migration](#change-session-relations-migration)
  - [Migration 3ba776aed6c5 Drop Legacy Tables](#migration-3ba776aed6c5-drop-legacy-tables)
  - [Migration 640dd27b82b8](#migration-640dd27b82b8)
  - [Migration 94dcbdb61b10](#migration-94dcbdb61b10)
  - [Migration Change Session Relations](#migration-change-session-relations)
  - [Migration Responsibility](#migration-responsibility)
  - [Films Session Drop Migration f63a5988397e](#films-session-drop-migration-f63a5988397e)
- ⚙️ Logic & Responsibility
  - [Downgrade Logic](#downgrade-logic)
  - [Upgrade Logic](#upgrade-logic)
  - [Component Responsibility](#component-responsibility)
- 📄 Data Contracts
  - [Data Contract](#data-contract)
  - [Data Contract 640dd27b82b8](#data-contract-640dd27b82b8)
- 🔄 Logic Flow
  - [Logic Flow 640dd27b82b8](#logic-flow-640dd27b82b8)
- 👁️ Visible Interactions
  - [Visible Interactions](#visible-interactions)
  - [Visible Interactions 640dd27b82b8](#visible-interactions-640dd27b82b8)
- 🌐 API Endpoints
  - [Auth Endpoints](#auth-endpoints)
  - [Film Endpoints](#film-endpoints)
  - [Add Review](#add-review)
  - [Delete Review](#delete-review)
  - [List My Reviews](#list-my-reviews)
  - [List Reviews](#list-reviews)
- 🗂️ Models
  - [Film Model](#film-model)
  - [FilmReview Model](#filmreview-model)
  - [User Model](#user-model)
- 🗄️ Repositories
  - [Base Repository](#base-repository)
  - [Concrete Repositories](#concrete-repositories)
  - [Wishlist Repository Update Element Films](#wishlist-repository-update-element-films)
  - [WishlistRepository Update Element Films](#wishlistrepository-update-element-films)
- 🔐 Security
  - [Password Hashing](#password-hashing)
  - [Random Hash Generation](#random-hash-generation)

 

<a name="alembic-env-config"></a>
## Alembic Environment Configuration  

**Component Responsibility**  
Initialises Alembic’s migration environment for **FilmList** by loading the ORM metadata (`Base.metadata`), injecting the runtime DB URL from `settings.DB_URL`, and wiring the appropriate migration runner (offline vs. online).

**Visible Interactions**  
- `from db.database import Base` → accesses **all** model tables.  
- `from core.config import settings` → fetches the **DB_URL** defined in the project config.  
- `alembic.context.config` → the Alembic configuration object, mutated to set `sqlalchemy.url`.  
- `engine_from_config` & `pool.NullPool` → creates a temporary engine for online migrations.  

**Technical Logic Flow**  
1. Load logging config (if present).  
2. Import `Base` → expose `target_metadata`.  
3. Print table keys (debug aid).  
4. Import `settings` → read `DB_URL`.  
5. Override Alembic config: `config.set_main_option("sqlalchemy.url", settings.DB_URL)`.  
6. Define `run_migrations_offline()` – configures context with URL only, enables literal binds.  
7. Define `run_migrations_online()` – builds engine from config, binds connection to context.  
8. Branch on `context.is_offline_mode()` to invoke the appropriate runner.  

**Data Contract**

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `config` | `alembic.context.Config` | Source of Alembic settings | Mutated to set `sqlalchemy.url`. |
| `settings.DB_URL` | `str` | Database connection string | Supplied by **FilmList** core config. |
| `Base.metadata` | `sqlalchemy.MetaData` | Table collection for autogeneration | Includes every model imported in `app.db.database`. |
| `engine_from_config` | Callable | Creates SQLAlchemy engine from `alembic.ini` values | Uses `pool.NullPool` to avoid connection pooling. |
| `connection` | DBAPI connection | Live DB link for migration scripts | Scoped within `with connectable.connect()`. |

> **Warning** – The `print(Base.metadata.tables.keys())` line writes table names to stdout during migration start‑up; remove in production to avoid noisy logs. 
<a name="alembic-ini-constraints"></a>
## Operational Constraints  

> **⚠️ Warning:** Execute migrations **only on a fresh database** or **after a verified backup**.  
> Dropping tables (`op.drop_table`) and indexes (`op.drop_index`) are irreversible without a restore point. 
<a name="alembic-ini-data-contract"></a>
## Data Contract (Excerpt)  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `revision` | `str` | Migration identifier | `'f63a5988397e'` |
| `down_revision` | `Union[str, Sequence[str], None]` | Parent migration | `'0a46a1d58dcf'` |
| `op.drop_index` | `Callable` | Removes deterministic index (via `op.f`) | Targets: `session`, `users` |
| `op.drop_table` | `Callable` | Deletes whole table, causing data loss | Tables: `session`, `films`, `users` |
| `op.create_table` | `Callable` | Re‑creates table schema (downgrade) | Columns defined with SQLAlchemy types |
| `op.create_index` | `Callable` | Re‑creates deterministic indexes | `unique=1` for `users.username` | 
<a name="alembic-ini-interactions"></a>
## Interaction Flow  

1. **CLI Invocation** – `alembic upgrade head` parses `alembic.ini`.  
2. **Env Script** – `env.py` calls `config.get_main_option("sqlalchemy.url")` → creates engine.  
3. **Migration Context** – `op.*` helpers (e.g., `op.drop_table`) use the engine to emit DDL.  
4. **Logging** – Settings under `[loggers]` control console output during migration execution. 
<a name="alembic-ini-purpose"></a>
## Alembic Configuration (`alembic.ini`) – Purpose & Scope  

The **`alembic.ini`** file supplies *static* settings for Alembic’s migration engine.  
It is **read only** by `alembic/env.py`, which injects the values into the migration context.  

| Setting | Type | Role | Notes |
|---------|------|------|-------|
| `script_location` | `str` | Base path for migration scripts | `%(here)s/alembic` |
| `prepend_sys_path` | `str` | Paths added to `sys.path` before import | `.` (project root) |
| `path_separator` | `str` | Delimiter for list‑type options | `os` (uses `os.pathsep`) |
| `sqlalchemy.url` | `str` | Database connection string for migration runs | `sqlite:///test.db` |
| `version_locations` (optional) | `str` | Alternate directories for version files | Not set – defaults to `script_location/versions` |
| `[loggers]` / `[handlers]` / `[formatters]` | *config* | Logging configuration for Alembic commands | Verbose INFO for Alembic, WARN for SQLAlchemy | 
<a name="alembic-ini-usage-tips"></a>
## Practical Tips  

- Keep `sqlalchemy.url` in sync with `app/core/config.py` → `Settings.database_url`.  
- When adding new migration directories, update `version_locations` and restart the Alembic CLI.  
- Use the `[post_write_hooks]` section to auto‑format generated scripts (e.g., Black, Ruff). 
<a name="add-film-review-migration"></a>
## Add Film Review Migration (`b8613fd000d0`)

**Functional role** – Executes a *destructive* schema change that removes the legacy **session**, **users**, and **films** tables together with their deterministic indexes. The migration does **not** recreate any of these objects; it merely drops them so that a subsequent migration can introduce the new `films_base` and `films_reviews` structures.

**Visible interactions** – Uses Alembic’s `op` helper (imported as `from alembic import op`) to issue DDL statements. No other project modules are referenced; the migration runs exclusively within Alembic’s command‑line context.

**Logic flow**  
1. `op.drop_index(op.f('ix_session_id'), table_name='session')` – removes the index that maps the session primary‑key column.  
2. `op.drop_table('session')` – deletes the entire `session` table.  
3. `op.drop_index(op.f('ix_users_id'), table_name='users')` and `op.drop_index(op.f('ix_users_username'), table_name='users')` – clear both user‑id and username indexes.  
4. `op.drop_table('users')` – removes the user table.  
5. `op.drop_index(op.f('ix_films_model_id'), table_name='films')` – discards the films index on `model_id`.  
6. `op.drop_table('films')` – drops the films table.  

The **downgrade** reverses these steps, recreating the three tables with their original column definitions and reinstating all indexes exactly as they existed before the upgrade.

> **Warning** – Running `upgrade()` **irreversibly deletes** all rows in `session`, `users`, and `films`. Apply only on a fresh development DB or after a verified backup.

--- 
<a name="change-session-relations-migration"></a>
## Change Session Relations Migration (`c6fa346e2960`)

**Functional role** – Refactors the `session` table’s foreign‑key column name from `user` to `user_id` and aligns the associated indexes with the new schema. Like the previous migration, it drops the old tables before they can be rebuilt with corrected relationships.

**Visible interactions** – Operates solely through Alembic’s `op` object.

**Logic flow**  
1. Remove `users` indexes (`ix_users_id`, `ix_users_username`) and drop the `users` table.  
2. Remove the `session` index (`ix_session_id`) and drop the `session` table.  

The **downgrade** recreates the `session` table with a column named `user` (FK → `users.id`) and restores both `session` and `users` indexes to their original definitions.

> **Warning** – The `upgrade()` step erases all persisted session and user data.

---

### Data contract  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `revision` | `str` | Migration identifier | `'b8613fd000d0'` / `'c6fa346e2960'` |
| `down_revision` | `str` | Parent migration | `'f63a5988397e'` / `'3253066141e8'` |
| `op.drop_index` | Callable | Removes deterministic index | Uses `op.f()` for naming |
| `op.drop_table` | Callable | Deletes whole table | Irreversible data loss |
| `op.create_table` | Callable | Re‑creates table schema (downgrade) | Columns defined with SQLAlchemy types |
| `op.create_index` | Callable | Re‑creates deterministic index | `unique=1` for `username` |

These tables precisely capture the inputs (DDL commands) and outputs (schema state) of each migration step without any external assumptions. 
<a name="migration-3ba776aed6c5-drop-legacy-tables"></a>
## Migration 3ba776aed6c5 – Drop Legacy Tables  

**Component Responsibility**  
Executes a destructive schema change that removes the historic `users`, `films_base`, `films`, `films_reviews`, and `session` tables along with their indexes. This is the final step of a migration chain that clears obsolete models before a new design is applied.

**Visible Interactions**  
- Calls the Alembic **operation proxy** `op` to issue DDL statements against the **SQLAlchemy‑engine** bound to the project's `SessionLocal`.  
- No Python‑level objects from the service layer are touched; the migration runs only during `alembic upgrade`.

**Technical Logic Flow**  
1. `op.drop_index(op.f('ix_users_id'), table_name='users')` – removes PK index.  
2. `op.drop_index(op.f('ix_users_username'), table_name='users')` – removes unique username index.  
3. `op.drop_table('users')` – deletes the `users` table.  
4. Repeats steps 1‑3 for `films_base`, `films`, `films_reviews`, and `session` tables, each preceded by its associated index removal.  
5. End of `upgrade`; `downgrade` recreates the dropped structures in reverse order using `op.create_table` and `op.create_index`.

**Data Contract**  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `revision` | `str` | Migration identifier | `'3ba776aed6c5'` |
| `down_revision` | `str` | Parent migration | `'640dd27b82b8'` |
| `op` | Alembic operation proxy | Issues DDL to DB | Methods: `drop_index`, `drop_table`, `create_table`, `create_index` |
| `sa` | SQLAlchemy | Column/type helpers for `create_table` | Used only in `downgrade` |

> **Warning** – This migration permanently deletes all data in the affected tables. Ensure a backup before applying to a production environment. 
<a name="migration-640dd27b82b8"></a>
## `640dd27b82b8_cahnge_film_review` – Schema Reset Migration  

**Component Responsibility**  
Replaces the legacy *films*, *films_base*, *films_reviews*, *session*, and *users* tables with a clean slate. The `upgrade()` path drops all indexes and tables; the `downgrade()` path rebuilds them exactly as they existed prior to this reset, preserving column definitions, primary‑key and foreign‑key constraints, and index names. 
<a name="migration-94dcbdb61b10"></a>
## Migration `94dcbdb61b10_change_db` – Full Schema Reset  

**Component responsibility** – Executes an irreversible drop‑and‑re‑create of all core tables (`users`, `session`, `films`, `films_base`, `films_reviews`). It is used by the **FilmList** Alembic migration chain to bring a fresh development database to the initial state expected by the layered FastAPI services.

### Visible interactions
- Calls **Alembic** operation helpers `op.drop_index`, `op.drop_table`, `op.create_table`, `op.create_index`.
- No direct runtime interaction with FastAPI endpoints; effects are observed when the DB is re‑initialised and the ORM models (`User`, `Session`, `Film`, `FilmReview`, `FilmBase`) are subsequently used by the repository layer.

### Technical logic flow
1. **Upgrade**  
   - Drop indexes (`ix_*`) for each table.  
   - Drop tables in dependency order (`films_base` → `films_reviews` → `films` → `session` → `users`).  
2. **Downgrade** (re‑create)  
   - Re‑create `users` table → add indexes (`ix_users_username` *unique*, `ix_users_id`).  
   - Re‑create `session` table with FK → index on `id`.  
   - Re‑create `films` with FK to `users` → index on `model_id`.  
   - Re‑create `films_reviews` with FKs to `films_base` and `users` → index on `review_id`.  
   - Re‑create `films_base` → index on `id`.

### Data contract  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `revision` | `str` | Migration identifier | `'94dcbdb61b10'` |
| `down_revision` | `str` | Parent migration | `'3ba776aed6c5'` |
| `op.drop_index` | Callable | Removes deterministic index | Uses `op.f` for naming |
| `op.drop_table` | Callable | Deletes whole table | Irreversible data loss |
| `op.create_table` | Callable | Re‑creates table schema | Columns defined with SQLAlchemy types |
| `op.create_index` | Callable | Re‑creates deterministic index | `unique=1` for username |

> **Warning** – Running `upgrade()` **irreversibly deletes** all rows in the affected tables. Apply only on a fresh development DB or after a verified backup. 
<a name="migration-change-session-relations"></a>
## Alembic Migration – Change Session Relations

**Component Responsibility**  
Executes a destructive schema revision (`0a46a1d58dcf`) that removes the legacy `users`, `session` and `films` tables together with their indexes. The downgrade path restores those tables with original column definitions, foreign‑key constraints and indexes.

**Visible Interactions**  
- Called by Alembic’s migration runner via `alembic upgrade head`.  
- Uses the global Alembic `op` object to emit DDL commands against the database engine configured in `alembic.ini`.  
- No direct imports from the FilmList application code; interaction is limited to the DB.

**Technical Logic Flow**  
1. **Upgrade**  
   - `op.drop_index` removes `ix_users_id` and `ix_users_username` from `users`.  
   - `op.drop_table('users')` deletes the `users` table.  
   - `op.drop_index` removes `ix_session_id` from `session`.  
   - `op.drop_table('session')` deletes the `session` table.  
   - `op.drop_table('films')` deletes the `films` table.  
2. **Downgrade**  
   - Re‑creates `films` with columns `id`, `user_id`, `title`, `img_path` and a foreign key to `users.id`.  
   - Re‑creates `session` (`id`, `user_id`) with a FK to `users.id` and adds index `ix_session_id`.  
   - Re‑creates `users` (`id`, `username`, `_password`) and restores indexes `ix_users_username` (unique) and `ix_users_id`.

**Data Contract**

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `revision` | `str` | Migration identifier | `'0a46a1d58dcf'` |
| `down_revision` | `str` | Parent migration | `'293791786db9'` |
| `op` | Alembic operation proxy | Issues DDL to DB | Methods: `drop_index`, `drop_table`, `create_table`, `create_index` |
| `sa` | SQLAlchemy | Column/type helpers | Used in `create_table` definitions |

> **Warning** – This migration permanently drops data; ensure backups before applying to production. 
<a name="migration-responsibility"></a>
## Migration Purpose – Table Reset  

The **`54c11c00dfc4_change_reiview_constaint.py`** migration is a *schema‑reset* operation for the legacy `users`, `films`, `films_reviews`, `wish_list*`, and `session` tables. During **upgrade** it permanently drops these tables and their indexes, effectively clearing all persisted data. The **downgrade** path restores the exact column definitions, primary‑key constraints, foreign‑key links, and index configurations that existed before the reset. 
<a name="films-session-drop-migration-f63a5988397e"></a>
## Films & Session Drop Migration (`f63a5988397e`)

**Component responsibility** – Executes an *upgrade* that removes the legacy `session`, `users`, and `films` tables and their related indexes, preparing the schema for the forthcoming `films_base` and `films_reviews` structures. The *downgrade* restores those tables and indexes exactly as they existed prior to the upgrade.

**Visible interactions** – Utilises only Alembic’s `op` helper (imported from `alembic`). No project modules, services, or runtime code are referenced; the migration runs inside Alembic’s CLI context.

### Logic flow
1. `op.drop_index(op.f('ix_session_id'), table_name='session')` – deletes the deterministic index on `session.id`.  
2. `op.drop_table('session')` – drops the entire `session` table (all rows lost).  
3. `op.drop_table('films')` – removes the `films` table (including its foreign‑key to `users`).  
4. `op.drop_index(op.f('ix_users_id'), table_name='users')` – clears the index on `users.id`.  
5. `op.drop_index(op.f('ix_users_username'), table_name='users')` – clears the unique index on `users.username`.  
6. `op.drop_table('users')` – deletes the `users` table.  

**Downgrade** reverses the above steps, recreating `users`, `films`, and `session` with their original column definitions and reinstating all indexes using `op.create_table` and `op.create_index`.

> **Warning** – `upgrade()` irreversibly deletes all data in `session`, `users`, and `films`. Apply only on a fresh DB or after a verified backup.

### Data contract

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `revision` | `str` | Migration identifier | `'f63a5988397e'` |
| `down_revision` | `Union[str, Sequence[str], None]` | Parent migration | `'0a46a1d58dcf'` |
| `op.drop_index` | `Callable` | Removes deterministic index (via `op.f`) | Target tables: `session`, `users` |
| `op.drop_table` | `Callable` | Deletes whole table, causing data loss | Tables: `session`, `films`, `users` |
| `op.create_table` | `Callable` | Re‑creates table schema (downgrade) | Columns defined with SQLAlchemy types |
| `op.create_index` | `Callable` | Re‑creates deterministic indexes | `unique=1` for `users.username` |

--- 
<a name="downgrade-logic"></a>
## Alembic Operations – Downgrade Path  

The downgrade recreates each structure in reverse order using `op.create_table` with explicit `sa.Column` definitions, primary‑key constraints, and foreign‑key links, followed by `op.create_index` calls that restore the original index names and uniqueness flags.

> **Warning** – This migration **irreversibly deletes** all rows in the affected tables. Apply only to a fresh development database or after a verified backup. 
<a name="upgrade-logic"></a>
## Alembic Operations – Upgrade Path  

1. `op.drop_index(op.f('ix_films_id'), table_name='films')` – removes the non‑unique PK surrogate index.  
2. `op.drop_table('films')` – deletes the `films` table.  
3. `op.drop_table('wish_list_films')` – removes the junction table linking wish‑lists to films.  
4. `op.drop_index(op.f('ix_users_id'), table_name='users')` and `op.drop_index(op.f('ix_users_username'), table_name='users')` – clear both PK‑related and unique‑username indexes.  
5. `op.drop_table('users')` – erases the user accounts table.  
6. `op.drop_index(op.f('ix_films_reviews_review_id'), table_name='films_reviews')` – drops the review‑id index.  
7. `op.drop_table('films_reviews')` – removes the review table.  
8. `op.drop_table('wish_list')` – deletes the wish‑list container.  
9. `op.drop_index(op.f('ix_session_id'), table_name='session')` – clears the session‑id index.  
10. `op.drop_table('session')` – eliminates the session tracking table. 
<a name="component-responsibility"></a>
## Component Responsibility  

- **Reset legacy schema** to a clean state, preparing the database for a fresh model migration or for complete data purge.  
- Guarantees that subsequent migrations start from a known baseline without residual constraints. 
<a name="data-contract"></a>
## Data Contract  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `revision` | `str` | Migration identifier | `'54c11c00dfc4'` |
| `down_revision` | `Union[str, Sequence[str], None]` | Parent migration | `'2256bb63d384'` |
| `op` | Alembic operation proxy | Executes DDL commands (`drop_index`, `drop_table`, `create_table`, `create_index`) | Scoped to the current migration script |
| `sa` | SQLAlchemy | Provides column/type helpers for `create_table` | Used only in `downgrade` |
| Index names (`ix_*`) | auto‑generated via `op.f` | Consistent naming across dialects | `unique=False` unless explicitly set (`unique=1` for username) | 
<a name="data-contract-640dd27b82b8"></a>
**Data Contract**  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `revision` | `str` | Migration identifier | `'640dd27b82b8'` |
| `down_revision` | `Union[str, Sequence[str], None]` | Parent migration | `'b8613fd000d0'` |
| `op` | Alembic operation proxy | Executes DDL (`drop_index`, `drop_table`, `create_table`, `create_index`) | Scoped to this script |
| `sa` | SQLAlchemy | Provides column/type constructors for `create_table` | Used only in `downgrade` |
| Index names (`ix_*`) | auto‑generated via `op.f` | Guarantees deterministic naming across dialects | `unique=False` unless explicitly set |

> **Warning** – Running `upgrade()` **irreversibly deletes** all rows in the affected tables. Apply only on a fresh development DB or after a verified backup. 
<a name="logic-flow-640dd27b82b8"></a>
**Technical Logic Flow**  

| Step | Operation | Target |
|------|-----------|--------|
| 1 | `op.drop_index(..., 'films')` | removes `ix_films_model_id` |
| 2 | `op.drop_table('films')` | deletes *films* table |
| 3 | `op.drop_index(..., 'films_base')` | removes `ix_films_base_id` |
| 4 | `op.drop_table('films_base')` | deletes *films_base* |
| 5 | `op.drop_index(..., 'films_reviews')` | removes `ix_films_reviews_review_id` |
| 6 | `op.drop_table('films_reviews')` | deletes *films_reviews* |
| 7 | `op.drop_index(..., 'session')` | removes `ix_session_id` |
| 8 | `op.drop_table('session')` | deletes *session* |
| 9 | `op.drop_index(..., 'users')` (twice) | removes `ix_users_id` & `ix_users_username` |
|10 | `op.drop_table('users')` | deletes *users* |

The `downgrade()` mirrors this list in reverse, invoking `op.create_table` with explicit `sa.Column` specifications, then `op.create_index` to restore each index (e.g., `unique=1` for `ix_users_username`). 
<a name="visible-interactions"></a>
## Visible Interactions  

- The script interacts **solely** with Alembic’s `op` object; no imports from the application layer (`app.*`) are referenced.  
- No runtime data is read or written; the migration issues **DDL** statements to the target database engine configured in the Alembic environment. 
<a name="visible-interactions-640dd27b82b8"></a>
**Visible Interactions**  
- Interacts **only** with Alembic’s `op` proxy and SQLAlchemy’s `sa` helpers.  
- No imports from the application layer (`app.*`).  
- Executes DDL statements against the database engine configured in the Alembic environment; no runtime data is read or written. 
<a name="auth-endpoints"></a>
## Auth Endpoints (`app/api/v1/endpoints/auth.py`)

**Responsibility** – Expose registration, login, session‑check and logout routes; delegate all business logic to `AuthService` and use `UserRepository(SessionLocal)` for persistence.

**Visible Interactions**  
- `verify_user` (dependency) validates the session cookie and returns a dict `{status, message, user_id?, session_id?}`.  
- `AuthService` methods (`regist`, `login`, `logout`) receive plain Pydantic models (`UserInfo`, `SessionSearchingParams`).  
- `UserRepository` is instantiated with the global `SessionLocal` factory; no explicit DB session is passed.

**Logic Flow**  
1. **POST /auth/regist** – Build `AuthService`; call `regist(user_info)`.  
2. If `True` → JSON `{"status":"success","message":created_object}` else error message.  
3. **POST /auth/login** – Call `login(user_params)`. On success set cookie `custom_session_id` with returned session token.  
4. **GET /auth/check_auth** – Return success if `verify_user` reports `status=True`.  
5. **POST /auth/logout** – After successful verification, invoke `logout(SessionSearchingParams(id=session_id))`; success yields JSON success, otherwise error.

**Data Contract**

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `user_info` / `user_params` | `UserInfo` (Pydantic) | Input | Contains `username`, `password`. |
| `verify_data` | `dict` | Dependency output | Keys: `status` (bool), `message` (str), optional `user_id`, `session_id`. |
| `detail` (login) | `str` | Session token | Placed in response cookie. |
| Returned JSON | `dict` | Output | Keys `status` (`"success"`/`"error"`), `message` or `result`. |

> **Warning** – The endpoints instantiate a new `UserRepository(SessionLocal)` per request; this bypasses FastAPI’s `Depends(get_db)` pattern and may lead to multiple engine connections if not managed elsewhere. 
<a name="film-endpoints"></a>
## Film & Wish‑List Endpoints (`app/api/v1/endpoints/film.py`)

**Responsibility** – Provide film search, detail retrieval, and wish‑list manipulation for authenticated users; rely on `FilmService` and `WishListService`.

**Visible Interactions**  
- `verify_user` guards every route.  
- `FilmService(FilmRepository(SessionLocal))` handles external TMDB queries and auto‑creation of missing `Film` rows.  
- `WishListService(WishListRepository(SessionLocal))` manages user‑specific wish‑list records.  

**Logic Flow**  
1. **GET /film/search_film** – On auth success, call `find_film_by_name(q=query)`; return list under `result`.  
2. **GET /film/{film_id}** – Call `get_info_about_film(FilmSerchingParams(id=film_id))`; forward film object on success.  
3. **POST /film/wish_list/{film_id}** – Build `AddToWishList(user_id, film_id)`; invoke `add_film_to_wish_list`; return updated wish‑list.  
4. **DELETE /film/wish_list/{film_id}** – Same DTO, call `remove_film_from_wish_list`; success yields simple success JSON.  
5. **GET /film/wish_list** – Call `get_wish_list(WishListCreator(user_id))`; reverse list before returning.

**Data Contract**

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `query` | `str` | Input (search) | Required query term. |
| `film_id` | `int` | Path param | Target film identifier. |
| `AddToWishList` | Pydantic | Input (wish‑list ops) | Fields `user_id`, `film_id`. |
| `WishListCreator` | Pydantic | Input (list retrieval) | Field `user_id`. |
| Service return | `(bool, object)` | Output | `bool` indicates success; `object` is either film data, wish‑list, or error placeholder. |
| Returned JSON | `dict` | Output | Same shape as auth endpoints (`status`, optional `result`, `message`). |

> **Critical** – All endpoints depend on `verify_user`; if it returns `status=False`, the route aborts early with the provided `message`. No additional validation is performed inside these functions. 
<a name="add-review"></a>
## Review Endpoint – Add Review (`POST /review/{film_id}`)

**Responsibility** – Accept a `ReviewForAdd` payload, validate the caller via `verify_user`, and delegate creation to `ReviewService`. Returns the persisted **Review** model on success.

**Visible Interactions**  
- `verify_user` (from `app.core.dependencies`) supplies `status`, `user_id`, and a default *unauthorized* message.  
- `ReviewService` is instantiated with `FilmReviewRepository(SessionLocal)`.  
- `ReviewService.add_review` receives a fully‑populated `Review` ORM instance and returns `(bool, Review|None)`.

**Logic Flow**  
1. FastAPI injects `verify_data` from `Depends(verify_user)`.  
2. If `verify_data["status"]` is **True**, build `Review` (`film_id`, `user_id` from `verify_data`, `content`, `rate`).  
3. Call `review_service_object.add_review(review)`.  
4. On `status=True` → respond `{"status":"success","result":review_object}`; otherwise → `{"status":"error","message":message}`.  

**Data Contract**

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `review_info` | `ReviewForAdd` (Pydantic) | Input body | Contains `film_id`, `content`, `rate`. |
| `verify_data` | `dict` | Dependency output | Keys: `status` (bool), `user_id` (int), `message` (str). |
| `review_object` | `Review` (ORM) | Service output | Persisted review instance returned on success. |
| Returned JSON | `dict` | Output | `status` (`"success"`/`"error"`), `result` (review) or `message`. |

> **Warning** – Each request creates a new `FilmReviewRepository(SessionLocal)` bypassing FastAPI’s `Depends(get_db)`. This can spawn multiple DB connections if the session lifecycle isn’t otherwise controlled. 
<a name="delete-review"></a>
## Review Endpoint – Delete Review (`DELETE /review/{review_id}`)

*After authorization, calls `ReviewService.delete_review` with `ReviewSearchingParams(review_id, user_id)`. Success yields `{"status":"success"}`; failure falls back to the dependency’s error message.* 
<a name="list-my-reviews"></a>
## Review Endpoint – List My Reviews (`GET /review/my`)

*Uses `verify_user` to inject `user_id`, builds `ReviewSearchingParams(user_id=…)`, and returns the user’s reviews.* 
<a name="list-reviews"></a>
## Review Endpoint – List All (`GET /review/`)

*Validates user, forwards `ReviewSearchingParams` (auto‑populated from query) to `ReviewService.get_reviews`, returns list under `result`.* 
<a name="film-model"></a>
## Film Model & Wish‑List Association  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| **Film** | SQLAlchemy model | Stores basic film data (`id`, `title`, `image`) | Primary key `id` indexed |
| **wish_list_films** | Association table | Many‑to‑many link between `WishList` and `Film` | Columns `wish_list_id` → `wish_list.user_id`, `film_id` → `films.id` |
| **WishList** | SQLAlchemy model | Holds a user’s selected films | `user_id` PK, `films` relationship via `wish_list_films`; `get_films()` returns list of film IDs |

> **Logic:** When a `WishList` instance is loaded, SQLAlchemy populates `films` through the secondary table; calling `get_films()` provides a plain list of IDs for API responses. 
<a name="filmreview-model"></a>
## FilmReview Model – Uniqueness Guard  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| **FilmReview** | SQLAlchemy model | Represents a user’s rating/comment on a film | Unique constraint `uq_user_film_review` prevents duplicate reviews per `(user_id, film_id)` | 
<a name="user-model"></a>
## User Model – Password Management  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| **User** | SQLAlchemy model | Authentication principal | `username` unique; `_password` stores hashed value |
| **password (property)** | Python property | Setter hashes via `hash_password`; getter returns raw stored hash | `check_password()` verifies with `verify_password` |
| **Session** | SQLAlchemy model | Tracks active login sessions | PK `id` generated by `get_rand_hash`; links to `User` | 
<a name="base-repository"></a>
## BaseRepository – CRUD Core  

| Method | Input | Output / Side‑Effect | Notes |
|--------|-------|----------------------|-------|
| `read_by_options(schema, eager=False)` | Pydantic `BaseModel` with optional filters | `{"all": [objects], "query": Query}` | Builds filter list from non‑null fields |
| `create(schema)` | Pydantic model | `(bool success, ORM instance or None)` | Commits or rolls back on exception |
| `read_by_id(schema, eager=False)` | Pydantic model with primary key | ORM instance or `None` | Delegates to `read_by_options` |
| `update_element_by_id(id_schema, change_schema)` | PK schema, change schema | Updated ORM instance or `None` | Sets attributes then commits |
| `delete_object(schema)` | PK schema | `True` if deleted, `False` otherwise | Performs `session.delete` + commit |

> **Assumption:** All repository instances receive a `session_factory` (usually `SessionLocal`) from FastAPI dependencies; the session is created lazily and closed in `__del__`. 
<a name="concrete-repositories"></a>
## Concrete Repository Instantiations  

| Repository | Base Model | Purpose |
|------------|------------|---------|
| `FilmRepository` | `Film` | Exposes `BaseRepository` CRUD for film records |
| `FilmReviewRepository` | `FilmReview` | Manages review persistence and uniqueness |
| `UserRepository` | `User` | Handles user lookup/creation |
| `SessionRepository` | `Session` | Validates and revokes login sessions |

*All concrete classes simply call `super().__init__(session_factory, Model)`; no additional logic is present in the supplied fragment.* 
<a name="wishlist-repository-update-element-films"></a>
## WishListRepository · `update_element_films` – Persist Film‑ID Collection

**Component responsibility**  
Updates the `films` attribute of an existing `WishList` ORM instance and guarantees the change is flushed to the database.

**Visible interactions**  
1. Receives a *primary‑key holder* (`schema_id`) and an `UpdateWishList` payload.  
2. Calls `self.read_by_id(schema_id)` to obtain `curr_object` (`WishList`).  
3. Mutates `curr_object.films` in‑place, then uses the repository‑owned SQLAlchemy `session` for persistence.

### Technical logic flow
1. `curr_object = self.read_by_id(schema_id)` – fetches the target row.  
2. `setattr(curr_object, "films", update_schema.films)` – assigns the new list of film IDs (already converted to `list[Film]` upstream).  
3. `session = self.get_session()` – obtains the transaction context.  
4. **Commit attempt**  
   ```python
   try:
       session.commit()
       session.refresh(curr_object)
   except Exception:
       session.rollback()
       return False, None
   ```  
5. On success, returns `True, curr_object`.

> **Warning**: The method assumes every key in `update_schema` matches a column on `WishList`. Unexpected fields are set without validation.

### Data contract

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `schema_id` | `BaseModel` (e.g., `WishListCreator`) | Holds the primary key of the wish‑list to update | Passed to `read_by_id` |
| `update_schema` | `BaseModel` (`UpdateWishList`) | Payload with mutable fields; `films` = `list[int]` | Converted to `list[Film]` before this method |
| `session` | `Session` (SQLAlchemy) | Transaction context | Obtained via `BaseRepository.get_session()` |
| `curr_object` | `WishList` ORM instance | The row being mutated | Updated in‑place |
| Return value | `tuple[bool, WishList|None]` | `(success, updated_object)` | `None` also returned when target not found or on error | 
<a name="wishlistrepository-update-element-films"></a>
## WishListRepository.update_element_films

**Responsibility**  
Updates a `WishList` ORM instance’s mutable fields, converting a list of film IDs into `Film` objects for the `films` relationship.

**Visible Interactions**  
- Calls `self.get_session()` from `BaseRepository` → obtains a SQLAlchemy `Session`.  
- Reads the target wish‑list via `self.read_by_id(schema_id)`.  
- Queries `Film` model (`session.query(Film).filter(Film.id.in_(value)).all()`).  
- Commits the session; on failure rolls back and returns `False, None`.

**Logic Flow**  
1. Acquire `session`.  
2. Retrieve current wish‑list (`curr_object`). If missing → `return None`.  
3. Serialize `update_schema` (`model_dump()`).  
4. Iterate over each field:  
   - If key is `"films"` convert supplied ID list to ORM `Film` objects.  
   - Assign the processed value to the attribute on `curr_object`.  
5. Attempt `session.commit()` and `session.refresh(curr_object)`.  
6. On exception: `session.rollback()` → `return False, None`.  
7. Success → `return True, curr_object`.

**Data Contract**

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `schema_id` | `BaseModel` (e.g., `WishListCreator`) | Primary‑key holder for the wish‑list to update | Passed to `read_by_id` |
| `update_schema` | `BaseModel` (`UpdateWishList`) | Payload with fields to modify; `films` = `list[int]` | Converted to `list[Film]` inside method |
| `session` | `Session` (SQLAlchemy) | Transaction context | Obtained via `BaseRepository.get_session()` |
| `curr_object` | `WishList` ORM instance | Target row being mutated | Updated in‑place |
| Return value | `tuple` | `(bool success, WishList|None)` | `None` also returned when target not found |

> **Warning**: The method assumes `update_schema` contains only fields present on the `WishList` model; unexpected keys will be set as attributes without validation. 
<a name="password-hashing"></a>
## Password Hashing Utilities (`hash_password` & `verify_password`)

**Responsibility** – Encode a clear‑text password into a bcrypt hash and later verify a candidate password against that hash.

**Visible Interactions** – Uses the third‑party `bcrypt` library; no other project components are touched.

**Logic Flow – `hash_password`**
1. Generate a salt with `bcrypt.gensalt()`.  
2. Encode the plain password to UTF‑8 bytes.  
3. Compute `bcrypt.hashpw(password_bytes, salt)` → hashed bytes.  
4. Decode hashed bytes to UTF‑8 string and return.

**Logic Flow – `verify_password`**
1. Encode both `plain_password` and stored `hashed_password` to UTF‑8 bytes.  
2. Call `bcrypt.checkpw(plain_bytes, hashed_bytes)`.  
3. Return the Boolean result.

**Data Contract**

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `password` / `plain_password` | `str` | User‑supplied clear text | Must be UTF‑8 encodable |
| `hashed_password` | `str` | Stored bcrypt hash | Produced by `hash_password` |
| Return (`hash_password`) | `str` | bcrypt hash string (includes salt & cost) | Ready for DB storage |
| Return (`verify_password`) | `bool` | Verification outcome | `True` if match, else `False` |

> **Critical** – The functions **do not** perform any additional validation (e.g., password strength) and assume the inputs are well‑formed strings. 
<a name="random-hash-generation"></a>
## Random Hash Generation (`get_rand_hash`)

**Responsibility** – Produces a deterministic‑length pseudo‑random hexadecimal string using `uuid.uuid4()`.

**Visible Interactions** – Relies solely on Python’s standard `uuid` module; no external services or project‑level dependencies.

**Logic Flow**
1. Call `uuid.uuid4()` → generates a random UUID (128‑bit).  
2. Access `.hex` → 32‑character hex representation.  
3. Slice `[:length]` where `length` defaults to `32`.  
4. Return the sliced string.

**Data Contract**

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `length` | `int` (default = 32) | Desired length of the output hash | Must be ≤ 32; longer values are silently truncated |
| Return | `str` | Hex‑encoded random hash | Characters: `0‑9a‑f` |

> **Warning** – The function does **not** guarantee cryptographic security; it is suitable for identifiers, not for password hashing. 
