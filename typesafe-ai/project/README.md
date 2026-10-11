# Jev ticket-router learning lab

Start with the [two-hour learning path](../learning-path.md) and [exercise worksheet](../exercises.md).

Requires Python 3. Uses only its standard library: no dependency installation. From the repository root:

```sh
python3 typesafe-ai/project/jev_lab.py
python3 typesafe-ai/project/jev_lab.py --show-request
python3 typesafe-ai/project/jev_lab.py --fixture uncertain
python3 typesafe-ai/project/jev_lab.py --fixture confidently_wrong
```

Default mode never calls an API. The responses are handcrafted teaching examples, not recorded model outputs. The program prints a proposed route and priority; it does not send tickets anywhere.

## Live use

If you have access, get a TypeSafe API key from its [console](https://console.typesafe.ai/) and run:

```sh
python3 typesafe-ai/project/jev_lab.py --live
python3 typesafe-ai/project/jev_lab.py --live --state 'The login page crashes for every customer.'
```

The program uses `TYPESAFE_API_KEY` if available, otherwise prompts invisibly for a key. Enter it locally, not in a worksheet or source file. Each `--live` invocation sends one request to TypeSafe. See the [official quickstart](https://docs.typesafe.ai/introduction/quickstart).

`--show-request` only prints the request and does not need a key. A custom `--state` requires `--live` or `--show-request`, because a fixed fixture cannot evaluate new text.

## Read these parts in order

1. `FIXTURES`: three invented cases, including uncertainty and a confident mistake.
2. `make_request`: turns a message into state plus a Choice and a Noul question.
3. `fixture_response` / `call_jev`: alternative sources of the same answer structure.
4. `decide`: applies your thresholds to choose a queue and priority.
5. `main`: connects the pieces and handles errors.

Try `--threshold 0.2` and `--threshold 0.8` on the uncertain fixture. The thresholds are teaching settings, not validated production defaults.

The existing offline paths, request construction, argument checks, and simulated 401/429 handling were checked before copying the lab here. A real Jev call has not been verified. Learner changes and model quality need their own checks.
