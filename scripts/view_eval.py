#!/usr/bin/env python3
"""View the evaluation dataset."""

from tests.eval.evaluation_dataset import (
    CATEGORIES,
    TOTAL_KNOWN_MENTIONS,
    get_known_mentions_by_category,
)

print("\n" + "=" * 80)
print("           AGENTS CLI MONITOR - EVALUATION DATASET")
print("=" * 80)
print()
print(f"Total known mentions: {TOTAL_KNOWN_MENTIONS}")
print()
print("Breakdown by category:")
for cat, count in CATEGORIES.items():
    print(f"  {cat.ljust(10)}: {count}")
print()
print("=" * 80)
print()

by_category = get_known_mentions_by_category()

for category, mentions in sorted(by_category.items()):
    print(f"\n📂 {category.upper()} ({len(mentions)} mentions)")
    print("-" * 80)
    for mention in mentions:
        print(f"  • {mention['title']}")
        print(f"    {mention['url']}")
        print()

print("=" * 80)
print()
print("💡 This is the EVALUATION DATASET (ground truth)")
print()
print("To test if the agent can find these mentions:")
print("  1. Run: agents-cli playground")
print("  2. Prompt: 'Run a comprehensive monitoring sweep'")
print("  3. Check: data/agents_cli_mentions.md")
print("  4. Compare found mentions vs. this dataset")
print()
print("Target: Agent should find ≥80% of these known mentions")
print("=" * 80)
