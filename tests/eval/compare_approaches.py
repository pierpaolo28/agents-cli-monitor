#!/usr/bin/env python3
"""Compare pattern detection approaches: conservative vs aggressive."""

import json

# Import detection functions
from app.tools.search import detect_agents_cli_patterns as improved_detect
from app.tools.search_balanced import detect_agents_cli_patterns as balanced_detect
from tests.eval.evaluation_dataset import KNOWN_MENTIONS


def conservative_detect(content: str, url: str) -> str:
    """
    Conservative approach - original version with higher thresholds.

    Key differences from improved version:
    - No URL-based patterns
    - No contextual patterns (ADK.*runtime, etc.)
    - No fuzzy matching
    - Single threshold: 0.3 for all domains
    """
    import re

    patterns_found = []
    confidence = 0.0

    # High confidence patterns (0.4 each)
    high_confidence_patterns = [
        (r"agents-cli", "CLI tool name mentioned"),
        (r"Agents CLI", "Agents CLI explicitly mentioned"),
        (r"github\.com/google/agents-cli", "GitHub repo URL"),
        (r"google\.github\.io/agents-cli", "Documentation URL"),
    ]

    # Medium confidence patterns (0.2 each)
    medium_confidence_patterns = [
        (r"agents-cli\s+(create|deploy|install|playground|eval)", "CLI command"),
        (r"google-agents-cli", "Package name"),
        (r"uvx google-agents-cli", "Installation command"),
        (r"Agent Development Kit.*CLI", "ADK + CLI context"),
    ]

    # Low confidence patterns (0.1 each)
    low_confidence_patterns = [
        (r"ADK.*agent.*deploy", "ADK deployment context"),
        (r"Agent Platform.*runtime", "Agent Platform context"),
        (r"Gemini Enterprise Agent Platform.*CLI", "Gemini Agent Platform + CLI"),
    ]

    # Check high confidence patterns
    for pattern, description in high_confidence_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            patterns_found.append(description)
            confidence += 0.4

    # Check medium confidence patterns
    for pattern, description in medium_confidence_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            patterns_found.append(description)
            confidence += 0.2

    # Check low confidence patterns
    for pattern, description in low_confidence_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            patterns_found.append(description)
            confidence += 0.1

    # Cap confidence at 1.0
    confidence = min(confidence, 1.0)

    # Single threshold for all domains
    threshold = 0.3
    is_relevant = confidence >= threshold

    reason = ""
    if is_relevant:
        reason = f"Found {len(patterns_found)} Agents CLI pattern(s): {', '.join(patterns_found[:3])}"
        if len(patterns_found) > 3:
            reason += f" (+{len(patterns_found) - 3} more)"
    else:
        reason = "No significant Agents CLI patterns detected"

    result = {
        "is_relevant": is_relevant,
        "confidence": round(confidence, 2),
        "patterns_found": patterns_found,
        "reason": reason,
        "threshold_used": threshold,
    }

    return json.dumps(result)


# False positive test cases - should NOT match
FALSE_POSITIVE_CASES = [
    {
        "url": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/overview",
        "title": "Gemini Enterprise Agent Platform Overview",
        "content": "The Gemini Enterprise Agent Platform helps you build and deploy AI agents. Learn about agent capabilities and platform features.",
        "category": "false_positive",
        "reason": "General GEAP docs, no CLI mention",
    },
    {
        "url": "https://medium.com/google-cloud/adk-deployment-guide",
        "title": "ADK Deployment Best Practices",
        "content": "Best practices for deploying agents with the Agent Development Kit. Learn about runtime configuration and deployment strategies.",
        "category": "false_positive",
        "reason": "ADK deployment, but no CLI",
    },
    {
        "url": "https://cloud.google.com/blog/products/ai-machine-learning/agent-platform",
        "title": "Building Agents with Agent Platform",
        "content": "Agent Platform provides tools to build intelligent agents. Deploy and manage your agent applications at scale.",
        "category": "false_positive",
        "reason": "Agent Platform, but not specific to CLI",
    },
    {
        "url": "https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-builder",
        "title": "Agent Builder Documentation",
        "content": "Use Agent Builder to create conversational agents. Configure agent runtime and deploy to production.",
        "category": "false_positive",
        "reason": "Different agent tool, not ADK CLI",
    },
    {
        "url": "https://github.com/other-org/agent-cli",
        "title": "Agent CLI Tool",
        "content": "A command-line tool for managing agents. Use agent-cli to deploy and monitor your agents.",
        "category": "false_positive",
        "reason": "Different agent CLI, not Google's",
    },
    {
        "url": "https://example.com/adk-tutorial",
        "title": "ADK Runtime Tutorial",
        "content": "Learn how to use the Agent Development Kit runtime. Build and deploy agents with ADK.",
        "category": "false_positive",
        "reason": "ADK general content, no CLI",
    },
]


