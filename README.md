**Project Title**  
**FilmList – Thin FastAPI Backend for Film Discovery & Personal Collections**

---

### Project Goal
FilmList provides a lightweight, high‑performance backend that lets users:

1. **Authenticate securely** using cookie‑based sessions.  
2. **Search for movies** through The Movie Database (TMDB) API, presenting curated information without exposing TMDB credentials.  
3. **Maintain a personal wish‑list** and **write film reviews** that are stored locally in a relational database.  

The system solves the common problem of building a full‑stack film‑tracking application by handling all authentication, external‑API integration, and persistence concerns in a single, well‑structured FastAPI service, leaving the front‑end completely free to focus on UI/UX.

---

### Core Logic & Principles  

| Layer | Responsibility | Key Concepts |
|-------|----------------|--------------|
| **API (Router)** | Exposes HTTP endpoints (`/auth/*`, `/film/*`, `/review/*`, etc.). | FastAPI routers, dependency injection, `Response.set_cookie` for session tokens. |
| **Service** | Orchestrates business rules. Calls repositories for data access and the side‑API for TMDB interactions. | Stateless classes (`AuthService`, `FilmService`, `WishListService`, `ReviewService`). |
| **Repository** | Performs CRUD operations against the SQLAlchemy ORM models. | Generic `BaseRepository` + concrete repos (`UserRepository`, `FilmRepository`, …). Each repository receives a single `Session` instance for the whole request. |
| **Database** | Provides a fresh SQLAlchemy session per request (`SessionLocal`) and creates DB metadata on startup. | SQLite/PostgreSQL (configurable), Alembic migrations. |
| **Side‑API (TMDB client)** | Wraps all external calls to TMDB, injecting the API key from environment variables. | `TMDBClient.search_film()`, `TMDBClient.get_details()`. Returns raw JSON, which is then parsed into Pydantic schemas. |
| **Core Utilities** | Password hashing, cookie verification, shared constants. | `hash_password`, `verify_password`, `verify_user` dependency that reads the `custom_session_id` cookie and resolves the current `User`. |
| **Schemas** | Define the contract between request/response bodies and internal models. | Pydantic models for `UserCreate`, `FilmSearchResult`, `WishListItem`, `ReviewCreate`, etc. |

**Data Flow (Typical Request)**  

1. **Entry Point** – A FastAPI router receives an HTTP request (e.g., `POST /auth/login`).  
2. **Dependency Resolution** – If the endpoint requires authentication, `Depends(verify_user)` reads the session cookie, retrieves the `User` via `UserRepository`, and injects it into the path operation.  
3. **Service Invocation** – The router calls the appropriate Service method, passing validated Pydantic data.  
4. **Repository Interaction** – The Service delegates persistence work to a Repository, which uses the request‑scoped `Session` to query/commit data.  
5. **External API (if needed)** – For film searches, `FilmService` calls `TMDBClient`, receives raw JSON, maps it to Pydantic response models, and returns them.  
6. **Terminal Points** –  
   * `Response.set_cookie` writes the session token back to the client (login).  
   * `session.commit()` finalizes any DB changes.  
   * The router returns a JSON response, completing the HTTP cycle.

**Architectural Principles**

* **Layered Separation** – Each concern (routing, business logic, data access, external integration) lives in its own package, making the codebase easy to extend and test.  
* **Dependency Injection** – FastAPI’s `Depends` system provides request‑scoped resources (DB session, authenticated user) without coupling code to global state.  
* **Contract‑First Design** – Pydantic schemas are the single source of truth for data exchanged between layers, ensuring validation and type safety.  
* **Replaceability** – Swapping the TMDB provider or changing the persistence engine only requires modifications in the side‑API or repository modules; services remain untouched.  
* **CI‑Driven Documentation** – GitHub Actions (`autodoc.yml`) automatically generate API docs, keeping documentation in sync with code.

---

