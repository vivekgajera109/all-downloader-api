import urllib.request
import json
import ssl
import time

def test_mirror(base_url, reel_url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    payload = {
        "url": reel_url,    
        "videoQuality": "1080"
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # Some older instances use /api/json, others use /
    endpoints = ["/", "/api/json"]
    for ep in endpoints:
        url = base_url.rstrip('/') + ep
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        try:
            # Short timeout to skip offline ones quickly
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
        "https://api.cobalt.tools",
        "https://co.wuk.sh",
        "https://api.co.wuk.sh",
        "https://cobalt.syntx.tech",
        "https://cobalt.moe",
        "https://cobalt.q19.me",
        "https://cobalt.api.ryo-koshikawa.com",
        "https://cobalt.hyperdefined.xyz",
        "https://cobalt.wuk.sh",
        "https://api.cobalt.best",
        "https://cobalt.best",
        "https://api.cobalt.directory",
    ]
    
    successful = []
    for mirror in mirrors:
        res = test_mirror(mirror, reel_url)
        if res:
            successful.append(res)
            
    print("\n=== Summary of Working Mirrors ===")
    for url, res in successful:
        print(f"- {url} (status: {res.get('status')})")

if __name__ == "__main__":
    main()
