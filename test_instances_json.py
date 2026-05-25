import urllib.request
import json
import ssl

def fetch_instances_json():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = "https://instances.cobalt.best/api/instances.json"
    print(f"Requesting instances from: {url}")
    
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode("utf-8"))
            print("Successfully fetched instances list!")
            print(f"Total instances returned: {len(data)}")
            # print the first 10 instances
            for i, inst in enumerate(data[:10]):
                print(f"{i+1}: Name: {inst.get('name')}, API: {inst.get('api')}, Front: {inst.get('frontend')}")
    except Exception as e:
        print("Failed to fetch instances list:")
        print(e)

if __name__ == "__main__":
    fetch_instances_json()
