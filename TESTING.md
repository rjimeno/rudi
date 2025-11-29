# Testing Strategy for Rudi

This document describes the testing approach for Rudi: **unit tests** (fast, mocked) and **integration tests** (slow, real Ubuntu environment).

## Quick Start

```bash
# Unit tests only (fast, ~1 second)
make tests-unit

# Integration tests only (slow, ~2-3 minutes, requires Docker)
make tests-integration

# Run all tests
make tests

# Run all checks (setup-dev, tests, lint)
make all
```

## Testing Pyramid

```
        ┌──────────────────────────┐
        │ Integration Tests        │  5-10% of tests
        │ (Docker, real Ubuntu)    │  Slow but high-confidence
        ├──────────────────────────┤
        │ Unit Tests               │  90-95% of tests
        │ (Mocked subprocess, fs)  │  Fast and isolated
        └──────────────────────────┘
```

## Unit Tests (`tests/test_rudi.py`, `tests/test_rudi_constants.py`)

### What They Test
- YAML manifest parsing (Services, Packages, Files, Evictions sections)
- File deployment logic (`do_file` function)
- Service lifecycle (stop → install → deploy → start)
- Package evictions
- Warning diagnostics for missing files
- Module constants and function existence

### Key Feature: Mocking
All subprocess calls and file operations are **mocked** using `unittest.mock`. This means:
- ✅ No actual packages installed
- ✅ No real files created
- ✅ No services restarted
- ✅ **Very fast** (~0.15 seconds)
- ✅ Safe to run on any machine

### Run Unit Tests
```bash
make tests-unit
```

### Example Unit Test
```python
@patch("subprocess.run")
@patch("builtins.open", new_callable=mock_open)
def test_do_file_basic_flow(self, mock_file, mock_run):
    """Verify do_file writes content and sets permissions."""
    mock_run.return_value = Mock(returncode=0)
    
    file_spec = {
        "base": "/tmp/test_rudi_/",
        "name": "test.txt",
        "content": "hello world",
        "owner": "root",
        "group": "root",
        "mode": "644"
    }
    
    rudy.do_file(file_spec)
    
    # Verify mkdir, chown, chgrp, chmod were called
    mkdir_calls = [c for c in mock_run.call_args_list if "mkdir" in str(c)]
    self.assertTrue(len(mkdir_calls) > 0)
```

## Integration Tests (`tests/integration/*.sh`)

### What They Test
Real Rudi behavior in a **real Ubuntu environment** using Docker:

| Test              | File                          | Purpose                           |
|-------------------|-------------------------------|-----------------------------------|
| Basic manifest    | `test_basic_manifest.sh`      | Deploy files (helloPhpInfo.yaml)  |
| Default manifest  | `test_default_manifest.sh`    | Load rudi.yaml by default         |
| Evictions         | `test_evictions.sh`           | Remove packages                   |
| Cron deployment   | `test_cron_deployment.sh`     | Deploy config + restart service   |

### Key Feature: Real System
Each test runs in a fresh Docker container with:
- ✅ Real `apt-get` package manager
- ✅ Real `service` command
- ✅ Real file system with correct permissions
- ✅ Real Ubuntu environment (catches environment-specific bugs)
- ❌ **Slower** (~1-2 minutes per test)
- ❌ Requires Docker installed

### Run Integration Tests
```bash
# Requires Docker
make tests-integration

# Or run individual tests
bash tests/integration/test_basic_manifest.sh
bash tests/integration/test_evictions.sh
```

### Example Integration Test
```bash
#!/bin/bash
set -e

docker run --rm ubuntu:24.04 bash -c '
  apt-get update
  apt-get install -y git python3-yaml
  
  git clone https://github.com/rjimeno/rudi.git /app
  cd /app
  python3 rudi.py helloPhpInfo.yaml
  
  # Verify file was actually deployed
  [ -f /var/www/html/hello.php ] || exit 1
'
```

## When to Run Each

| Scenario                                  | Test          | Command                   |
|-------------------------------------------|---------------|---------------------------|
| **During development** (quick feedback)   | Unit only     | `make tests-unit`         |
| **Before commit** (fast validation)       | Unit only     | `make tests-unit`         |
| **Before PR/merge** (full validation)     | Both          | `make tests`              |
| **In CI/CD pipeline**                     | Both          | `make tests`              |
| **Debugging real issues**                 | Integration   | `make tests-integration`  |