### Key Features
- **Secure Cookie‑Based Authentication** – login, logout, and session verification using hashed passwords.  
- **TMDB‑Powered Film Search** – fuzzy title search, detailed movie lookup, and result pagination.  
- **Personal Wish‑List Management** – add, list, and remove movies from a user‑specific collection.  
- **Film Review System** – create, edit, and delete textual reviews linked to a film and a user.  
- **Layered Service‑Repository Architecture** – clean separation of concerns, facilitating unit testing and future extensions.  
- **Database Migrations with Alembic** – versioned schema evolution.  
- **Automated API Documentation** – OpenAPI/Swagger UI generated from FastAPI routes and Pydantic models.  
- **CI Workflow for Documentation** – GitHub Actions automatically rebuilds docs on each push.

---

### Dependencies
| Category | Packages / Tools | Purpose |
|----------|------------------|---------|
| **Web Framework** | `fastapi>=0.95`, `uvicorn[standard]` | HTTP server and routing. |
| **ORM & DB** | `SQLAlchemy>=2.0`, `alembic` | Object‑relational mapping and migrations. |
| **Data Validation** | `pydantic>=2.0` | Request/response schemas. |
| **Authentication** | `passlib[bcrypt]` | Password hashing utilities. |
| **External API** | `httpx` | Asynchronous HTTP client for TMDB calls. |
| **Environment Management** | `python-dotenv` | Load `TMDB_API_KEY` and other env variables. |
| **Testing** *(not listed but typical)* | `pytest`, `pytest-asyncio`, `httpx[http2]` | Unit & integration testing. |
| **CI / Docs** | GitHub Actions (`autodoc.yml`), `mkdocs` (optional) | Automated documentation generation. |
| **CORS** | `fastapi[all]` (includes `starlette`) | Cross‑origin resource sharing configuration. |

*All versions are indicative; exact pinned versions are defined in `requirements.txt` / `pyproject.toml` of the repository.*

