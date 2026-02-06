import requests

IPINFO_URL = "https://ipinfo.io/{ip}/json"
TIMEOUT = 5

def lookup(ip: str):
    """
    Returns geo info for an IP.
    Never raises exception (safe).
    """
    try:
        r = requests.get(IPINFO_URL.format(ip=ip), timeout=TIMEOUT)
        if r.status_code != 200:
            return None

        data = r.json()
        org = data.get("org", "")

        return {
            "ip": ip,
            "country": data.get("country"),
            "org": org,
            "asn": org.split()[0] if org.startswith("AS") else None,
            "is_cdn": is_cdn(org)
        }

    except Exception:
        return None


def is_cdn(org: str) -> bool:
    cdn_keywords = [
        "cloudflare",
        "akamai",
        "fastly",
        "google",
        "amazon",
        "cdn"
    ]
    org = org.lower()
    return any(k in org for k in cdn_keywords)
