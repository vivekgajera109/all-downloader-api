import urllib.request
import re
import ssl

def fetch_instances():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    urls = [
        "https://instances.cobalt.best/",
        "https://cobalt.directory/"
    ]

    for url in urls:
        print(f"--- Fetching {url} ---")
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        try:
            with urllib.request.urlopen(req, context=ctx) as response:
                html = response.read().decode("utf-8")
                print("HTML Length:", len(html))
                # Print some snippets or find links
                links = re.findall(r'https?://[^\s"\'<>]+', html)
                # Filter links that might be cobalt instances
                cobalt_links = set()
                for link in links:
                    if "cobalt" in link or "co.wuk.sh" in link or "kuko" in link:
                        cobalt_links.add(link)
                print("Found matching links:")
                for cl in sorted(cobalt_links):
                    print("  ", cl)
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    fetch_instances()
