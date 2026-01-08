#!/usr/bin/env python3
import subprocess
import re
import json
import sys

def get_coverage_color(coverage):
    if coverage >= 95:
        return "brightgreen"
    elif coverage >= 90:
        return "green"
    elif coverage >= 80:
        return "yellowgreen"
    elif coverage >= 70:
        return "yellow"
    elif coverage >= 60:
        return "orange"
    else:
        return "red"

def main():
    print("Running tests with coverage...")
    try:
        # Run pytest and capture output
        result = subprocess.run(
            ["pytest", "--cov=custom_components.meteocat_community_edition", "tests/"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        output = result.stdout
        print(output)
        
        # Look for the TOTAL line
        # TOTAL                                                             2550     89    97%
        match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
        if not match:
            # Try finding the final "Total coverage: XX.XX%" line from our previous output
            match = re.search(r'Total coverage:\s+([0-9.]+)', output)
            
        if match:
            coverage_pct = float(match.group(1))
            print(f"Detected coverage: {coverage_pct}%")
            
            # Generate JSON for Shield
            badge_data = {
                "schemaVersion": 1,
                "label": "coverage",
                "message": f"{coverage_pct}%",
                "color": get_coverage_color(coverage_pct)
            }
            
            with open("coverage.json", "w") as f:
                json.dump(badge_data, f, indent=2)
            
            print("Updated coverage.json")
            
        else:
            print("Could not parse coverage percentage from output.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
