import urllib.request
import ssl

def write_html():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = "https://cobalt.directory/"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            html = response.read().decode("utf-8")
            with open("cobalt_dir.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Wrote html to cobalt_dir.html")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    write_html()