def test_approach(detect_fn, approach_name: str, test_cases: list) -> dict:
    """Test a detection approach on a set of test cases."""
    results = {
        "approach": approach_name,
        "total": len(test_cases),
        "detected": 0,
        "missed": 0,
        "details": [],
    }

    for case in test_cases:
        content = f"{case['title']} {case.get('content', case['title'])}"
        detection_json = detect_fn(content, case['url'])
        detection = json.loads(detection_json)

        is_detected = detection['is_relevant']

        results['details'].append({
            "title": case['title'],
            "url": case['url'],
            "detected": is_detected,
            "confidence": detection['confidence'],
            "patterns": detection['patterns_found'],
            "threshold": detection['threshold_used'],
        })

        if is_detected:
            results['detected'] += 1
        else:
            results['missed'] += 1

    return results


def print_comparison():
    """Run and print comparison of all three approaches."""
    print("\n" + "=" * 80)
    print("           PATTERN DETECTION APPROACH COMPARISON")
    print("=" * 80)
    print()

    # Test on TRUE POSITIVES (known mentions - should detect)
    print("📊 TRUE POSITIVES - Known Agents CLI Mentions (should detect)")
    print("-" * 80)

    conservative_tp = test_approach(conservative_detect, "Conservative", KNOWN_MENTIONS)
    balanced_tp = test_approach(balanced_detect, "Balanced", KNOWN_MENTIONS)
    improved_tp = test_approach(improved_detect, "Improved (Aggressive)", KNOWN_MENTIONS)

    print("\nConservative Approach:")
    print(f"  Detected: {conservative_tp['detected']}/{conservative_tp['total']} ({conservative_tp['detected']/conservative_tp['total']*100:.1f}% recall)")
    print(f"  Missed: {conservative_tp['missed']}")

    print("\nBalanced Approach:")
    print(f"  Detected: {balanced_tp['detected']}/{balanced_tp['total']} ({balanced_tp['detected']/balanced_tp['total']*100:.1f}% recall)")
    print(f"  Missed: {balanced_tp['missed']}")

    print("\nImproved (Aggressive) Approach:")
    print(f"  Detected: {improved_tp['detected']}/{improved_tp['total']} ({improved_tp['detected']/improved_tp['total']*100:.1f}% recall)")
    print(f"  Missed: {improved_tp['missed']}")

    # Show which ones each approach missed
    print("\n📌 Conservative approach missed:")
    for detail in conservative_tp['details']:
        if not detail['detected']:
            print(f"  ✗ {detail['title']}")
            print(f"    Confidence: {detail['confidence']}, Threshold: {detail['threshold']}")

    print("\n📌 Balanced approach missed:")
    for detail in balanced_tp['details']:
        if not detail['detected']:
            print(f"  ✗ {detail['title']}")
            print(f"    Confidence: {detail['confidence']}, Threshold: {detail['threshold']}")

    print("\n📌 Improved (Aggressive) approach missed:")
    for detail in improved_tp['details']:
        if not detail['detected']:
            print(f"  ✗ {detail['title']}")
            print(f"    Confidence: {detail['confidence']}, Threshold: {detail['threshold']}")

    # Test on FALSE POSITIVES (should NOT detect)
    print("\n" + "=" * 80)
    print("📊 FALSE POSITIVES - General ADK/Agent Content (should NOT detect)")
    print("-" * 80)

    conservative_fp = test_approach(conservative_detect, "Conservative", FALSE_POSITIVE_CASES)
    balanced_fp = test_approach(balanced_detect, "Balanced", FALSE_POSITIVE_CASES)
    improved_fp = test_approach(improved_detect, "Improved (Aggressive)", FALSE_POSITIVE_CASES)

    print("\nConservative Approach:")
    print(f"  Correctly rejected: {conservative_fp['missed']}/{conservative_fp['total']} ({conservative_fp['missed']/conservative_fp['total']*100:.1f}% precision)")
    print(f"  False positives: {conservative_fp['detected']}")

    print("\nBalanced Approach:")
    print(f"  Correctly rejected: {balanced_fp['missed']}/{balanced_fp['total']} ({balanced_fp['missed']/balanced_fp['total']*100:.1f}% precision)")
    print(f"  False positives: {balanced_fp['detected']}")

    print("\nImproved (Aggressive) Approach:")
    print(f"  Correctly rejected: {improved_fp['missed']}/{improved_fp['total']} ({improved_fp['missed']/improved_fp['total']*100:.1f}% precision)")
    print(f"  False positives: {improved_fp['detected']}")

    # Show false positives
    print("\n📌 Conservative approach false positives:")
    for detail in conservative_fp['details']:
        if detail['detected']:
            print(f"  ⚠ {detail['title']}")
            print(f"    Confidence: {detail['confidence']}, Patterns: {detail['patterns']}")

    print("\n📌 Balanced approach false positives:")
    for detail in balanced_fp['details']:
        if detail['detected']:
            print(f"  ⚠ {detail['title']}")
            print(f"    Confidence: {detail['confidence']}, Patterns: {detail['patterns']}")

    print("\n📌 Improved (Aggressive) approach false positives:")
    for detail in improved_fp['details']:
        if detail['detected']:
            print(f"  ⚠ {detail['title']}")
            print(f"    Confidence: {detail['confidence']}, Patterns: {detail['patterns']}")

    # Final summary
    print("\n" + "=" * 80)
    print("📈 SUMMARY")
    print("=" * 80)

    conservative_recall = conservative_tp['detected'] / conservative_tp['total'] * 100
    balanced_recall = balanced_tp['detected'] / balanced_tp['total'] * 100
    improved_recall = improved_tp['detected'] / improved_tp['total'] * 100

    conservative_precision = conservative_fp['missed'] / conservative_fp['total'] * 100
    balanced_precision = balanced_fp['missed'] / balanced_fp['total'] * 100
    improved_precision = improved_fp['missed'] / improved_fp['total'] * 100

    conservative_f1 = 2 * (conservative_precision * conservative_recall) / (conservative_precision + conservative_recall) if (conservative_precision + conservative_recall) > 0 else 0
    balanced_f1 = 2 * (balanced_precision * balanced_recall) / (balanced_precision + balanced_recall) if (balanced_precision + balanced_recall) > 0 else 0
    improved_f1 = 2 * (improved_precision * improved_recall) / (improved_precision + improved_recall) if (improved_precision + improved_recall) > 0 else 0

    print(f"\n{'Approach':<25} {'Recall':<10} {'Precision':<12} {'F1 Score':<10}")
    print("-" * 80)
    print(f"{'Conservative':<25} {conservative_recall:<10.1f}% {conservative_precision:<12.1f}% {conservative_f1:<10.1f}%")
    print(f"{'Balanced':<25} {balanced_recall:<10.1f}% {balanced_precision:<12.1f}% {balanced_f1:<10.1f}%")
    print(f"{'Improved (Aggressive)':<25} {improved_recall:<10.1f}% {improved_precision:<12.1f}% {improved_f1:<10.1f}%")

    print("\n💡 Recommendation:")

    # Find best F1 score
    f1_scores = {
        "Conservative": conservative_f1,
        "Balanced": balanced_f1,
        "Improved (Aggressive)": improved_f1,
    }
    best_approach = max(f1_scores, key=f1_scores.get)

    # Requirements: >=80% recall, >=80% precision
    meets_requirements = []
    if conservative_recall >= 80 and conservative_precision >= 80:
        meets_requirements.append("Conservative")
    if balanced_recall >= 80 and balanced_precision >= 80:
        meets_requirements.append("Balanced")
    if improved_recall >= 80 and improved_precision >= 80:
        meets_requirements.append("Improved (Aggressive)")

    if meets_requirements:
        print(f"  ✅ Use {meets_requirements[0].upper()} approach")
        print("     - Meets ≥80% recall AND ≥80% precision requirements")
        print("     - Best balance for production monitoring")
    else:
        print("  ⚠️  No approach meets both ≥80% recall AND ≥80% precision")
        print(f"     Best F1 score: {best_approach}")
        print("\n     Trade-offs:")
        print(f"     - Conservative: {conservative_recall:.0f}% recall, {conservative_precision:.0f}% precision (minimal noise)")
        print(f"     - Balanced: {balanced_recall:.0f}% recall, {balanced_precision:.0f}% precision (middle ground)")
        print(f"     - Aggressive: {improved_recall:.0f}% recall, {improved_precision:.0f}% precision (catches more, noisier)")
        print("\n     For production: Choose based on priority:")
        print("     - Precision > Recall: Use Conservative (fewer false alarms)")
        print("     - Recall > Precision: Use Balanced or Aggressive (don't miss mentions)")

    print("\n" + "=" * 80)
    print()


if __name__ == "__main__":
    print_comparison()
