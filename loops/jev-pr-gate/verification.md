# Verification

Verified on 2026-10-12.

Requested roles completed: architect, patch-producing component builder, Jev reviewer component builder, and independent verifier. The coordinator integrated their work in this folder.

## Results

- Combined suite: `python3 -m unittest discover -s tests -v` — 20 tests passed.
- Independent verifier: 14 additional checks passed against the final files. Its script is saved in `work/verification/check_gate.py`.
- Documented offline demo: producer emitted an applicable patch; low-risk and high-risk response fixtures returned `simulated_review_required` with exit 1; the high-risk response flagged security sensitivity. The demo repository remained clean with its original greeting. Both reports match the patch SHA256 and base commit.

The independent checks covered exact argument/stdin handling, applicable patch generation, unchanged repository and base commit, dirty input rejection, failed agents, invalid patches, source/task output protection, simulated and mocked live policy paths, malformed response rejection, missing-key errors replacing stale approvals, repository/patch changes during inference, and preview removing stale approval.

## Fixed findings

1. A reviewer report path outside a supplied repository subdirectory could still be inside the actual Git root. Canonical Git-root checks now run before report writes; the tracked source remained intact in the regression check.
2. A producer output path could overwrite its task file. Resolved-path equality is now rejected before the agent starts; the task stayed intact in the regression check.

No unresolved findings in the verified local behavior.

## Limits

No `TYPESAFE_API_KEY` was available, so no live Jev request was made. Mocked HTTPS responses and handcrafted fixtures verify the integration and policy logic, not real model judgment quality. A real authenticated coding-agent invocation was also not run; the documented Codex command was checked against local CLI help and official documentation. Risk thresholds are illustrative and need evaluation on your changes before use as a production policy.
