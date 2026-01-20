
import sys
import os
from pathlib import Path
import urllib.request
import urllib.error
import socket

# Add parent dir to path
sys.path.append(str(Path(__file__).parent.parent))

from modules import apps

def check_url(url):
    try:
        req = urllib.request.Request(
            url, 
            method='HEAD',
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                'Accept': '*/*'
            }
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            return True, response.status
    except urllib.error.HTTPError as e:
        # Some servers don't like HEAD, try GET with range
        if e.code == 405 or e.code == 403: 
            try:
                req = urllib.request.Request(
                    url, 
                    headers={
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                        'Range': 'bytes=0-10'
                    }
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    return True, response.status
            except urllib.error.HTTPError as e2:
                return False, e2.code
            except Exception as e2:
                return False, str(e2)
        return False, e.code
    except Exception as e:
        return False, str(e)

def main():
    print("Verifying App URLs...")
    failed = []
    
    for app_key, app_info in apps.SUPPORTED_APPS.items():
        url = app_info.get("url")
        if not url:
            print(f"[SKIP] {app_key}: No URL")
            continue
            
        print(f"Checking {app_key}...", end=" ", flush=True)
        success, status = check_url(url)
        
        if success:
            print(f"[OK] {status}")
        else:
            print(f"[FAIL] {status} - {url}")
            failed.append((app_key, url, status))
            
    if failed:
        print("\n--- Failed URLs ---")
        for app, url, status in failed:
            print(f"{app}: {status}")
        sys.exit(1)
    else:
        print("\nAll URLs valid!")

if __name__ == "__main__":
    main()
