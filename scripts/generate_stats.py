#!/usr/bin/env python3
"""Generate the profile README stat cards as static SVGs.

Replaces github-readme-stats.vercel.app, whose shared instance regularly
answers 503 and leaves broken images on the profile. Everything here is
computed from the public GitHub API and rendered to assets/*.svg, so the
README serves images straight from the repository.

Runs in CI on a schedule (.github/workflows/stats.yml) with the automatic
GITHUB_TOKEN — only public data is queried. Locally:

    GH_TOKEN=$(gh auth token) python3 scripts/generate_stats.py
"""

import json
import os
import pathlib
import urllib.request

USER = "igorkhaylov"
OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "assets"
API = "https://api.github.com"
TOP_LANGS = 8

# GitHub linguist colors for the languages that actually appear on the account;
# anything unknown falls back to a neutral gray.
LANG_COLORS = {
    "Python": "#3572A5",
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "Shell": "#89e051",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "SCSS": "#c6538c",
    "Vue": "#41b883",
    "Dockerfile": "#384d54",
    "Makefile": "#427819",
    "PHP": "#4F5D95",
}
FALLBACK_COLOR = "#8b949e"

THEMES = {
    "light": {"title": "#24292f", "text": "#57606a", "value": "#24292f", "track": "#eaeef2"},
    "dark": {"title": "#e6edf3", "text": "#8b949e", "value": "#e6edf3", "track": "#21262d"},
}


def api(path: str, payload: dict | None = None) -> dict | list:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(f"{API}{path}", data=data)
    request.add_header("Accept", "application/vnd.github+json")
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def public_contributions_last_year() -> int:
    """Public contributions over the last year, identical for any token.

    totalContributions includes private contributions when the calling token
    may see them (e.g. the owner's own PAT), so the restricted share is
    subtracted explicitly — otherwise local runs and CI would disagree.
    """
    query = f"""
    {{ user(login: "{USER}") {{ contributionsCollection {{
        contributionCalendar {{ totalContributions }}
        restrictedContributionsCount
    }} }} }}"""
    collection = api("/graphql", {"query": query})["data"]["user"]["contributionsCollection"]
    total = collection["contributionCalendar"]["totalContributions"]
    return total - collection["restrictedContributionsCount"]


def collect() -> tuple[list[tuple[str, str]], list[tuple[str, float]]]:
    """Return ([(stat label, value)], [(language, share percent)])."""
    repos: list[dict] = []
    page = 1
    while True:
        batch = api(f"/users/{USER}/repos?per_page=100&type=owner&page={page}")
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    own = [r for r in repos if not r["fork"]]

    profile = api(f"/users/{USER}")

    # Deliberately NOT the search API: its results depend on what the calling
    # token can see (the Actions GITHUB_TOKEN is scoped to this repository and
    # returns a fraction of what a personal token does). Counting per public
    # repo keeps the numbers identical no matter which token runs the script.
    commits = 0
    for repo in own:
        for contributor in api(f"/repos/{USER}/{repo['name']}/contributors?per_page=100"):
            if contributor["login"] == USER:
                commits += contributor["contributions"]
                break

    stats = [
        ("Public repos", str(len(own))),
        ("Total stars", str(sum(r["stargazers_count"] for r in own))),
        ("Commits (public repos)", f"{commits:,}"),
        ("Contributions (year)", f"{public_contributions_last_year():,}"),
        ("Followers", str(profile["followers"])),
    ]

    bytes_per_lang: dict[str, int] = {}
    for repo in own:
        for lang, size in api(f"/repos/{USER}/{repo['name']}/languages").items():
            bytes_per_lang[lang] = bytes_per_lang.get(lang, 0) + size
    total = sum(bytes_per_lang.values()) or 1
    top = sorted(bytes_per_lang.items(), key=lambda item: item[1], reverse=True)[:TOP_LANGS]
    langs = [(name, size * 100.0 / total) for name, size in top]
    return stats, langs


def render_stats(stats: list[tuple[str, str]], theme: dict) -> str:
    width, row_height, top = 320, 26, 46
    height = top + row_height * len(stats) + 6
    rows = []
    for index, (label, value) in enumerate(stats):
        y = top + row_height * index
        rows.append(
            f'<text x="0" y="{y}" font-size="14" fill="{theme["text"]}">{label}</text>'
            f'<text x="{width}" y="{y}" font-size="14" font-weight="600" '
            f'fill="{theme["value"]}" text-anchor="end">{value}</text>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="-apple-system,BlinkMacSystemFont,'
        f'Segoe UI,Helvetica,Arial,sans-serif">'
        f'<text x="0" y="18" font-size="16" font-weight="700" fill="{theme["title"]}">'
        f"GitHub stats</text>{''.join(rows)}</svg>"
    )


def render_langs(langs: list[tuple[str, float]], theme: dict) -> str:
    width, bar_y, bar_height = 320, 34, 10
    legend_top, legend_row, column_width = 66, 22, 160
    rows = (len(langs) + 1) // 2
    height = legend_top + legend_row * rows

    # Stacked percentage bar; widths are proportional to each language share.
    x = 0.0
    segments = []
    for name, share in langs:
        segment = width * share / 100.0
        color = LANG_COLORS.get(name, FALLBACK_COLOR)
        segments.append(
            f'<rect x="{x:.1f}" y="{bar_y}" width="{max(segment - 1, 1):.1f}" '
            f'height="{bar_height}" rx="2" fill="{color}"/>'
        )
        x += segment

    legend = []
    for index, (name, share) in enumerate(langs):
        lx = (index % 2) * column_width
        ly = legend_top + (index // 2) * legend_row
        color = LANG_COLORS.get(name, FALLBACK_COLOR)
        legend.append(
            f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{color}"/>'
            f'<text x="{lx + 16}" y="{ly}" font-size="13" fill="{theme["text"]}">'
            f'{name} <tspan fill="{theme["value"]}" font-weight="600">{share:.1f}%</tspan></text>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="-apple-system,BlinkMacSystemFont,'
        f'Segoe UI,Helvetica,Arial,sans-serif">'
        f'<text x="0" y="18" font-size="16" font-weight="700" fill="{theme["title"]}">'
        f'Top languages</text>'
        f'<rect x="0" y="{bar_y}" width="{width}" height="{bar_height}" rx="2" '
        f'fill="{theme["track"]}"/>{"".join(segments)}{"".join(legend)}</svg>'
    )


def main() -> None:
    stats, langs = collect()
    OUT_DIR.mkdir(exist_ok=True)
    for theme_name, theme in THEMES.items():
        (OUT_DIR / f"stats-{theme_name}.svg").write_text(render_stats(stats, theme) + "\n")
        (OUT_DIR / f"langs-{theme_name}.svg").write_text(render_langs(langs, theme) + "\n")
    print(f"stats: {stats}")
    print(f"langs: {[(name, round(share, 1)) for name, share in langs]}")
    print(f"wrote 4 svg files to {OUT_DIR}")


if __name__ == "__main__":
    main()
