# text_test: Grassroots Testing for the Text Module

This package provides a minimal, isolated environment for grassroots testing of the text module's actions and faculties, as per the unified interactible object design.

## Structure
- `__init__.py`: Marks this directory as a package.
- `__main__.py`: Allows running `python -m backend.text_test` to verify the package is set up and runnable.
- `unit_test.py`: Contains (or will contain) unittests for text module actions/faculties. Run with `python -m backend.text_test.unit_test`.
- `demo_test.py`: For quick, script-style demos of text module features. Run with `python -m backend.text_test.demo_test`.

## Usage

- **Run package entry point:**
  ```sh
  python -m backend.text_test
  ```
- **Run unit tests:**
  ```sh
  python -m backend.text_test.unit_test
  ```
- **Run demo test:**
  ```sh
  python -m backend.text_test.demo_test
  ```

## Purpose
This package is for rapid, grassroots-level testing and demonstration of the text module's core logic, actions, and object/faculty handling, in line with the attached design document. Expand with more tests and demos as needed. 