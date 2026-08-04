import urllib.request
import re

FRONTEND_URL = "http://localhost:5173"

def test_frontend_server():
    print("=" * 60)
    print("🏥 PRASHANTH HOSPITALS — FRONTEND VITE WEB APP TEST")
    print("=" * 60)

    try:
        req = urllib.request.Request(FRONTEND_URL)
        with urllib.request.urlopen(req) as response:
            status = response.status
            html = response.read().decode("utf-8")
            
            print(f"✅ [{status}] GET {FRONTEND_URL} - Main Index Page")
            
            # Check Title
            if "<title>" in html:
                title_match = re.search(r"<title>(.*?)</title>", html)
                title = title_match.group(1) if title_match else "N/A"
                print(f"   📄 Page Title: '{title}'")
            
            # Check Entry Script
            if 'src="/src/main.jsx"' in html or 'src="/@vite/client"' in html:
                print("   ⚡ Vite Module Entry Script Detected: /src/main.jsx")
            
            # Extract linked scripts/css
            scripts = re.findall(r'<script [^>]*src="([^"]+)"', html)
            print(f"   📦 Total Script Tags: {len(scripts)}")
            for s in scripts[:3]:
                print(f"      - {s}")
                
            return True
    except Exception as e:
        print(f"❌ GET {FRONTEND_URL} failed: {e}")
        return False

if __name__ == "__main__":
    test_frontend_server()
