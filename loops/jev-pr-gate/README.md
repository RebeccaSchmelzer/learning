# Jev PR review gate

Two components, Python 3.10+ and Git. No packages to install.

- `produce.py`: asks a coding agent for a unified diff and saves an applicable patch.
- `review.py`: asks TypeSafe Jev to score the patch and flag security-sensitive changes.

Both operate on a clean, committed Git repository. Neither applies the patch or merges a PR. Keep patch/report files outside the reviewed repository. This is a local gate you can call from CI; GitHub branch protection is not configured by this project.

## Real agent → Jev

Write a task file outside the reviewed repository. For example:

```text
Inspect this repository and implement the requested change: [describe your change].
Return only an applicable Git unified diff, starting with diff --git.
Do not edit files. Do not wrap the diff in Markdown or add explanations.
```

From this project directory, use your existing authenticated coding agent. With Codex available on your PATH:

```bash
python3 produce.py --repo /path/to/repo --task-file /path/to/task.txt \
  --output /path/to/change.patch -- \
  codex exec --sandbox read-only --color never --ephemeral -

python3 review.py --repo /path/to/repo --patch /path/to/change.patch \
  --output /path/to/review.json
```

The producer is provider-neutral: any executable can read the task on stdin and return the diff on stdout. It executes the supplied argument list directly. Use an agent you trust; the producer itself is not a sandbox. The Codex example uses its read-only sandbox and existing CLI sign-in.

The reviewer reads `TYPESAFE_API_KEY` from your local environment and sends the diff to TypeSafe over HTTPS. Get a key from the [TypeSafe console](https://console.typesafe.ai/) and set it locally; do not put it in source or chat. Without a key, review exits with an error. Preview the exact request without a key or network call:

```bash
python3 review.py --repo /path/to/repo --patch /path/to/change.patch \
  --output /path/to/review.json --show-request
```

## Offline demo

This fixture agent emits a handcrafted greeting change; it performs no inference. The response fixtures are invented Jev-shaped examples, not recorded Jev results.

```bash
mkdir -p work/demo-repo
printf 'print("hello")\n' > work/demo-repo/hello.py
git -C work/demo-repo init -q
git -C work/demo-repo add hello.py
git -C work/demo-repo -c user.name=Demo -c user.email=demo@example.invalid \
  commit -qm "Demo baseline"
printf 'Change the greeting to hello, world. Return only a unified diff.\n' > work/task.txt

python3 produce.py --repo work/demo-repo --task-file work/task.txt \
  --output work/demo.patch -- python3 "$PWD/fixtures/demo_agent.py"

python3 review.py --repo work/demo-repo --patch work/demo.patch \
  --output work/demo-review.json \
  --response-fixture fixtures/low-risk-response.json
```

The final command intentionally exits `1`: fabricated model answers can demonstrate policy, but cannot approve a patch. Inspect `work/demo-review.json`, then try `fixtures/high-risk-response.json` for the security-review path. Re-running the setup commit when nothing changed is unnecessary.

## Gate policy

Jev returns a risk score from 0 to 3, confidence, and the probability that the change is security-sensitive. A patch passes only when all three hold:

| Signal | Required to pass |
| --- | --- |
| Risk score | ≤ 1 |
| Risk confidence | ≥ 0.8 |
| Security-sensitivity probability | ≤ 0.2 |

Sensitive or uncertain results require human review. These thresholds are learning defaults, not calibrated vulnerability detection. A low risk score does not prove code is secure; run your ordinary tests and human review too.

The reviewer accepts UTF-8 patches up to 12,000 bytes and fails on larger input; split a larger change rather than truncating it. It uses a 30-second request timeout. The producer defaults to a 120-second agent timeout, adjustable with `--timeout`.

The JSON report identifies the exact patch SHA256 and Git base commit. A decision only applies to those inputs. A changed patch or base needs a new review.

Exit codes: `0` = producer success / live gate pass; `1` = review required; `2` = input, agent, response, or API error. API failures and invalid model output fail closed. Consumers must check the command's exit code and current report together, not reuse an earlier approval file. `--show-request` is request inspection, not a passing review.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

The test suite uses local repositories and mocked responses. No API calls or paid inference.

## Sources

- [TypeSafe API reference](https://docs.typesafe.ai/api): Jev request/response contract.
- [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode): stdin task and final stdout.
- [Codex command reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli): sandbox and execution flags.
