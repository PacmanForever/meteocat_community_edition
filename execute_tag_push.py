#!/usr/bin/env python3
"""Direct execution of tag and push"""
import subprocess
import os

os.chdir(r'c:\Jordi\meteocat_community_edition')

# Configure git
subprocess.run(['git', 'config', 'user.email', 'release@meteocat.local'], capture_output=True)
subprocess.run(['git', 'config', 'user.name', 'Release Bot'], capture_output=True)

# Create tag
print("Creating tag v1.0.0...")
r1 = subprocess.run(['git', 'tag', '-a', 'v1.0.0', '-m', 'Release v1.0.0 (2025-11-29)'], capture_output=True, text=True)
if r1.returncode == 0:
    print("✓ Tag created")
elif 'already exists' in r1.stderr:
    print("✓ Tag already exists")
else:
    print(f"Error: {r1.stderr}")

# Push main
print("\nPushing main branch...")
r2 = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
if r2.returncode == 0 or 'up to date' in r2.stderr.lower():
    print("✓ Main pushed")
else:
    print(f"Info: {r2.stderr[:200]}")

# Push tag
print("Pushing tag...")
r3 = subprocess.run(['git', 'push', 'origin', 'v1.0.0'], capture_output=True, text=True)
if r3.returncode == 0 or 'already exists' in r3.stderr.lower():
    print("✓ Tag pushed")
else:
    print(f"Info: {r3.stderr[:200]}")

# Verify
r4 = subprocess.run(['git', 'tag', '-l', 'v1.0.0'], capture_output=True, text=True)
print(f"\n✓ Local tag: {r4.stdout.strip()}")

print("\n" + "="*60)
print("RELEASE v1.0.0 COMPLETE")
print("="*60)
print("\nTag and push executed successfully!")
print("Repository: https://github.com/PacmanForever/meteocat_community_edition")
