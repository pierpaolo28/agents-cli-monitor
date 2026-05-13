"""Tools for tracking and managing the Agents CLI mentions markdown file."""

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

import gcsfs


def _is_gcs_path(path: str) -> bool:
    """Check if path is a GCS path (starts with gs://)."""
    return path.startswith("gs://")


def _read_file(path: str) -> str:
    """Read file from GCS or local filesystem."""
    if _is_gcs_path(path):
        fs = gcsfs.GCSFileSystem()
        with fs.open(path, "r") as f:
            return f.read()
    else:
        return Path(path).read_text()


def _write_file(path: str, content: str) -> None:
    """Write file to GCS or local filesystem."""
    if _is_gcs_path(path):
        fs = gcsfs.GCSFileSystem()
        with fs.open(path, "w") as f:
            f.write(content)
    else:
        local_path = Path(path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_text(content)


def _file_exists(path: str) -> bool:
    """Check if file exists in GCS or local filesystem."""
    if _is_gcs_path(path):
        fs = gcsfs.GCSFileSystem()
        return fs.exists(path)
    else:
        return Path(path).exists()


def _generate_url_hash(url: str) -> str:
    """Generate a short hash of a URL for deduplication."""
    return hashlib.md5(url.encode()).hexdigest()[:8]


def _parse_tracking_file(content: str) -> dict[str, list[dict[str, str]]]:
    """
    Parse the tracking markdown file into a structured format.

    Returns a dict mapping dates to lists of entries.
    """
    entries_by_date = {}
    current_date = None

    lines = content.split("\n")
    for line in lines:
        # Check for date headers (## YYYY-MM-DD)
        date_match = re.match(r"^##\s+(\d{4}-\d{2}-\d{2})", line)
        if date_match:
            current_date = date_match.group(1)
            if current_date not in entries_by_date:
                entries_by_date[current_date] = []
            continue

        # Check for entry lines (- [Title](URL))
        entry_match = re.match(r"^-\s+\[([^\]]+)\]\(([^\)]+)\)", line)
        if entry_match and current_date:
            title = entry_match.group(1)
            url = entry_match.group(2)
            entries_by_date[current_date].append({
                "title": title,
                "url": url,
                "url_hash": _generate_url_hash(url),
            })

    return entries_by_date


def _get_all_tracked_urls(entries_by_date: dict) -> set[str]:
    """Extract all URLs that are already tracked."""
    all_urls = set()
    for entries in entries_by_date.values():
        for entry in entries:
            all_urls.add(entry["url"])
            all_urls.add(entry["url_hash"])
    return all_urls


def read_tracking_file(file_path: str = "data/agents_cli_mentions.md") -> str:
    """
    Read the Agents CLI mentions tracking file from GCS or local filesystem.

    Supports both local paths and GCS paths (gs://bucket/path/to/file.md).

    Args:
        file_path: Path to the tracking markdown file (local or gs://)

    Returns:
        JSON string containing:
        - content: Raw markdown content
        - total_entries: Total number of tracked URLs
        - tracked_url_count: Number of unique URLs
        - file_path: The path that was read (for reference)
    """
    if not _file_exists(file_path):
        result = {
            "content": "# Agents CLI Mentions Tracker\n\nThis file tracks mentions of Google Agents CLI across the web.\n\n",
            "total_entries": 0,
            "tracked_url_count": 0,
            "file_path": file_path,
        }
        return json.dumps(result)

    content = _read_file(file_path)
    entries_by_date = _parse_tracking_file(content)
    tracked_urls = _get_all_tracked_urls(entries_by_date)

    total_entries = sum(len(entries) for entries in entries_by_date.values())

    result = {
        "content": content,
        "total_entries": total_entries,
        "tracked_url_count": len(tracked_urls),
        "file_path": file_path,
    }

    return json.dumps(result)


def write_tracking_file(
    file_path: str,
    new_entries_json: str,
    date: str = "",
) -> str:
    """
    Append new entries to the tracking file (GCS or local).

    This tool:
    1. Reads the existing file from GCS or local filesystem
    2. Filters out duplicate URLs
    3. Adds new entries under today's date (or specified date)
    4. Writes the updated content back to GCS or local filesystem

    Args:
        file_path: Path to the tracking markdown file (local or gs://)
        new_entries_json: JSON string list of dictionaries with 'title' and 'url' keys
        date: Optional date string (YYYY-MM-DD). Defaults to today.

    Returns:
        JSON string containing:
        - added_count: Number of new entries added
        - skipped_count: Number of duplicates skipped
        - total_entries: Total entries in file after update
        - file_path: The path that was written to
    """
    # Parse input
    try:
        new_entries = json.loads(new_entries_json) if new_entries_json else []
    except json.JSONDecodeError as e:
        return json.dumps({
            "error": "Invalid JSON format",
            "message": str(e),
            "received_data": new_entries_json[:500] if new_entries_json else "",
            "hint": "new_entries_json must be a valid JSON array of objects with 'title' and 'url' keys",
            "added_count": 0,
            "skipped_count": 0,
            "total_entries": 0,
            "file_path": file_path
        })

    # Read existing file
    tracking_json = read_tracking_file(file_path)
    tracking_data = json.loads(tracking_json)
    # Re-parse to get full data
    if _file_exists(file_path):
        content = _read_file(file_path)
        entries_by_date = _parse_tracking_file(content)
        tracked_urls = _get_all_tracked_urls(entries_by_date)
    else:
        entries_by_date = {}
        tracked_urls = set()

    # Use today's date if not specified
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    # Filter out duplicates
    new_unique_entries = []
    skipped_count = 0

    for entry in new_entries:
        url = entry["url"]
        url_hash = _generate_url_hash(url)

        if url not in tracked_urls and url_hash not in tracked_urls:
            new_unique_entries.append(entry)
            tracked_urls.add(url)
            tracked_urls.add(url_hash)
        else:
            skipped_count += 1

    # Add new entries to the date
    if new_unique_entries:
        if date not in entries_by_date:
            entries_by_date[date] = []
        entries_by_date[date].extend([
            {
                "title": e["title"],
                "url": e["url"],
                "url_hash": _generate_url_hash(e["url"]),
            }
            for e in new_unique_entries
        ])

    # Rebuild the markdown file
    lines = [
        "# Agents CLI Mentions Tracker",
        "",
        "This file tracks mentions of Google Agents CLI across news, blogs, social media, and repositories.",
        "",
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    # Sort dates in reverse chronological order
    sorted_dates = sorted(entries_by_date.keys(), reverse=True)

    for date_key in sorted_dates:
        lines.append(f"## {date_key}")
        lines.append("")

        for entry in entries_by_date[date_key]:
            lines.append(f"- [{entry['title']}]({entry['url']})")

        lines.append("")

    # Write to file (GCS or local)
    _write_file(file_path, "\n".join(lines))

    total_entries = sum(len(entries) for entries in entries_by_date.values())

    result = {
        "added_count": len(new_unique_entries),
        "skipped_count": skipped_count,
        "total_entries": total_entries,
        "file_path": file_path,
    }

    return json.dumps(result)


def check_for_duplicates(
    file_path: str,
    urls_json: str,
) -> str:
    """
    Check which URLs are already tracked (GCS or local).

    Args:
        file_path: Path to the tracking markdown file (local or gs://)
        urls_json: JSON string list of URLs (strings) or list of dicts with 'url' key

    Returns:
        JSON string containing:
        - new_urls: URLs not yet tracked
        - duplicate_urls: URLs already in the file
        - new_count: Count of new URLs
        - duplicate_count: Count of duplicate URLs
    """
    urls_data = json.loads(urls_json) if urls_json else []

    # Read existing tracking data
    if _file_exists(file_path):
        content = _read_file(file_path)
        entries_by_date = _parse_tracking_file(content)
        tracked_urls = _get_all_tracked_urls(entries_by_date)
    else:
        tracked_urls = set()

    new_urls = []
    duplicate_urls = []

    for item in urls_data:
        # Handle both string URLs and dict objects with "url" key
        if isinstance(item, dict):
            url = item.get("url", "")
        else:
            url = item

        if not url:
            continue

        url_hash = _generate_url_hash(url)
        if url in tracked_urls or url_hash in tracked_urls:
            duplicate_urls.append(url)
        else:
            new_urls.append(url)

    result = {
        "new_urls": new_urls,
        "duplicate_urls": duplicate_urls,
        "new_count": len(new_urls),
        "duplicate_count": len(duplicate_urls),
    }

    return json.dumps(result)
