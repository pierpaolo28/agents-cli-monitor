#!/usr/bin/env python3
"""
Full monitoring sweep that tracks BOTH third-party and first-party content.

This script runs two separate sweeps:
1. Third-party community content (Medium, InfoQ, Reddit, YouTube, etc.)
2. First-party Google content (developers.googleblog.com, docs.cloud.google.com, adk.dev)

Results are saved to separate tracking files:
- data/agents_cli_mentions.md (third-party)
- data/agents_cli_mentions_first_party.md (first-party)
"""

import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tools.batch_search import batch_search_agents_cli
from app.tools.batch_search_first_party import batch_search_first_party
from app.tools.search import detect_agents_cli_patterns
from app.tools.search_first_party import detect_agents_cli_first_party
from app.tools.tracking import read_tracking_file, write_tracking_file

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_third_party_sweep(tracking_file: str) -> dict:
    """Run third-party content sweep."""
    logger.info("=" * 70)
    logger.info("THIRD-PARTY CONTENT SWEEP")
    logger.info("=" * 70)
    logger.info(f"Tracking file: {tracking_file}")
    logger.info("")

    # Step 1: Read existing tracking file
    logger.info("Step 1: Reading tracking file...")
    tracking_data = json.loads(read_tracking_file(tracking_file))
    current_count = len(tracking_data.get("urls", []))
    logger.info(f"  Current entries: {current_count}")
    logger.info("")

    # Step 2: Run batch search
    logger.info("Step 2: Running batch search (41 queries)...")
    search_result = json.loads(batch_search_agents_cli())
    urls_found = search_result.get("total_urls_found", 0)
    logger.info(f"  Found {urls_found} URLs")
    logger.info("")

    # Step 3: Validate URLs
    logger.info("Step 3: Validating URLs...")
    valid_urls = []
    for url_data in search_result.get("unique_urls", []):
        title = url_data.get("title", "")
        url = url_data.get("url", "")

        validation_result = json.loads(detect_agents_cli_patterns(title, url))
        if validation_result.get("confidence", 0) >= 0.3:
            valid_urls.append({
                "title": title,
                "url": url
            })

    logger.info(f"  Valid URLs (confidence >= 0.3): {len(valid_urls)}/{urls_found}")
    logger.info("")

    # Step 4: Save results
    logger.info("Step 4: Saving results...")
    write_result = json.loads(write_tracking_file(tracking_file, json.dumps(valid_urls)))

    logger.info(f"  Added: {write_result.get('new_entries', 0)}")
    logger.info(f"  Duplicates: {write_result.get('duplicates', 0)}")
    logger.info(f"  Total: {write_result.get('total_entries', 0)}")
    logger.info("")

    return {
        "success": True,
        "urls_found": urls_found,
        "urls_validated": len(valid_urls),
        "urls_added": write_result.get('new_entries', 0),
        "urls_skipped": write_result.get('duplicates', 0),
        "total_tracked": write_result.get('total_entries', 0)
    }


def run_first_party_sweep(tracking_file: str) -> dict:
    """Run first-party Google content sweep."""
    logger.info("=" * 70)
    logger.info("FIRST-PARTY GOOGLE CONTENT SWEEP")
    logger.info("=" * 70)
    logger.info(f"Tracking file: {tracking_file}")
    logger.info("")

    # Step 1: Read existing tracking file
    logger.info("Step 1: Reading tracking file...")
    tracking_data = json.loads(read_tracking_file(tracking_file))
    current_count = len(tracking_data.get("urls", []))
    logger.info(f"  Current entries: {current_count}")
    logger.info("")

    # Step 2: Run batch search
    logger.info("Step 2: Running first-party batch search (12 queries)...")
    search_result = json.loads(batch_search_first_party())
    urls_found = search_result.get("total_urls_found", 0)
    logger.info(f"  Found {urls_found} URLs")
    logger.info("")

    # Step 3: Validate URLs
    logger.info("Step 3: Validating URLs...")
    valid_urls = []
    for url_data in search_result.get("unique_urls", []):
        title = url_data.get("title", "")
        url = url_data.get("url", "")

        validation_result = json.loads(detect_agents_cli_first_party(title, url))
        if validation_result.get("confidence", 0) >= 0.3:
            valid_urls.append({
                "title": title,
                "url": url
            })

    logger.info(f"  Valid URLs (confidence >= 0.3): {len(valid_urls)}/{urls_found}")
    logger.info("")

    # Step 4: Save results
    logger.info("Step 4: Saving results...")
    write_result = json.loads(write_tracking_file(tracking_file, json.dumps(valid_urls)))

    logger.info(f"  Added: {write_result.get('new_entries', 0)}")
    logger.info(f"  Duplicates: {write_result.get('duplicates', 0)}")
    logger.info(f"  Total: {write_result.get('total_entries', 0)}")
    logger.info("")

    return {
        "success": True,
        "urls_found": urls_found,
        "urls_validated": len(valid_urls),
        "urls_added": write_result.get('new_entries', 0),
        "urls_skipped": write_result.get('duplicates', 0),
        "total_tracked": write_result.get('total_entries', 0)
    }


def main():
    """Run full monitoring sweep."""
    # Tracking files
    third_party_file = os.getenv("TRACKING_FILE_PATH", "data/agents_cli_mentions.md")
    first_party_file = os.getenv("TRACKING_FILE_PATH_FIRST_PARTY", "data/agents_cli_mentions_first_party.md")

    try:
        # Run third-party sweep
        third_party_result = run_third_party_sweep(third_party_file)

        # Run first-party sweep
        first_party_result = run_first_party_sweep(first_party_file)

        # Summary
        logger.info("=" * 70)
        logger.info("FULL SWEEP COMPLETE")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Third-Party Content:")
        logger.info(f"  URLs tracked: {third_party_result['total_tracked']}")
        logger.info(f"  New URLs added: {third_party_result['urls_added']}")
        logger.info("")
        logger.info("First-Party Google Content:")
        logger.info(f"  URLs tracked: {first_party_result['total_tracked']}")
        logger.info(f"  New URLs added: {first_party_result['urls_added']}")
        logger.info("")

        return {
            "success": True,
            "third_party": third_party_result,
            "first_party": first_party_result
        }

    except Exception as e:
        logger.error(f"Sweep failed: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))