## Executive Navigation Tree
- 📂 Documentation
  - [AutoDoc Workflow](#autodoc-workflow)
- 📂 Identity & Access
  - [Auth Endpoints](#auth-endpoints)
  - [Auth Service](#auth-service)
- 📂 Utilities
  - [Password Hashing Utility](#password-hashing-utility)
  - [Password Verification Utility](#password-verification-utility)
  - [Random Hash Generator](#random-hash-generator)
- 📂 Film Management
  - [Film Endpoints](#film-endpoints)
  - [Film ORM Models](#film-orm-models)
  - [Film Service](#film-service)
- 📂 Review System
  - [Review Endpoints](#review-endpoints)
- 📂 Session Management
  - [User Session ORM Models](#user-session-orm-models)
- 📂 Data Access Layer
  - [Base Repository](#base-repository)
  - [Concrete Repositories](#concrete-repositories)
  - [Wish List Repository Update](#wish-list-repository-update)

 

<a name="autodoc-workflow"></a>
## AutoDoc GitHub Actions Workflow

**Component Role** – Automates documentation generation for the *FilmList* codebase by invoking the reusable *ADG* workflow. It is triggered manually (or via `workflow_dispatch`) and requires write permission on the repository to commit generated docs.

**Visible Interactions**  
- **Input:** Workflow dispatch event from GitHub UI/API.  
- **Outputs:** Commits (or updates) documentation files back to the repository.  
- **External Dependency:** Reuses the remote workflow `Drag-GameStudio/ADG/.github/workflows/reuseble_agd.yml@main`.  
- **Secrets:** Consumes `GROCK_API_KEY` secret, passed to the reused workflow.

**Logic Flow**  

1. **Event Listener** – `on: [workflow_dispatch]` registers a manual trigger.  
2. **Job Definition** – Single job `run` executes with `permissions: contents: write` to allow pushing changes.  
3. **Reusable Workflow Call** – `uses:` loads the external ADG workflow, pinning it to the `main` branch.  
4. **Secret Propagation** – Under `secrets:` the `GROCK_API_KEY` from the current repo is forwarded unchanged.  
5. **Execution** – The imported workflow runs its own steps (e.g., code analysis, doc generation, git commit) using the supplied API key.

**Data Contract**

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `workflow_dispatch` event | Trigger | Starts the AutoDoc pipeline | Manual only; no payload defined |
| `GROCK_API_KEY` | Secret string | Auth token for the documentation generator | Must exist in repository secrets |
| `contents` permission | Permission scope | Allows the workflow to push commits | Set to `write` |
| Reused workflow `reuseble_agd.yml` | Remote workflow reference | Encapsulates actual doc generation logic | Version‑pinned to `@main` |

> **Warning:** If `GROCK_API_KEY` is missing or lacks required scopes, the workflow will fail before any documentation is produced. 
<a name="auth-endpoints"></a>  
## Auth Endpoints – Registration, Login, Session Checks  

**Component Role**  
Implements the public authentication surface. It instantiates `AuthService` with a fresh `UserRepository(SessionLocal)` for each request and delegates user‑creation, credential verification, and session termination.

**Visible Interactions**  
- Calls `UserRepository` (CRUD on `User` & `Session` tables).  
- Returns HTTP JSON; on successful login writes cookie `custom_session_id`.  
- Relies on `verify_user` dependency for protected routes (`check_auth`, `logout`).

**Logic Flow**  
1. **/regist** – receives `UserInfo`; creates `AuthService`; `regist()` returns `(bool, obj)`.  
2. **/login** – receives `UserInfo`; `login()` returns `(bool, token)`. On success `Response.set_cookie`.  
3. **/check_auth** – `verify_user` supplies `{status, message}`; forwards status.  
4. **/logout** – `verify_user` yields `session_id`; `logout()` called; success → JSON.

**Data Contract**

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `UserInfo` | Pydantic model | Input for `/regist` & `/login` | Username, password fields |
| `SessionSearchingParams` | Pydantic model | Input for `/logout` | Holds `id` of session |
| `custom_session_id` | Cookie (string) | Auth token set on login | `httponly=False`, 30‑day TTL |
| JSON response | `{"status": "...", "message": "...", "result": ...}` | Output | `status` = `"success"` or `"error"` |

> **Warning:** Missing or malformed `UserInfo` leads to a validation error before entering service logic.

--- 
<a name="auth-service"></a>
## AuthService Core Methods  

| Method | Input | Output | Side Effects |
|--------|-------|--------|--------------|
| `regist(user: UserInfo)` | `UserInfo(username, password)` | `(bool, Model|None)` | Calls `UserRepository.create`. |
| `login(user: UserInfo)` | `UserInfo` | `(bool, str|None)` | Reads user, checks password, creates `Session` via `SessionRepository.create`, returns session ID. |
| `logout(session_schema: SessionSearchingParams)` | `SessionSearchingParams(id?, user?)` | `bool` | Deletes matching `Session`. |
| `check_auth(session_schema)` | `SessionSearchingParams` | `(bool, int|None)` | Reads `Session`; returns associated `user.id`. |

**Interaction Path** – AuthService composes a `UserRepository` and a `SessionRepository` (the latter receives the same `session_factory`). All DB work is delegated to these repositories; password hashing/verification is encapsulated in the `User` model (outside this fragment). 
<a name="password-hashing-utility"></a>
## Password Hashing Utility  

**Responsibility** – Convert a plain‑text password into a bcrypt hash suitable for storage.  

**Visible Interactions** – Relies on the external **`bcrypt`** library; otherwise stateless.  

**Logic Flow**  
1. `bcrypt.gensalt()` creates a unique salt.  
2. `bcrypt.hashpw()` hashes the UTF‑8 encoded password with that salt.  
3. Decode the resulting bytes to a UTF‑8 string and return.  

**Data Contract**  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `password` | `str` | User‑provided plain password | Must be UTF‑8 encodable |
| Return | `str` | Bcrypt hash string | Format: `$2b$<cost>$<salt+hash>` |

--- 
<a name="password-verification-utility"></a>
## Password Verification Utility  

**Responsibility** – Validate a plain password against a stored bcrypt hash.  

**Visible Interactions** – Uses `bcrypt.checkpw`.  

**Logic Flow**  
1. Encode both the plain password and stored hash as UTF‑8 bytes.  
2. Call `bcrypt.checkpw()`; it returns `True` if they match.  

**Data Contract**  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `plain_password` | `str` | Input to verify | UTF‑8 encodable |
| `hashed_password` | `str` | Stored bcrypt hash | Must be a valid bcrypt string |
| Return | `bool` | Verification result | `True` = match, `False` = mismatch |

> **Warning** – No rate‑limiting or timing‑attack mitigation is performed here; callers should enforce such controls. 
<a name="random-hash-generator"></a>
## Random Hash Generator  

**Responsibility** – Produce a short, pseudo‑random hexadecimal string for use as identifiers or tokens.  

**Visible Interactions** – Pure utility; no external calls or state.  

**Logic Flow**  
1. Call `uuid.uuid4()` to create a UUID object.  
2. Access its `hex` representation (32 hex chars).  
3. Slice to the requested `length` (default 32).  
4. Return the sliced string.  

**Data Contract**  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `length` | `int` | Desired output length | Must be ≤ 32; not validated in code |
| Return | `str` | Random hash | Deterministic only by UUID randomness |

--- 
<a name="film-endpoints"></a>  
## Film Endpoints – Search & Wish‑List Operations  

**Component Role**  
Provides authenticated film lookup via TMDB (via `FilmService`) and personal wish‑list manipulation through `WishListService`.

**Visible Interactions**  
- `verify_user` supplies user context.  
- `FilmRepository` accessed for external TMDB look‑ups.  
- `WishListRepository` persists wish‑list entries.  

**Logic Flow**  
1. **/search_film** – validates auth, creates `FilmService`, calls `find_film_by_name(q)`, returns list.  
2. **/wish_list/{film_id} (POST)** – builds `AddToWishList(user_id, film_id)`, invokes `add_film_to_wish_list`; on success returns created list entry.  
3. **/wish_list/{film_id} (DELETE)** – similar payload, calls `remove_film_from_wish_list`.  
4. **/wish_list (GET)** – creates `WishListCreator(user_id)`, fetches list, reverses order before response.  
5. **/{film_id} (GET)** – queries `FilmService.get_info_about_film` with `FilmSerchingParams(id)`.

**Data Contract**

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `query` | `str` (query param) | Search term for `/search_film` | Required |
| `film_id` | `int` (path) | Identifier for wish‑list ops & detail fetch | Required |
| `AddToWishList` | Pydantic model | Input for add/remove wish‑list | Contains `user_id`, `film_id` |
| `WishListCreator` | Pydantic model | Input for retrieving list | Contains `user_id` |
| `FilmSerchingParams` | Pydantic model | Input for film detail endpoint | Contains `id` |
| JSON response | `{"status": "...", "result": ..., "message": "..."}` | Output across endpoints | `result` varies (list, object, or omitted) |

> **Warning:** All endpoints abort with `"error"` if `verify_user` reports `status=False`; ensure the `custom_session_id` cookie is present and valid. 
<a name="film-orm-models"></a>
## Film & WishList ORM Models  

The **Film** model stores minimal metadata (`id`, `title`, `image`).  
`WishList` links a single **User** (`user_id`) to many **Film** rows via the association table **wish_list_films**.  
`WishList.get_films()` returns a list of film IDs currently in the list.

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `Film` | SQLAlchemy model | Persisted film catalog entry | Primary key `id`; no constraints beyond `index=True`. |
| `wish_list_films` | Association Table | Many‑to‑many bridge between `WishList` and `Film` | Composite PK (`wish_list_id`, `film_id`). |
| `WishList` | SQLAlchemy model | User‑specific collection of favourite films | One‑to‑one `user`; `films` uses `secondary=wish_list_films`. | 
<a name="film-service"></a>
## FilmService Key Operations  

| Method | Input | Output | Side Effects |
|--------|-------|--------|--------------|
| `find_film_by_name(q: str)` | Search query | `list[FilmInfo]` (max 10) | Calls `TMDB.find_the_films`. |
| `auto_create_film(film_info: FilmSerchingParams)` | Film identifiers | `(bool, Film|None)` | Attempts `get_film`; if missing, calls `create_film`. |
| `get_info_about_film(film_info)` | Same as above | `(bool, Film|None)` | Wrapper around `auto_create_film`. |
| `get_film(film_info)` | `FilmSerchingParams` | `(bool, Film|None)` | Delegates to `FilmRepository.read_by_id`. |
| `create_film(film_creator: FilmCreator)` | `FilmCreator(id)` | `(bool, Film|None)` | Retrieves TMDB data via `TMDB.find_film_by_id`; persists via `FilmRepository.create`. |

**Visible Inter‑layer Calls** – `FilmService` uses `FilmRepository` for persistence and the side‑API wrapper `TMDB` for external look‑ups. No cookies or auth dependencies are involved here.  

---  

These sections capture the exact responsibilities, intra‑project interactions, and data contracts of the supplied code without extrapolating beyond what is present. 
<a name="review-endpoints"></a>  
## Review Endpoints – Add / List / Own / Delete  

**Component Role**  
Handles CRUD operations for film reviews. Each route validates the caller via `verify_user`, builds a `ReviewService` backed by a `FilmReviewRepository(SessionLocal)`, and returns a uniform JSON payload.

**Visible Interactions**  

| Entity | Origin | Interaction |
|--------|--------|-------------|
| `verify_user` (core.dependencies) | Cookie‑based auth | Supplies `status`, `user_id`, `message` |
| `ReviewService` (app.services.review_service) | Business‑logic layer | Exposes `add_review`, `get_reviews`, `delete_review` |
| `FilmReviewRepository` | Repository layer | Receives the `SessionLocal` factory for DB sessions |
| `SessionLocal` | app.db.database | Provides a fresh SQLAlchemy `Session` per request |
| Pydantic schemas (`Review`, `ReviewForAdd`, `ReviewSearchingParams`) | app.schema.film_review | Validate request bodies / query parameters |

**Technical Logic Flow**  

1. **POST `/review/{film_id}`** – `add_review` receives a `ReviewForAdd` body.  
   - `verify_user` runs; on `status=False` returns `{"status":"error","message":…}`.  
   - On success, instantiate `ReviewService(FilmReviewRepository(SessionLocal))`.  
   - Build a `Review` model merging `film_id` (path), `user_id` (auth), and payload fields.  
   - Call `add_review`; if `True` respond with `{"status":"success","result":review_object}` else error.  

2. **GET `/review/`** – `get_reviews` accepts optional query filters via `ReviewSearchingParams`.  
   - Auth check same as above.  
   - Service returns a list; response: `{"status":"success","result":reviews}`.  

3. **GET `/review/my`** – `get_my_reviews` forces a filter on `user_id` from auth data.  
   - Returns `{"status":"success","results":reviews}` (note plural key).  

4. **DELETE `/review/{review_id}`** – `delete_review` builds `ReviewSearchingParams` with `review_id` and `user_id`.  
   - If service reports success → `{"status":"success"}`; otherwise error payload.  

**Data Contract**  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `ReviewForAdd` | Pydantic model | Body for POST | Fields: `film_id`, `content`, `rate` |
| `ReviewSearchingParams` | Pydantic model | Query for GET /review | Optional filters (`user_id`, `film_id`, …) |
| `custom_session_id` | Cookie (str) | Auth token | Supplied to `verify_user`; `httponly=False`, 30‑day TTL |
| JSON response | dict | Output | Keys: `status` (`"success"`/`"error"`), `result`/`results` (payload), `message` (error text) |

> **Warning:** If `verify_user` cannot locate a valid `custom_session_id`, every endpoint short‑circuits with `"error"` and the provided `message`. No service logic is executed in that case. 
<a name="user-session-orm-models"></a>
## User & Session ORM Models  

`User` holds authentication data (`username`, hashed `_password`). The `password` property transparently hashes on set; `check_password` validates a clear‑text password.  
`Session` represents a login session; its PK `id` defaults to a random hash via `get_rand_hash`.

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| `User` | SQLAlchemy model | Authenticated account holder | Unique `username`; cascade delete of linked `WishList`. |
| `Session` | SQLAlchemy model | Cookie‑based authentication token | Primary key `id` (32‑char hash). |
| `User.password` | property | Hashes plain password on assignment | Uses `hash_password`. |
| `User.check_password` | method | Verifies password | Calls `verify_password`. | 
<a name="base-repository"></a>
## BaseRepository Core CRUD  

`BaseRepository` abstracts common DB actions using a supplied `session_factory`. It maintains a single session per repository instance (`curr_session`).  

| Method | Input | Output | Side Effects |
|--------|-------|--------|--------------|
| `read_by_options(schema, eager=False)` | Pydantic `BaseModel` with optional fields | `{"all": List[Model], "query": Query}` | Executes filtered `SELECT`. |
| `create(schema)` | Pydantic `BaseModel` | `(True, Model)` or `(False, None)` | `INSERT` + `commit`; rolls back on exception. |
| `read_by_id(schema, eager=False)` | Pydantic `BaseModel` (ID field) | Model instance or `None` | Calls `read_by_options`. |
| `update_element_by_id(schema_id, change_schema)` | ID schema, change schema | Updated Model or `None` | Sets attrs, `commit`, `refresh`. |
| `delete_object(schema)` | ID schema | `True`/`False` | `DELETE` + `commit`. |
| `__del__` | – | – | Closes the session if open. |

> **Warning:** If `verify_user` cannot locate a valid `custom_session_id`, every endpoint short‑circuits with `"error"` and the provided `message`. No service logic is executed in that case. 
<a name="concrete-repositories"></a>
## Concrete Repository Implementations  

| Repository | Base Class | Model |
|------------|------------|-------|
| `FilmRepository` | `BaseRepository` | `Film` |
| `FilmReviewRepository` | `BaseRepository` | `FilmReview` |
| `UserRepository` | `BaseRepository` | `User` |
| `SessionRepository` | `BaseRepository` | `Session` |

Each subclass simply forwards the `session_factory` and the associated SQLAlchemy model to `BaseRepository`, inheriting the full CRUD contract without additional logic. 
<a name="wish-list-repository-update"></a>
## `WishListRepository.update_element_films` – ORM‑Instance Patch & Commit  

**Responsibility**  
Persist a partial modification of a ``WishList`` ORM object (currently only the ``films`` collection). The method receives a *target identifier* (`schema_id`) and an *update payload* (`update_schema`), applies the changes in‑place, and finalises the transaction.

**Visible Inter‑layer Interactions**  
- Called by ``WishListService.add_film_to_wish_list`` and ``remove_film_from_wish_list``.  
- Operates on the SQLAlchemy ``Session`` supplied by the repository’s ``session_factory`` (no external API or auth involved).  

**Logic Flow**  

1. Retrieve the existing ``WishList`` row via ``read_by_id(schema_id)`` → ``curr_object``.  
2. Iterate over ``update_schema.model_dump()``; for each ``key, value`` pair execute ``setattr(curr_object, key, value)`` (special‑case handling for ``films`` is performed *before* this step).  
3. **Commit Block**  
   ```python
   try:
       session.commit()
       session.refresh(curr_object)
   except Exception:
       session.rollback()
       return False, None
   ```  
   - On success the DB row is refreshed to reflect any DB‑generated defaults.  
   - On failure the transaction is undone and a failure flag is returned.  
4. Return ``(True, curr_object)`` indicating a successful update.

**Data Contract**  

| Entity | Type | Role | Notes |
|--------|------|------|-------|
| ``schema_id`` | Pydantic model (e.g. ``WishListCreator``) | Identifies the wish‑list to patch | Passed to ``read_by_id`` |
| ``update_schema`` | Pydantic ``UpdateWishList`` | Dict of fields to modify; ``films`` is a ``list[int]`` | ``model_dump()`` yields a plain dict |
| ``curr_object`` | SQLAlchemy ``WishList`` instance | In‑memory ORM row receiving ``setattr`` | Refreshed after commit |
| Return | ``tuple[bool, WishList|None]`` | ``True`` + updated ORM on success, ``False`` + ``None`` on DB error | Mirrors repository contract |

> **Warning** – Only the ``films`` attribute receives pre‑processing (deduplication, ID resolution). All other keys are written verbatim; missing keys are ignored. 
