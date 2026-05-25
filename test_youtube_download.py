import urllib.request
import json
import ssl

def test_mirror(base_url, target_url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    payload = {
        "url": target_url
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
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
            return True
    except Exception as e:
        err_msg = ""
        if hasattr(e, 'read'):
            err_msg = e.read().decode("utf-8", errors="ignore")
        else:
            err_msg = str(e)
        print(f"[FAILED] {url} -> {err_msg[:120]}")
    return False

def main():
    target_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    mirrors = [
        "https://cobaltapi.cjs.nz",
        "https://api.dl.woof.monster",
        "https://cobaltapi.squair.xyz",
    ]
    for mirror in mirrors:
        test_mirror(mirror, target_url)

if __name__ == "__main__":
    main()
