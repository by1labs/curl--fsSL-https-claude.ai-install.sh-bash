"""CLI entry point for AI Search Analyzer."""

import argparse
import sys

from .fetcher import fetch_page
from .analyzers import run_all_analyzers
from .report import generate_report, report_to_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ai-search-analyzer",
        description="Analyze how visible a website is to AI search engines and LLMs.",
    )
    parser.add_argument(
        "url",
        help="URL of the website to analyze (e.g. https://example.com)",
    )
    parser.add_argument(
        "-o", "--output",
        help="Write JSON report to file instead of stdout",
        metavar="FILE",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print JSON output (default: true)",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Output compact JSON (no indentation)",
    )

    args = parser.parse_args(argv)
    url = args.url

    # Normalize URL
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Fetch
    print(f"Fetching {url} ...", file=sys.stderr)
    page_data = fetch_page(url)

    if not page_data["ok"]:
        print(f"Error: {page_data.get('error', 'Unknown error')}", file=sys.stderr)
        return 1

    print("Analyzing...", file=sys.stderr)

    # Analyze
    results = run_all_analyzers(page_data)

    # Report
    report = generate_report(url, page_data, results)
    indent = None if args.compact else 2
    json_output = report_to_json(report, indent=indent) if indent else report_to_json(report, indent=0)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_output)
            f.write("\n")
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(json_output)

    # Print summary to stderr
    overall = report["overall"]
    print(
        f"\nOverall AI Search Visibility: {overall['grade']} "
        f"({overall['percentage']}% — {overall['score']}/{overall['max_score']})",
        file=sys.stderr,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
