import urllib.request
import json
import ssl

def test_cobalt():
    # Ignore SSL verification issues just in case
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = "https://api.cobalt.tools/"
    payload = {
        "url": "https://www.instagram.com/reel/DWv6ayADXds/"
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        print(f"Requesting {url} for Instagram reel...")
        with urllib.request.urlopen(req, context=ctx) as response:
            res_data = response.read().decode("utf-8")
            print("Response status code:", response.status)
            print("Response body:")
            print(res_data)
    except Exception as e:
        print("Error encountered:")
        if hasattr(e, 'read'):
            print(e.read().decode("utf-8"))
        else:
            print(str(e))

if __name__ == "__main__":
    test_cobalt()
