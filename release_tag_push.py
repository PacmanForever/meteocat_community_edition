#!/usr/bin/env python3
import subprocess
import sys
import os
from datetime import datetime

os.chdir(r'c:\Jordi\meteocat_community_edition')
log_path = r'c:\Jordi\meteocat_community_edition\release_tag_push.log'

with open(log_path, 'w', encoding='utf-8') as log:
    log.write(f"{'='*80}\n")
    log.write(f"RELEASE v1.0.0 - TAG AND PUSH\n")
    log.write(f"Started: {datetime.now().isoformat()}\n")
    log.write(f"{'='*80}\n\n")
    
    # Configure git identity
    log.write("[STEP 0] Configure Git Identity\n")
    log.write("-" * 80 + "\n")
    subprocess.run(['git', 'config', 'user.email', 'release@meteocat.local'], capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Release Bot'], capture_output=True)
    log.write("Git identity configured\n\n")
    
    # Step 1: Check current status
    log.write("[STEP 1] Git Status Check\n")
    log.write("-" * 80 + "\n")
    result = subprocess.run(['git', 'log', '--oneline', '-1'], capture_output=True, text=True)
    log.write(f"Latest commit: {result.stdout.strip()}\n\n")
    
    # Step 2: Create annotated tag
    log.write("[STEP 2] Create Git Tag\n")
    log.write("-" * 80 + "\n")
    result = subprocess.run(
        ['git', 'tag', '-a', 'v1.0.0', '-m', 'Release v1.0.0 (2025-11-29)'],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode == 0:
        log.write("✓ Tag v1.0.0 created successfully\n")
    else:
        if 'already exists' in result.stderr:
            log.write("⚠ Tag v1.0.0 already exists (OK)\n")
        else:
            log.write(f"✗ Error creating tag: {result.stderr}\n")
    
    # Verify tag was created
    result = subprocess.run(['git', 'tag', '-l', 'v1.0.0'], capture_output=True, text=True)
    if result.stdout.strip():
        log.write(f"  Verified: {result.stdout.strip()}\n\n")
    
    # Step 3: Push to remote
    log.write("[STEP 3] Push to Remote\n")
    log.write("-" * 80 + "\n")
    
    # Push main branch
    log.write("Pushing main branch...\n")
    result = subprocess.run(
        ['git', 'push', 'origin', 'main'],
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode == 0:
        log.write("✓ Main branch pushed successfully\n")
        log.write(f"  {result.stdout.strip()}\n")
    else:
        if 'up to date' in result.stderr.lower():
            log.write("✓ Main branch already up to date\n")
        else:
            log.write(f"⚠ Push output: {result.stderr}\n")
    
    # Push tag
    log.write("\nPushing tag v1.0.0...\n")
    result = subprocess.run(
        ['git', 'push', 'origin', 'v1.0.0'],
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode == 0:
        log.write("✓ Tag v1.0.0 pushed successfully\n")
        log.write(f"  {result.stdout.strip()}\n")
    else:
        if 'already exists' in result.stderr or 'up to date' in result.stderr.lower():
            log.write("✓ Tag already pushed or up to date\n")
        else:
            log.write(f"⚠ Push output: {result.stderr}\n")
    
    # Step 4: Verify remote
    log.write("\n[STEP 4] Verify Remote Status\n")
    log.write("-" * 80 + "\n")
    result = subprocess.run(['git', 'branch', '-v'], capture_output=True, text=True)
    log.write("Local branches:\n")
    for line in result.stdout.split('\n')[:5]:
        if line.strip():
            log.write(f"  {line}\n")
    
    result = subprocess.run(['git', 'tag', '-l'], capture_output=True, text=True)
    log.write("\nLocal tags:\n")
    for line in result.stdout.split('\n'):
        if line.strip():
            log.write(f"  {line}\n")
    
    log.write(f"\n{'='*80}\n")
    log.write(f"RELEASE v1.0.0 READY\n")
    log.write(f"Completed: {datetime.now().isoformat()}\n")
    log.write(f"{'='*80}\n")
    log.write("\nNext steps:\n")
    log.write("1. Verify tag and push on GitHub: https://github.com/PacmanForever/meteocat_community_edition\n")
    log.write("2. Create release from tag on GitHub Releases\n")
    log.write("3. Update documentation/announcements\n")

print("✓ Release process complete. See release_tag_push.log")
