#!/usr/bin/env python3
"""
Production monitoring sweep script.

This script runs the monitoring workflow directly without relying on ADK agent orchestration.
Designed to be triggered by Cloud Scheduler via Cloud Run or run locally.
"""

import json
import logging
import sys
from datetime import datetime

from app.tools.batch_search import batch_search_agents_cli
from app.tools.search import detect_agents_cli_patterns
from app.tools.tracking import read_tracking_file, write_tracking_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_monitoring_sweep(tracking_file_path: str = "data/agents_cli_mentions.md") -> dict:
    """
    Run a comprehensive monitoring sweep for Agents CLI mentions.

    Returns:
        dict with results summary
    """
    logger.info("=" * 70)
    logger.info("AGENTS CLI MONITORING SWEEP")
    logger.info("=" * 70)
    logger.info(f"Tracking file: {tracking_file_path}")
    logger.info("")

    # Step 1: Read existing tracking file
    logger.info("Step 1: Reading tracking file...")
    tracking_data = json.loads(read_tracking_file(tracking_file_path))
    logger.info(f"  Current entries: {tracking_data['total_entries']}")

    # Step 2: Run batch search
    logger.info("")
    logger.info("Step 2: Running batch search (33 queries)...")
    search_result = json.loads(batch_search_agents_cli())
    total_urls_found = search_result['total_urls_found']
    logger.info(f"  Found {total_urls_found} URLs")

    # Step 3: Validate URLs
    logger.info("")
    logger.info("Step 3: Validating URLs...")
    valid_urls = []
    for url_data in search_result['unique_urls']:
        title = url_data['title']
        url = url_data['url']

        validation_result = json.loads(detect_agents_cli_patterns(title, url))

        if validation_result['confidence'] >= 0.3:
            valid_urls.append({
                'title': title,
                'url': url
            })

    logger.info(f"  Valid URLs (confidence >= 0.3): {len(valid_urls)}/{total_urls_found}")

    # Step 4: Save results
    logger.info("")
    logger.info("Step 4: Saving results...")
    write_result = json.loads(write_tracking_file(
        tracking_file_path,
        json.dumps(valid_urls)
    ))

    logger.info(f"  Added: {write_result['added_count']}")
    logger.info(f"  Duplicates: {write_result['skipped_count']}")
    logger.info(f"  Total: {write_result['total_entries']}")

    # Summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("SWEEP COMPLETE")
    logger.info("=" * 70)
    logger.info(f"✅ Monitoring run successful at {datetime.now().isoformat()}")
    logger.info("")

    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "urls_found": total_urls_found,
        "urls_validated": len(valid_urls),
        "urls_added": write_result['added_count'],
        "urls_skipped": write_result['skipped_count'],
        "total_tracked": write_result['total_entries'],
    }


if __name__ == "__main__":
    import os

    tracking_file = os.getenv("TRACKING_FILE_PATH", "data/agents_cli_mentions.md")

    try:
        result = run_monitoring_sweep(tracking_file)
        print(json.dumps(result, indent=2))
        sys.exit(0)
    except Exception as e:
        logger.error(f"Monitoring sweep failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
