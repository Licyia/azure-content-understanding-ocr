"""Analyze a document URL with Azure AI Content Understanding."""

from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.parse import urlparse

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalysisInput
from azure.core.exceptions import AzureError
from azure.identity import DefaultAzureCredential


def is_absolute_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract text and structured content from a document URL.")
    parser.add_argument("file_url", nargs="?", default=os.getenv("CONTENT_UNDERSTANDING_FILE_URL"), help="Publicly accessible document URL.")
    parser.add_argument("--analyzer", default=os.getenv("CONTENT_UNDERSTANDING_ANALYZER_ID", "prebuilt-read"), help="Existing analyzer ID.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    endpoint = os.getenv("CONTENT_UNDERSTANDING_ENDPOINT")
    if not endpoint:
        print("Error: set CONTENT_UNDERSTANDING_ENDPOINT to your resource endpoint.", file=sys.stderr)
        return 2
    if not is_absolute_url(args.file_url or ""):
        print("Error: provide an HTTP or HTTPS document URL.", file=sys.stderr)
        return 2

    client = ContentUnderstandingClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
        api_version="2026-06-01-preview",
    )
    try:
        print(f"Analyzing document with '{args.analyzer}'...")
        poller = client.begin_analyze(analyzer_id=args.analyzer, inputs=[AnalysisInput(url=args.file_url)])
        result = poller.result()
        print(json.dumps(result.as_dict(), indent=2, ensure_ascii=False))
        return 0
    except AzureError as exc:
        print(f"Azure Content Understanding error: {exc}", file=sys.stderr)
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
