import urllib.request
import json
import ssl

def test_mirror(base_url, reel_url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    payload = {
        "url": reel_url
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    url = base_url.rstrip('/') + "/"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
            res_data = response.read().decode("utf-8")
            res_json = json.loads(res_data)
            print(f"[SUCCESS] {url} -> Status: {response.status}")
            print(f"Response: {res_json}\n")
            return url, res_json
    except Exception as e:
        err_msg = ""
        if hasattr(e, 'read'):
            err_msg = e.read().decode("utf-8", errors="ignore")
        else:
            err_msg = str(e)
        print(f"[FAILED] {url} -> {err_msg[:120]}")
    return None

def main():
    reel_url = "https://www.instagram.com/reel/DWv6ayADXds/"
    
    mirrors = [
        "https://nachos.imput.net",
        "https://blossom.imput.net",
        "https://kityune.imput.net",
        "https://sunny.imput.net",
        "https://api.qwkuns.me",
        "https://cobaltapi.cjs.nz",
        "https://api.dl.woof.monster",
        "https://cobaltapi.squair.xyz",
    ]
    
    successful = []
    for mirror in mirrors:
        res = test_mirror(mirror, reel_url)
        if res:
            successful.append((mirror, res))
            
    print("\n=== Summary of Working Mirrors ===")
    for url, res in successful:
        print(f"- {url} (status: {res[1].get('status') if isinstance(res, tuple) else res.get('status')})")

if __name__ == "__main__":
    main()
