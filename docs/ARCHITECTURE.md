# LockIt — Architecture

## 1. Overview

LockIt is a desktop file-encryption application built with **PySide6** and
**Clean Architecture** principles. The codebase is organized into
independent layers so that business logic (encryption, validation, file
handling) has zero dependency on the UI framework, and the UI has zero
dependency on how encryption is implemented internally.

Dependency direction always points **inward**, toward `core`:

```
ui  →  services  →  core
              ↑
          workers
```

- `ui` depends on `services` and `core` types, never the reverse.
- `services` orchestrates `core` logic for the UI layer.
- `workers` run `services`/`core` operations off the UI thread.
- `core` depends on nothing else in the project — it is pure, testable
  business logic.

This means the encryption engine could be reused in a CLI tool or a web
backend without modification, and the UI could be swapped for a different
framework without touching a single line of cryptography code.

## 2. Folder-by-folder breakdown

### `assets/`
Static, non-code resources bundled with the application.
- `assets/icons/` — SVG/PNG icons used across the UI (sidebar, buttons, status).
- `assets/images/` — Illustrations, backgrounds, empty-state graphics.
- `assets/fonts/` — Bundled font files, so typography is identical across OSes.

### `ui/`
Everything related to presentation. No encryption logic, no file I/O
business rules — only how things look and how user input is captured and
forwarded to `services`.
- `ui/windows/` — Top-level `QMainWindow` subclasses (e.g. `MainWindow`).
- `ui/dialogs/` — Modal/non-modal `QDialog` subclasses (password prompts,
  confirmation dialogs, about box).
- `ui/widgets/` — Reusable custom widgets (buttons, password strength bar,
  drag-and-drop zone, sidebar item) used across multiple windows/dialogs.
- `ui/layouts/` — Composed layout helpers/containers that arrange widgets
  into larger reusable sections (e.g. the sidebar layout, the file-details
  panel layout).
- `ui/styles/` — QSS stylesheets and theme definitions (dark/light/auto),
  plus any style-loading helpers.

### `core/`
Pure business logic. Framework-agnostic, fully unit-testable, no Qt
imports allowed here.
- `core/crypto/` — AES-256 encryption/decryption engine, PBKDF2 key
  derivation, salt/IV generation. Implemented in Phase 3.
- `core/security/` — Password strength scoring, secure memory helpers,
  secure random utilities, security policy constants.
- `core/files/` — File reading/writing abstractions, metadata extraction,
  the `.lockit` container format (header + salt + IV + ciphertext).
- `core/validators/` — Input validation (file paths, password rules,
  file size limits) shared by both UI and services.

### `services/`
The orchestration layer between `ui` and `core`. A service coordinates
multiple `core` components to fulfill a use case (e.g.
`EncryptionService.encrypt_file(path, password)` combines `core.crypto`,
`core.files`, and `core.validators`). Services expose a UI-friendly API
and are what `workers` and `ui` actually call.

### `workers/`
`QThread`/`QRunnable`-based background workers that invoke `services`
without blocking the UI thread. Responsible for emitting progress signals,
supporting cancellation, and translating exceptions into UI-safe error
signals.

### `config/`
Application configuration and constants.
- `config/constants.py` — Immutable app-wide values (name, version,
  window sizing, file extensions).
- `config/paths.py` — Cross-platform filesystem path resolution (user
  data directory, logs directory, config directory) following OS
  conventions (XDG on Linux, `AppData` on Windows, `Application Support`
  on macOS).
- Future phases add `config/settings.py` (persisted user preferences)
  and `config/themes.py` (theme token definitions).

### `utils/`
Small, generic, cross-cutting helpers with no business meaning of their
own — e.g. `utils/logger.py` (loguru setup). Utilities must not depend on
`ui`, `services`, or `core`.

### `tests/`
Mirrors the `core`/`services`/`utils` package structure. Unit tests for
pure logic, integration tests for service-level flows, and `pytest-qt`
tests for UI behavior. Populated primarily in Phase 9.

### `docs/`
Architecture notes, developer guides, and screenshots for the final
GitHub-ready README (Phase 10).

### Root files
- `main.py` — Application entry point; bootstraps logging and Qt, then
  launches `MainWindow`. Contains no business logic.
- `requirements.txt` / `requirements-dev.txt` — Pinned runtime and
  development dependencies.
- `pyproject.toml` — Tooling configuration (black, ruff, mypy, pytest).
- `.gitignore` — Excludes build artifacts, virtual environments, logs,
  and local user settings from version control.
- `LICENSE` — MIT license.
- `README.md` — Project overview (expanded significantly in Phase 10).

## 3. Why Clean Architecture here

File encryption software has an unusually high cost of bugs: a defect in
`core/crypto` can mean unrecoverable data loss. Isolating `core` from the
UI means:

1. **Testability** — encryption logic can be exhaustively unit-tested
   without spinning up Qt or touching the filesystem beyond temp files.
2. **Auditability** — a security reviewer can audit `core/crypto` and
   `core/security` in isolation, without wading through UI code.
3. **Longevity** — if LockIt ever moves to a different GUI toolkit or
   gains a CLI/headless mode, `core` and `services` are reusable as-is.

## 4. Threading model (introduced fully in Phase 4–5)

Encryption/decryption of large files must never block the UI thread.
`workers/` will host `QThread` subclasses that:
- Accept a `services.EncryptionService` (or `DecryptionService`) call.
- Emit `progress_changed(int)`, `finished(result)`, and `error(str)`
  Qt signals.
- Support cooperative cancellation via a thread-safe flag checked
  between chunked read/write operations.

## 5. Security posture (implemented in Phase 3, hardened in Phase 8)

- **AES-256** in an authenticated mode via the `cryptography` library.
- **PBKDF2-HMAC-SHA256** for password-based key derivation, with a
  cryptographically random salt per file and a high, configurable
  iteration count.
- **Random IV** generated per encryption operation — never reused.
- Passwords are **never persisted**; only derived keys exist transiently
  in memory during an operation.
- Existing files are never overwritten without explicit user
  confirmation.
- Logging (`utils/logger.py`) is designed to never receive secrets —
  this is enforced by convention and reviewed every phase.
