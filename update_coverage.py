#!/usr/bin/env python3
import subprocess
import json
import re
import sys

def main():
    print("Running tests and calculating coverage...")
    try:
        # Run pytest with coverage
        # We target both component and unit tests to get full coverage
        cmd = [
            "pytest",
            "tests/component/",
            "tests/unit/",
            "--cov=custom_components.meteocat_community_edition",
            "--cov-report=term-missing"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.returncode != 0:
            print("Tests failed!", file=sys.stderr)
            sys.exit(1)

        # Extract coverage percentage from stdout
        # Pattern looks like: "TOTAL ... 96%"
        match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", result.stdout)
        if not match:
            # Try to find the line "Required test coverage of X% reached. Total coverage: Y%"
            match = re.search(r"Total coverage: (\d+\.?\d*)%", result.stdout)

        if match:
            coverage_pct = float(match.group(1))
            print(f"Detected coverage: {coverage_pct}%")
            
            # Generate shields.io endpoint json
            # Color logic: <80 red, <90 orange, <95 yellow, >=95 green
            if coverage_pct < 80:
                color = "red"
            elif coverage_pct < 90:
                color = "orange"
            elif coverage_pct < 95:
                color = "yellow"
            else:
                color = "brightgreen"
            
            data = {
                "schemaVersion": 1,
                "label": "coverage",
                "message": f"{coverage_pct:.1f}%",
                "color": color
            }
            
            with open("coverage.json", "w") as f:
                json.dump(data, f, indent=2)
            
            if coverage_pct < 95:
                print(f"WARNING: Coverage {coverage_pct}% is below required 95%!")
                # We don't exit 1 here because the prompt says "Avisa", not "Falla"
            else:
                print("Coverage updated successfully.")
        else:
            print("Could not parse coverage percentage.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
