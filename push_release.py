#!/usr/bin/env python3
import subprocess
import sys
import os
from datetime import datetime

os.chdir(r'c:\Jordi\meteocat_community_edition')
log_path = r'c:\Jordi\meteocat_community_edition\github_release.log'

with open(log_path, 'w', encoding='utf-8') as log:
    log.write(f"{'='*80}\n")
    log.write(f"GITHUB RELEASE v1.0.0 - PUSH AND TAG\n")
    log.write(f"Started: {datetime.now().isoformat()}\n")
    log.write(f"{'='*80}\n\n")
    
    try:
        # Configure git
        log.write("[STEP 1] Configure Git Identity\n")
        log.write("-" * 80 + "\n")
        subprocess.run(['git', 'config', 'user.email', 'release@meteocat.local'], capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Release Bot'], capture_output=True)
        log.write("✓ Git configured\n\n")
        
        # Check remote
        log.write("[STEP 2] Check Remote Configuration\n")
        log.write("-" * 80 + "\n")
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        log.write("Git remotes:\n")
        log.write(result.stdout + "\n")
        
        # Create tag
        log.write("[STEP 3] Create Git Tag v1.0.0\n")
        log.write("-" * 80 + "\n")
        result = subprocess.run(
            ['git', 'tag', '-a', 'v1.0.0', '-m', 'Release v1.0.0 (2025-11-29) - First stable release'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            log.write("✓ Tag created: v1.0.0\n")
        else:
            log.write(f"✗ Tag creation failed: {result.stderr}\n")
        log.write("\n")
        
        # Push to origin/main
        log.write("[STEP 4] Push Main Branch\n")
        log.write("-" * 80 + "\n")
        result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            log.write("✓ Main branch pushed\n")
            log.write(result.stdout + "\n")
        else:
            log.write(f"✗ Push failed: {result.stderr}\n")
        log.write("\n")
        
        # Push tag
        log.write("[STEP 5] Push Tag v1.0.0\n")
        log.write("-" * 80 + "\n")
        result = subprocess.run(
            ['git', 'push', 'origin', 'v1.0.0'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            log.write("✓ Tag pushed to origin\n")
            log.write(result.stdout + "\n")
        else:
            log.write(f"✗ Tag push failed: {result.stderr}\n")
        log.write("\n")
        
        # Verify
        log.write("[STEP 6] Verify Release\n")
        log.write("-" * 80 + "\n")
        result = subprocess.run(['git', 'log', '--oneline', '-5'], capture_output=True, text=True)
        log.write("Last 5 commits:\n")
        log.write(result.stdout + "\n")
        
        result = subprocess.run(['git', 'tag', '-l', 'v1*'], capture_output=True, text=True)
        log.write("Tags with v1:\n")
        log.write(result.stdout + "\n")
        
        log.write("\n" + "="*80 + "\n")
        log.write("✓ RELEASE PUSHED TO GITHUB\n")
        log.write("✓ GitHub Actions will run tests automatically\n")
        log.write("  Check: https://github.com/PacmanForever/meteocat_community_edition/actions\n")
        log.write("="*80 + "\n")
        
    except Exception as e:
        log.write(f"\n✗ ERROR: {str(e)}\n")
        import traceback
        log.write(traceback.format_exc())
    
    log.write(f"\nCompleted: {datetime.now().isoformat()}\n")

print("✓ Release push complete. See github_release.log")
