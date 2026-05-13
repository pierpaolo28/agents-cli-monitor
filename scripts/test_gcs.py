#!/usr/bin/env python3
"""Test GCS integration for tracking file."""

import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.tracking import read_tracking_file, write_tracking_file


def test_gcs_integration():
    """Test reading and writing to GCS bucket."""

    project_id = os.popen("gcloud config get-value project").read().strip()
    bucket_name = f"agents-cli-monitor-reports-{project_id}"
    gcs_path = f"gs://{bucket_name}/test_agents_cli_mentions.md"

    print("=" * 80)
    print("Testing GCS Integration")
    print("=" * 80)
    print(f"Project ID: {project_id}")
    print(f"Bucket: {bucket_name}")
    print(f"Test file: {gcs_path}")
    print()

    # Test 1: Read non-existent file
    print("📖 Test 1: Reading non-existent file...")
    result = read_tracking_file(gcs_path)
    data = json.loads(result)
    print(f"   Total entries: {data['total_entries']}")
    print("   ✅ Reading non-existent file works")
    print()

    # Test 2: Write some test entries
    print("📝 Test 2: Writing test entries...")
    test_entries = [
        {
            "title": "[Blog] Test Entry 1 - GCS Integration",
            "url": "https://example.com/test1",
        },
        {
            "title": "[Docs] Test Entry 2 - GCS Integration",
            "url": "https://example.com/test2",
        },
    ]

    write_result = write_tracking_file(
        gcs_path,
        json.dumps(test_entries),
        date="2026-05-12"
    )
    write_data = json.loads(write_result)
    print(f"   Added: {write_data['added_count']}")
    print(f"   Skipped: {write_data['skipped_count']}")
    print(f"   Total: {write_data['total_entries']}")
    print("   ✅ Writing to GCS works")
    print()

    # Test 3: Read the file back
    print("📖 Test 3: Reading file back...")
    result = read_tracking_file(gcs_path)
    data = json.loads(result)
    print(f"   Total entries: {data['total_entries']}")
    print("   ✅ Reading from GCS works")
    print()

    # Test 4: Test deduplication
    print("📝 Test 4: Testing deduplication...")
    duplicate_entries = [
        {
            "title": "[Blog] Test Entry 1 - GCS Integration",  # Duplicate
            "url": "https://example.com/test1",
        },
        {
            "title": "[Article] Test Entry 3 - New Entry",  # New
            "url": "https://example.com/test3",
        },
    ]

    write_result = write_tracking_file(
        gcs_path,
        json.dumps(duplicate_entries),
        date="2026-05-12"
    )
    write_data = json.loads(write_result)
    print(f"   Added: {write_data['added_count']} (expected: 1)")
    print(f"   Skipped: {write_data['skipped_count']} (expected: 1)")
    print(f"   Total: {write_data['total_entries']} (expected: 3)")

    if write_data['added_count'] == 1 and write_data['skipped_count'] == 1:
        print("   ✅ Deduplication works")
    else:
        print("   ❌ Deduplication failed")
        return False
    print()

    # Test 5: Display content
    print("📄 Test 5: Displaying file content...")
    result = read_tracking_file(gcs_path)
    data = json.loads(result)
    print(data['content'])
    print()

    print("=" * 80)
    print("✅ All GCS integration tests passed!")
    print("=" * 80)
    print()
    print(f"Test file created at: {gcs_path}")
    print()
    print("To view in GCS:")
    print(f"  gsutil cat {gcs_path}")
    print()
    print("To delete test file:")
    print(f"  gsutil rm {gcs_path}")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_gcs_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print("\n❌ Test failed with error:")
        print(f"   {e}")
        print()
        print("Make sure you've authenticated:")
        print("  gcloud auth login")
        print("  gcloud auth application-default login")
        print()
        print("And that the bucket exists:")
        project_id = os.popen("gcloud config get-value project").read().strip()
        bucket_name = f"agents-cli-monitor-reports-{project_id}"
        print(f"  gsutil mb gs://{bucket_name}")
        print()
        sys.exit(1)
