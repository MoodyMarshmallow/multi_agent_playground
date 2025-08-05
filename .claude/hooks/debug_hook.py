#!/usr/bin/env python3

import sys
import json

def main():
    try:
        # Debug: write all stdin to a file
        stdin_content = sys.stdin.read()
        with open("hook_debug.txt", "w") as f:
            f.write(f"STDIN content: '{stdin_content}'\n")
            f.write(f"STDIN length: {len(stdin_content)}\n")
            f.write(f"STDIN repr: {repr(stdin_content)}\n")
        
        if not stdin_content.strip():
            print("No input received", file=sys.stderr)
            sys.exit(0)
            
        input_data = json.loads(stdin_content)
        print("JSON parsed successfully", file=sys.stderr)
        
    except Exception as e:
        with open("hook_debug.txt", "a") as f:
            f.write(f"Error: {e}\n")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()