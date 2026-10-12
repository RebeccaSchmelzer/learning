# PR review gate

Two runtime components, Python standard library only:

1. `produce.py` invokes your chosen coding agent with task text on stdin, captures a unified Git diff on stdout, checks applicability, and saves a patch without applying it.
2. `review.py` sends that patch to TypeSafe Jev, scores risk, flags security-sensitive changes, and writes a decision.

The reviewed repository must be clean. Output artifacts live outside that repository. Decisions bind to the repository base commit and patch SHA256; neither component merges or applies changes.

Jev evaluates two typed questions: `risk` as a four-level score (0–3) and `security_sensitive` as a yes probability. A pass requires score ≤1, confidence ≥0.8, and security probability ≤0.2. These are illustrative thresholds, not calibrated security guarantees. Other valid results require human review. Invalid results and request failures are errors.

Exit codes: 0 pass/success, 1 review required, 2 error. Handcrafted response fixtures never produce a real passing review.

No web server, queue, database, orchestration service, or automatic publishing.

API reference: https://docs.typesafe.ai/api
