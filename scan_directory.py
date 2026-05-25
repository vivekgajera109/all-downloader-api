import urllib.request
import re
import ssl
import json

def scan_cobalt_directory():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    base_url = "https://cobalt.directory"
    
    # Try common endpoints
    endpoints = [
        "/api/instances",
        "/api/servers",
        "/api/nodes",
        "/api/list",
        "/instances.json",
        "/api/data"
    ]

    for ep in endpoints:
        url = base_url + ep
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        try:
            with urllib.request.urlopen(req, context=ctx) as response:
                print(f"Endpoint {ep} Succeeded! Status: {response.status}")
                body = response.read().decode("utf-8")
                print("Length:", len(body))
                # print snippet
                print(body[:200])
        except Exception as e:
            print(f"Endpoint {ep} Failed: {e}")

    # Now parse the main HTML to find Svelte chunks
    req = urllib.request.Request(base_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            html = response.read().decode("utf-8")
            # Find script tags with src
            scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
            print("Found JS files:")
            for s in scripts:
                print("  ", s)
                # fetch JS file and search for URLs or api paths
                js_url = s if s.startswith("http") else base_url + s
                try:
                    js_req = urllib.request.Request(js_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(js_req, context=ctx) as js_res:
                        js_code = js_res.read().decode("utf-8")
                        # Find occurrences of http/https or paths
                        urls = re.findall(r'https?://[^\s"\'`(){}]+', js_code)
                        print(f"    Found {len(urls)} URLs in JS")
                        # print some distinct URLs
                        distinct = set(urls)
                        for d in sorted(distinct):
                            if "cobalt" in d or "wuk" in d or "directory" in d or "api" in d:
                                print(f"      Possible API/Instance: {d}")
                except Exception as ex:
                    print(f"    Failed to read JS: {ex}")
    except Exception as e:
        print("Failed to fetch homepage:", e)

if __name__ == "__main__":
    scan_cobalt_directory()
