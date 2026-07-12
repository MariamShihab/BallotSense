"""Check whether November 2026 official voter-guide sources are ready.

This monitor is intentionally metadata-only. It fetches official public pages
and prints whether the release-candidate source package appears ready for
snapshotting. It does not download, hash, ingest, embed, or store source
documents.
"""

from __future__ import annotations

import ssl
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    import certifi
except ImportError:  # pragma: no cover - certifi is expected in local dev env.
    certifi = None

USER_AGENT = "BallotSenseSourceMonitor/0.1 (+https://github.com/MariamShihab/BallotSense)"
VOTER_GUIDE_URL = "https://voterguide.sos.ca.gov/"
QUALIFIED_MEASURES_URL = (
    "https://www.sos.ca.gov/elections/ballot-measures/qualified-ballot-measures"
)


@dataclass(frozen=True)
class SourceCheck:
    name: str
    url: str
    ok: bool
    finding: str


class VisibleTextParser(HTMLParser):
    """Small stdlib HTML text extractor for source-readiness checks."""

    def __init__(self) -> None:
        super().__init__()
        self._hidden_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._hidden_depth:
            self._hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._hidden_depth:
            return
        cleaned = " ".join(data.split())
        if cleaned:
            self.parts.append(cleaned)

    @property
    def text(self) -> str:
        return "\n".join(self.parts)


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    context = (
        ssl.create_default_context(cafile=certifi.where())
        if certifi is not None
        else ssl.create_default_context()
    )
    with urlopen(  # noqa: S310 - official HTTPS sources only; TLS verification stays enabled.
        request,
        context=context,
        timeout=20,
    ) as response:
        body = response.read().decode("utf-8", errors="replace")
    parser = VisibleTextParser()
    parser.feed(body)
    return parser.text


def check_voter_guide_page() -> SourceCheck:
    text = fetch_text(VOTER_GUIDE_URL)
    lowered = text.lower()
    has_election = "november 3, 2026" in lowered
    says_future = "will be available in september 2026" in lowered
    if has_election and says_future:
        return SourceCheck(
            name="Official Voter Information Guide",
            url=VOTER_GUIDE_URL,
            ok=False,
            finding=(
                "Official page exists, but says the November 3, 2026 guide "
                "will be available in September 2026."
            ),
        )
    if has_election and "proposition 1" in lowered and "proposition 45" in lowered:
        return SourceCheck(
            name="Official Voter Information Guide",
            url=VOTER_GUIDE_URL,
            ok=True,
            finding="Possible voter-guide content found for Proposition 1 and Proposition 45.",
        )
    return SourceCheck(
        name="Official Voter Information Guide",
        url=VOTER_GUIDE_URL,
        ok=False,
        finding="Page is reachable, but release-candidate voter-guide content was not detected.",
    )


def check_qualified_measures_page() -> SourceCheck:
    text = fetch_text(QUALIFIED_MEASURES_URL)
    lowered = text.lower()
    has_targets = "proposition 1" in lowered and "proposition 45" in lowered
    has_prop_1_text = "veterans and affordable housing bond act of 2026" in lowered
    has_prop_45_text = "modifies environmental review for certain projects" in lowered
    return SourceCheck(
        name="Qualified Statewide Ballot Measures",
        url=QUALIFIED_MEASURES_URL,
        ok=has_targets and has_prop_1_text and has_prop_45_text,
        finding=(
            "Qualified list includes Proposition 1 and Proposition 45."
            if has_targets and has_prop_1_text and has_prop_45_text
            else (
                "Qualified list was reachable, but expected Proposition 1/45 "
                "text was not detected."
            )
        ),
    )


def main() -> int:
    checks: list[SourceCheck] = []
    check_names = {
        check_voter_guide_page: "Official Voter Information Guide",
        check_qualified_measures_page: "Qualified Statewide Ballot Measures",
    }
    check_urls = {
        check_voter_guide_page: VOTER_GUIDE_URL,
        check_qualified_measures_page: QUALIFIED_MEASURES_URL,
    }
    for check in (check_voter_guide_page, check_qualified_measures_page):
        try:
            checks.append(check())
        except (HTTPError, URLError, TimeoutError) as exc:
            checks.append(
                SourceCheck(
                    name=check_names[check],
                    url=check_urls[check],
                    ok=False,
                    finding=f"Could not fetch official page: {exc}",
                )
            )

    print("November 3, 2026 source readiness")
    print("=" * 41)
    for result in checks:
        icon = "✓" if result.ok else "!"
        print(f"{icon} {result.name}")
        print(f"  URL: {result.url or 'see finding'}")
        print(f"  Finding: {result.finding}")

    guide_ready = any(
        result.ok for result in checks if result.name == "Official Voter Information Guide"
    )
    if guide_ready:
        print("\nStatus: possible release-candidate voter-guide package detected.")
        print("Next: human reviewer should inspect official guide pages before snapshotting.")
    else:
        print("\nStatus: monitor only; not ready for snapshotting or ingestion.")
        print("Next: rerun this check after the SOS voter guide is published.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
