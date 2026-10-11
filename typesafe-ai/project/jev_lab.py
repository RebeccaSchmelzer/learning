"""Tiny TypeSafe/Jev learning lab. Python 3, no third-party packages.

Default: handcrafted fixtures, no network and no model inference.
--live: one real TypeSafe request; reads a key from the environment or a hidden prompt.
Official contract: https://docs.typesafe.ai/api
"""

import argparse
import getpass
import json
import os
import sys
import urllib.error
import urllib.request


# These are invented teaching examples, NOT recorded Jev outputs or benchmarks.
FIXTURES = {
    "clear": {
        "state": "Please email a copy of my invoice. Anytime next week is fine.",
        "probabilities": {"billing": 0.96, "technical": 0.02, "other": 0.02},
        "urgent": 0.05,
    },
    "uncertain": {
        "state": "My account looks wrong. Can you help?",
        "probabilities": {"billing": 0.49, "technical": 0.46, "other": 0.05},
        "urgent": 0.50,
    },
    "confidently_wrong": {
        "state": "The login page crashes for every customer. Our service is unusable.",
        "probabilities": {"billing": 0.96, "technical": 0.02, "other": 0.02},
        "urgent": 0.95,
    },
}


def make_request(state):
    return {
        "model": "jev-latest",
        "state": state,
        "questions": {
            "department": {
                "type": "choice",
                "instructions": "Which support queue best matches the message?",
                "criteria": {
                    "billing": "Invoice copies, incorrect charges, or refund requests",
                    "technical": "Software failures, login errors, or unavailable features",
                    "other": "Neither of these queues fits the request",
                },
            },
            "urgent": {
                "type": "noul",
                "instructions": (
                    "Does the message report a currently unusable service "
                    "or explicitly require a response today?"
                ),
            },
        },
    }


def fixture_response(name):
    case = FIXTURES[name]
    probabilities = case["probabilities"].copy()
    count = len(probabilities)
    confidence = (max(probabilities.values()) - 1 / count) / (1 - 1 / count)
    return {
        "model": "HANDCRAFTED_FIXTURE_NOT_JEV",
        "answers": {
            "department": {
                "type": "choice",
                "choice": max(probabilities, key=probabilities.get),
                "probabilities": probabilities,
                "confidence": round(confidence, 6),
            },
            "urgent": {"type": "noul", "noul": case["urgent"]},
        },
        "usage": {"input_tokens": 0, "output_tokens": 0},
    }


def decide(answers, threshold=0.8):
    """Exercise policy. These thresholds are illustrative, not validated defaults."""
    department = answers["department"]
    p_urgent = answers["urgent"]["noul"]
    queue = department["choice"]
    if department["confidence"] < threshold or queue == "other":
        queue = "human_review"
    priority = "urgent" if p_urgent >= 0.8 else "normal" if p_urgent <= 0.2 else "review"
    return {"queue": queue, "priority": priority}


def call_jev(payload):
    key = os.environ.get("TYPESAFE_API_KEY") or getpass.getpass("TypeSafe API key (hidden): ")
    if not key.strip():
        raise ValueError("A TypeSafe API key is required for --live.")
    request = urllib.request.Request(
        "https://api.typesafe.ai/v1/systemone",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + key.strip(), "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", choices=FIXTURES, default="clear")
    parser.add_argument("--live", action="store_true", help="Make one real API request")
    parser.add_argument("--state", help="Custom message; requires --live or --show-request")
    parser.add_argument("--threshold", type=float, default=0.8)
    parser.add_argument("--show-request", action="store_true", help="Print JSON only; no network")
    args = parser.parse_args()
    if not 0 <= args.threshold <= 1:
        parser.error("--threshold must be between 0 and 1")
    if args.state is not None and not (args.live or args.show_request):
        parser.error("Fixtures cannot evaluate new text. Use --live or --show-request.")
    state = args.state if args.state is not None else FIXTURES[args.fixture]["state"]
    payload = make_request(state)
    if args.show_request:
        print(json.dumps(payload, indent=2))
        return 0
    print("LIVE API" if args.live else "OFFLINE: invented response; no Jev call")
    print("State:", state)
    try:
        response = call_jev(payload) if args.live else fixture_response(args.fixture)
        print(json.dumps(response, indent=2))
        print("Proposed action only:", json.dumps(decide(response["answers"], args.threshold)))
    except urllib.error.HTTPError as error:
        guidance = {
            400: "Check the request shape against the API reference.",
            401: "Check your TypeSafe API key.",
            403: "Check account and model access.",
            422: "Check the question types and required fields.",
            429: "Rate limited; wait before trying again.",
        }
        print(f"HTTP {error.code}: {guidance.get(error.code, 'Check service status and the API reference.')}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, TypeError, EOFError) as error:
        print(f"Request or response failed ({type(error).__name__}). No action was performed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
