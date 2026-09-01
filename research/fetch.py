"""Robust fetch helper for the moyan SSE research (uses Python TLS stack).

Usage:
  python fetch.py <url> [--out <file>] [--raw] [--timeout 20]
    --raw     print body to stdout (truncated by caller)
    --json    print parsed JSON
"""
import json
import ssl
import sys
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 research-agent/1.0"


def fetch(url: str, timeout: int = 20, headers: dict | None = None) -> tuple[int, bytes, dict]:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers=headers or {"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.status, resp.read(), dict(resp.headers)


def main() -> None:
    args = sys.argv[1:]
    url = args[0]
    out = None
    as_json = False
    raw = False
    timeout = 25
    i = 1
    while i < len(args):
        a = args[i]
        if a == "--raw":
            raw = True
        elif a == "--json":
            as_json = True
        elif a == "--out":
            i += 1
            out = args[i]
        elif a.startswith("--out="):
            out = a.split("=", 1)[1]
        elif a == "--timeout":
            i += 1
            timeout = int(args[i])
        elif a.startswith("--timeout="):
            timeout = int(a.split("=", 1)[1])
        i += 1
    try:
        status, body, hdrs = fetch(url, timeout=timeout)
    except Exception as e:  # network-layer failures
        print(f"NETERR {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"STATUS {status} BYTES {len(body)} CT {hdrs.get('Content-Type', '')}", file=sys.stderr)
    if out:
        with open(out, "wb") as f:
            f.write(body)
        print(f"saved -> {out}", file=sys.stderr)
    if as_json:
        try:
            print(json.dumps(json.loads(body), ensure_ascii=False, indent=1))
        except Exception as e:
            print(f"JSONERR {e}", file=sys.stderr)
            if raw:
                sys.stdout.buffer.write(body)
    elif raw:
        sys.stdout.buffer.write(body)


if __name__ == "__main__":
    main()