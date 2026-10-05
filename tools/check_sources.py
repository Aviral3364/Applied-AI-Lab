#!/usr/bin/env python3
"""Check that official sources listed in a skill's source policy are still reachable.

Reachability only: a 200 response on the publisher's own host does NOT verify that
the page still supports the claims recorded in the policy. Failures mean a human
must re-check the source and refresh the policy's verification date.
Runs in CI only; the shipped skill never makes network calls.
"""
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

URL_RE = re.compile(r"\]\((https://[^)\s]+)\)")


def check(url, timeout=20):
    request = Request(url, method="GET", headers={"User-Agent": "applied-ai-lab-source-check"})
    with urlopen(request, timeout=timeout) as response:
        final_host = urlsplit(response.geturl()).hostname or ""
        return response.status, final_host


def main(paths):
    failures = 0
    for path in paths:
        for url in sorted(set(URL_RE.findall(Path(path).read_text(encoding="utf-8")))):
            host = urlsplit(url).hostname or ""
            try:
                status, final_host = check(url)
                same_site = final_host == host or final_host.endswith("." + host) or host.endswith("." + final_host)
                ok = status == 200 and same_site
                detail = f"{status} final_host={final_host}"
            except Exception as error:  # report every failure, keep checking the rest
                ok, detail = False, f"{type(error).__name__}: {error}"
            failures += not ok
            print(f"{'OK  ' if ok else 'FAIL'} {url} ({detail})")
    print(f"\n{failures} failing source(s). Reachability is not content verification.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["skills/production-ai-design-review/references/source-policy.md"]))
