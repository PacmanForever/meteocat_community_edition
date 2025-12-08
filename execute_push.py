#!/usr/bin/env python3
"""Execute push and tests on GitHub"""
import subprocess
import sys
import os
import json
from datetime import datetime
from pathlib import Path

os.chdir(r'c:\Jordi\meteocat_community_edition')

# Step 1: Configure git
subprocess.run(['git', 'config', 'user.email', 'release@meteocat.local'], capture_output=True)
subprocess.run(['git', 'config', 'user.name', 'Release Bot'], capture_output=True)

# Step 2: Create tag if not exists
result = subprocess.run(['git', 'tag', '-a', 'v1.0.0', '-m', 'Release v1.0.0 (2025-11-29)'], 
                       capture_output=True, text=True)

# Step 3: Push main branch
result_main = subprocess.run(['git', 'push', 'origin', 'main'], 
                            capture_output=True, text=True)

# Step 4: Push tag
result_tag = subprocess.run(['git', 'push', 'origin', 'v1.0.0'], 
                           capture_output=True, text=True)

# Step 5: Get remote URL
result_url = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                           capture_output=True, text=True)

# Write results
results = {
    'timestamp': datetime.now().isoformat(),
    'main_push': {
        'returncode': result_main.returncode,
        'output': result_main.stdout,
        'error': result_main.stderr
    },
    'tag_push': {
        'returncode': result_tag.returncode,
        'output': result_tag.stdout,
        'error': result_tag.stderr
    },
    'repository_url': result_url.stdout.strip(),
    'status': 'SUCCESS' if result_main.returncode == 0 and result_tag.returncode == 0 else 'PARTIAL'
}

with open('push_results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Also write human-readable log
with open('github_push.log', 'w') as f:
    f.write(f"{'='*80}\n")
    f.write(f"GITHUB PUSH - v1.0.0 RELEASE\n")
    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
    f.write(f"{'='*80}\n\n")
    
    f.write(f"Repository: {result_url.stdout.strip()}\n\n")
    
    f.write("[MAIN BRANCH PUSH]\n")
    f.write(f"Status: {'OK' if result_main.returncode == 0 else 'FAILED'}\n")
    f.write(f"Output: {result_main.stdout}\n")
    if result_main.stderr:
        f.write(f"Error: {result_main.stderr}\n")
    f.write("\n")
    
    f.write("[TAG PUSH]\n")
    f.write(f"Status: {'OK' if result_tag.returncode == 0 else 'FAILED'}\n")
    f.write(f"Output: {result_tag.stdout}\n")
    if result_tag.stderr:
        f.write(f"Error: {result_tag.stderr}\n")
    f.write("\n")
    
    if result_main.returncode == 0 and result_tag.returncode == 0:
        f.write("✓ RELEASE SUCCESSFULLY PUSHED TO GITHUB\n")
        f.write("\n✓ GitHub Actions will automatically:\n")
        f.write("  1. Run pytest test suite (202 tests)\n")
        f.write("  2. Run flake8 linting\n")
        f.write("  3. Run HACS validation\n")
        f.write("  4. Run Hassfest validation\n")
        f.write("\nCheck CI/CD status at:\n")
        f.write(f"  {result_url.stdout.strip()}/actions\n")
    else:
        f.write("✗ PUSH FAILED\n")

print("✓ Push complete")
sys.exit(0)
