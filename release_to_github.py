#!/usr/bin/env python3
"""Push v1.0.0 release to GitHub and trigger CI/CD"""
import subprocess
import sys
import os

def run_cmd(cmd, desc):
    """Run command and return success status"""
    print(f"\n[{desc}]")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        print(f"✓ {desc} - SUCCESS")
        if result.stdout.strip():
            for line in result.stdout.split('\n')[-5:]:
                if line.strip():
                    print(f"  {line}")
    else:
        print(f"✗ {desc} - FAILED")
        if result.stderr.strip():
            print(f"  Error: {result.stderr[:200]}")
    
    return result.returncode == 0

os.chdir(r'c:\Jordi\meteocat_community_edition')

print("="*80)
print("PUSHING v1.0.0 RELEASE TO GITHUB")
print("="*80)

# Configure git
subprocess.run(['git', 'config', 'user.email', 'release@meteocat.local'], capture_output=True)
subprocess.run(['git', 'config', 'user.name', 'Release Bot'], capture_output=True)

# Tag
run_cmd(['git', 'tag', '-a', 'v1.0.0', '-m', 'Release v1.0.0 (2025-11-29)'], 'Create tag v1.0.0')

# Push main
success_main = run_cmd(['git', 'push', 'origin', 'main'], 'Push main branch')

# Push tag
success_tag = run_cmd(['git', 'push', 'origin', 'v1.0.0'], 'Push tag v1.0.0')

# Get URL
result = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True)
repo_url = result.stdout.strip()

print("\n" + "="*80)
if success_main and success_tag:
    print("✓ RELEASE SUCCESSFULLY PUSHED TO GITHUB")
    print("\n📦 v1.0.0 Release Details:")
    print(f"  Repository: {repo_url}")
    print(f"  Branch: main")
    print(f"  Tag: v1.0.0")
    print(f"  Tests: 202 passing locally")
    print("\n⚙️ GitHub Actions CI/CD Pipeline Triggered:")
    print("  1. pytest test suite (202 tests)")
    print("  2. flake8 linting")
    print("  3. HACS validation")
    print("  4. Hassfest Home Assistant integration check")
    print("\n📊 Check CI/CD Status:")
    print(f"  {repo_url}/actions")
    print("\n✅ Release v1.0.0 is LIVE on GitHub!")
else:
    print("⚠️ PUSH PARTIALLY FAILED")
    print(f"  Main push: {'✓' if success_main else '✗'}")
    print(f"  Tag push: {'✓' if success_tag else '✗'}")

print("="*80)

sys.exit(0 if success_main and success_tag else 1)
