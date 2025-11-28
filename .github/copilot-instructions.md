# Rudi Copilot Instructions

## Purpose

Provide concise, repo-specific guidance so an AI coding agent can be productive working on **Rudi**.

## Project Overview

- **Type:** Small, single-script configuration-management tool implemented in Python (`rudi.py`) driven by YAML node manifests (`rudi.yaml`, `local.yaml`, etc.).
- **How it works:** `rudi.py` loads a YAML document and performs three kinds of actions: install/reinstall packages via `apt-get`, deploy files (create directories, write content, chown/chmod), and restart services via `/usr/sbin/service`.

## Key Files

- **`rudi.py`**: Main program. Look here first for runtime behavior, constants (`DPKG`, `SERVICE`, `CHOWN`, `CHMOD`, etc.), and error/exit patterns.
- **`rudi.yaml`, `local.yaml`, `evictCronPhp5Apache2.yaml`, `helloPhpInfo.yaml`**: Example configuration manifests; copy formats from these when creating new test manifests.
- **`rudi.md`**: Long-form usage notes and YAML semantics; includes important details like case-sensitivity of keys (`Services` vs `services`, `Packages` vs `packages`).
- **`README.md`**: High-level description and pointers to `rudi.md`.

## Architecture & Patterns

- **YAML-driven:** The code expects top-level keys like `Services`, `Packages`, `Files`, and `Evictions`. These are case-sensitive and have distinct roles.
- **Files abstraction:** `Files` entries contain `base`, `name`, `content`, `owner`, `group`, `mode`. The script concatenates `base + name` to create file paths and uses these metadata fields directly.
- **Packages & Services relationship:** `Services` maps service names to a `packages:` list, and each package listed under `Packages` may list `files:` that should be deployed when that package is installed.
- **System-level side effects:** The script invokes system commands (`apt-get`, `service`, `chown`, `chmod`) and must be run as root. Changes are not sandboxed—do not run against production machines.

## Developer Workflows / Commands

- **Run locally (manual):** `sudo python3 rudi.py` — uses `rudi.yaml` by default.
- **Run with a specific manifest:** `sudo python3 rudi.py evictCronPhp5Apache2.yaml` (examples in `rudi.md`).
- **Dependencies:** `PyYAML` is required. On Debian/Ubuntu install via `sudo apt-get install -y python3-yaml` or use a virtualenv and `pip install pyyaml`.
- **Run tests:** `make tests` (see `Makefile` and `tests/` directory).

## Patterns & Conventions for Agents

- **Be conservative modifying system-call code:** `rudi.py` uses `subprocess.run(..., shell=True, check=True)` widely. If you change command invocation, add testable abstractions or wrap subprocesses so they can be tested without invoking the system.
- **Respect key capitalization:** The project intentionally (if confusingly) distinguishes `Packages` vs `packages` and `Files` vs `files`. Follow existing keys when creating new manifests.
- **Error handling style:** The script prints diagnostics and calls `sys.exit(code)` on failures. Preserve the exit-code conventions if you change logic.
- **YAML examples are authoritative:** Use the files in the repository as canonical examples for structure and edge cases (e.g., `Evictions` being a list of package names).

## Safe Change Checklist

- **Non-destructive testing:** Add unit tests that mock `subprocess.run` and file writes before changing `rudi.py` behavior.
- **Add tests incrementally:** Start by extracting small, testable functions (e.g., a command-runner wrapper) and add tests for YAML parsing and `do_file` logic using temporary directories.
- **Document changes in `rudi.md`** when behavioral or manifest semantics change.
- **Run tests before push:** Execute `make tests` locally to verify changes pass all test suites.

## Example Commands

- **Run default manifest:** `sudo python3 rudi.py`
- **Deploy the hello.php example manifest:** `sudo python3 rudi.py helloPhpInfo.yaml`
- **Run tests:** `make tests`

## Where to Look for Similar Code / Pitfalls

- `rudi.py` top constants (search for `DPKG`, `SERVICE`) show where to change system command behavior. Update these constants rather than scattering literal strings.
- Warnings are printed when `Packages` references a file not present under `Files:` — preserve or improve these diagnostics rather than removing them.
