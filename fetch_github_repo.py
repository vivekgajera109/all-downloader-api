import urllib.request
import json
import ssl

def fetch_github_instances():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = "https://api.github.com/repos/hyperdefined/cobalt.directory/contents/backend/instances"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
    
    try:
        print(f"Fetching GitHub API directory contents for: {url}")
        with urllib.request.urlopen(req, context=ctx) as response:
            res_body = response.read().decode("utf-8")
            contents = json.loads(res_body)
            print("Type of contents:", type(contents))
            if isinstance(contents, dict):
                print("Keys:", list(contents.keys()))
                print("Type field:", contents.get("type"))
                print("Name field:", contents.get("name"))
                if "entries" in contents:
                    print("Found 'entries' key")
                # Print the entire response safely
                print(json.dumps(contents, indent=2)[:1000])
            elif isinstance(contents, list):
                print(f"List of length {len(contents)}")
                print(contents[0])
    except Exception as e:
        print("GitHub API call failed:", e)

if __name__ == "__main__":
    fetch_github_instances()
