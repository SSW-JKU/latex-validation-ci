# SSW LaTeX Validation CI

[![status](https://github.com/SSW-JKU/latex-validation-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/SSW-JKU/latex-validation-ci/actions/workflows/ci.yml)

This action, used at the [SSW](https://ssw.jku.at/) at the [JKU](https://www.jku.at/), is configured to automatically spell check and lint exercise files upon commit.

## Development

### Pre-Commit Checks

This repository uses [pre-commit](https://pre-commit.com/) to automatically check and format files before each commit.

#### Available Hooks
* **lint** (`make lint`): Lints Python source files
* **typecheck** (`make typecheck`): Performs static type checking on Python source files
* **conventional commits**: Enforces [conventional commit](https://www.conventionalcommits.org/) messages.

#### Setup

1. **Install `pre-commit`**:
   ```bash
   pip install pre-commit
   ```

2. **Install hooks**
   ```bash
   pre-commit install
   ```

3. (optionally) **Run on all files**
   ```bash
   pre-commit run --all-files
   ```

## Contributors
- [Katu603](https://github.com/Katu603)
- [skloibi](https://github.com/skloibi)