## Adding New Tests

### Adding a Unit Test

Add a test method to `tests/test_rudi.py`:

```python
@patch("subprocess.run")
def test_my_new_feature(self, mock_run):
    """Test description."""
    mock_run.return_value = Mock(returncode=0)
    
    # Call your function
    rudy.my_function(...)
    
    # Assert mocked calls
    self.assertTrue(mock_run.called)
```

Then run:
```bash
make tests-unit
```

### Adding an Integration Test

1. Create `tests/integration/test_my_feature.sh`
2. Use the standard Docker pattern:

```bash
#!/bin/bash
set -e

echo "Running integration test: My feature..."

docker run --rm ubuntu:24.04 bash -c '
  apt-get update > /dev/null 2>&1
  apt-get install -y git python3-yaml > /dev/null 2>&1
  
  git clone https://github.com/rjimeno/rudi.git /app > /dev/null 2>&1
  cd /app
  
  # Test your feature
  python3 rudi.py my_manifest.yaml
  
  # Verify expected outcome
  [ -f /expected/file ] || exit 1
'

echo "✓ Integration test PASSED: My feature"
```

3. Make it executable:
```bash
chmod +x tests/integration/test_my_feature.sh
```

4. Add to Makefile `tests-integration` target:
```makefile
@bash tests/integration/test_my_feature.sh
```

5. Run:
```bash
make tests-integration
```

## Expected Test Results

### Unit Tests Pass
```
============================= test session starts ==============================
collected 15 items

tests/test_rudi.py::TestRudyYAMLLoading::test_evictions_manifest PASSED
tests/test_rudi.py::TestRudyYAMLLoading::test_manifest_with_files_and_packages PASSED
tests/test_rudi.py::TestRudyFileDeployment::test_do_file_basic_flow PASSED
tests/test_rudi.py::TestRudyConverge::test_converge_installs_packages PASSED
tests/test_rudi_constants.py::TestRudiConstants::test_default_config_file PASSED
... (15 total)

============================== 15 passed in 0.15s ==============================
```

### Integration Tests Pass
```
Running integration test: Basic manifest execution...
✓ Integration test PASSED: Basic manifest execution
Running integration test: Default manifest (rudi.yaml)...
✓ Integration test PASSED: Default manifest execution
Running integration test: Package eviction...
✓ Integration test PASSED: Package eviction
Running integration test: Cron configuration deployment...
✓ Integration test PASSED: Cron configuration deployment

✓ All integration tests PASSED
```

## Troubleshooting

### Unit Tests Fail
1. Check Python version: `python3 --version`
2. Install dependencies: `make setup-dev`
3. Run with verbose output: `make tests-unit`

### Integration Tests Fail
1. Verify Docker is installed: `docker --version`
2. Check network access (docker needs internet to clone repo): `docker run ubuntu:24.04 curl -I google.com`
3. Run individual test with output: `bash tests/integration/test_basic_manifest.sh`

### Docker Image Too Large/Old
Integrate tests pull `ubuntu:24.04` on first run (~150MB download). To refresh:
```bash
docker pull ubuntu:24.04
```

## CI/CD Integration

In GitHub Actions or similar:

```yaml
- name: Unit tests
  run: make tests-unit

- name: Integration tests (requires Docker)
  run: make tests-integration
```

Or skip integration tests if Docker unavailable:

```yaml
- name: Unit tests
  run: make tests-unit

- name: Integration tests
  if: runner.os == 'Linux'  # Only run on Linux runners with Docker
  run: make tests-integration
```

## Summary

| Aspect            | Unit Tests        | Integration Tests             |
|-------------------|-------------------|-------------------------------|
| Speed             | ~0.15s            | ~2-3 minutes                  |
| Safety            | ✅ Very safe      | ✅ Safe (isolated containers) |
| Real systems      | ❌ No (mocked)    | ✅ Yes (Ubuntu)               |
| Easy to debug     | ✅ Yes            | ⚠️ Harder (container context) |
| CI/CD friendly    | ✅ Yes            | ⚠️ Requires Docker            |
| Coverage          | ✅ Good (logic)   | ✅ High (real behavior)       |

**Best practice:** Run unit tests during development and before every commit; run full test suite before merging to main branch.
