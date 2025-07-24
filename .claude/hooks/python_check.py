#!/usr/bin/env python3

import json
import sys
import subprocess
from pathlib import Path


def main():
    try:
        # Read input data from stdin
        stdin_content = sys.stdin.read().strip()
        
        # Handle empty input
        if not stdin_content:
            print('No input received')
            sys.exit(0)
        
        input_data = json.loads(stdin_content)

        tool_input = input_data.get("tool_input", {})
        print(tool_input)

        # Get file path from tool input
        file_path = tool_input.get("file_path")
        if not file_path:
            print('no file path')
            sys.exit(0)

        # Only check Python files
        if not file_path.endswith(".py"):
            print('no .py files')
            sys.exit(0)

        # Check if file exists
        if not Path(file_path).exists():
            print('file doesn\'t exist')
            sys.exit(0)

        # Run Pyright to check for type errors
        try:
            result = subprocess.run(
                ["pyright", file_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0 and (result.stdout or result.stderr):
                # Log the error for debugging
                log_file = Path(__file__).parent.parent / "pyright_errors.json"
                error_output = result.stdout or result.stderr
                error_entry = {
                    "file_path": file_path,
                    "errors": error_output,
                    "session_id": input_data.get("session_id"),
                }

                # Load existing errors or create new list
                if log_file.exists():
                    try:
                        with open(log_file, "r") as f:
                            content = f.read().strip()
                            if content:
                                errors = json.loads(content)
                            else:
                                errors = []
                    except (json.JSONDecodeError, FileNotFoundError):
                        errors = []
                else:
                    errors = []

                errors.append(error_entry)

                # Save errors
                with open(log_file, "w") as f:
                    json.dump(errors, f, indent=2)

                # Send error message to stderr for LLM to see
                print(f"Pyright errors found in {file_path}:", file=sys.stderr)
                print(error_output, file=sys.stderr)

                # Exit with code 2 to signal LLM to correct
                sys.exit(2)

        except subprocess.TimeoutExpired:
            print("Pyright check timed out", file=sys.stderr)
            sys.exit(0)
        except FileNotFoundError:
            # Pyright not available, skip check
            print('Pyright not found, skipping check')
            sys.exit(0)
        except Exception as subprocess_error:
            print(f"Subprocess error: {subprocess_error}", file=sys.stderr)
            sys.exit(0)

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error in pyright hook: {e}", file=sys.stderr)
        sys.exit(1)


main()