# TypeSafe AI + Jev: two hours from zero to a small integration

For an experienced app builder who is new to this product. Primary topic: external API/platform. Secondary topics: AI decision design and evaluation. Target depth: practical first use. By the end, explain the interface, inspect a real response if access is available, implement a review path, and test a tiny ticket router. Defer deployment, model training, agent frameworks, production retries, and large benchmarks.

## What you are learning

TypeSafe AI provides the platform; Jev is its model for bounded judgments inside software. TypeSafe calls this a System One model. You send context (`state`) and explicit questions, and receive typed answers. It does not write arbitrary prose. [Official introduction](https://docs.typesafe.ai/introduction).

`message → state + questions → Jev → answers → your decision policy → proposed action`

The API returns judgments. Your application decides what to do with them.

| Primitive | Use it for | Interpret it correctly |
|---|---|---|
| Choice | Billing, technical, or other? | A chosen label plus probabilities and confidence. |
| Noul | Does this need attention today? | A probability of yes. Near 0.5 means uncertainty, not medium urgency. |
| Score | How frustrated is this person? | A position along levels you describe, plus probabilities and confidence. With three levels, the score runs from 0 to 2 and can be fractional. |

[Question types](https://docs.typesafe.ai/primitives), [Score levels](https://docs.typesafe.ai/primitives/score#levels).

Type safety constrains the answer's form; it does not prove the judgment is correct. A confidence value of 0.8 is not a guarantee of 80% accuracy: Choice/Score confidence summarizes the returned probability distribution. Noul has no separate confidence field. [Confidence](https://docs.typesafe.ai/confidence).

## 0–10 minutes: trace a working example and check access

Open the [playground](https://console.typesafe.ai/playground). Sign in or create an account if you want live access. Spend at most five minutes on access; if blocked, use the offline lab and return to access later.

The starter in [project/jev_lab.py](project/jev_lab.py) uses Python 3 with no packages to install. Run the commands below from this `typesafe-ai/` folder. [Project setup](project/README.md) has the alternatives; [exercises.md](exercises.md) is an optional worksheet for predictions and results.

```sh
python3 project/jev_lab.py --show-request
python3 project/jev_lab.py
```

Before running the second command, predict the department and priority for the invoice message. Trace `make_request → fixture_response → decide`. Identify which function will be replaced by a network call. The fixture's proposed action should be billing / normal.

**Evidence:** point to the state, question definitions, answer values, and application policy. All fixture outputs are invented teaching data, not measured Jev behavior.

## 10–30 minutes: make and modify one request

Follow only [Quick start → Playground / API](https://docs.typesafe.ai/introduction/quickstart). In the playground, use the state and two question definitions printed by `--show-request`. Predict each answer before submitting. Inspect the full result, including probabilities.

For a local API call, obtain a TypeSafe key from the console, then run:

```sh
python3 project/jev_lab.py --live
python3 project/jev_lab.py --live --state 'The login page crashes. Nobody can use our service.'
```

The script reads `TYPESAFE_API_KEY` if set; otherwise it prompts invisibly. Enter the key locally, not in chat. Each live invocation sends one request to TypeSafe. The lab prints proposed actions only.

Change only the message first. Then change one question's wording and repeat the same input. Compare observed answers; don't expect exact predetermined probabilities.

**Offline alternative:** inspect `make_request` and both fixture responses with `--fixture clear` and `--fixture uncertain`. Explain the request/response contract. This teaches integration, but does not test Jev's quality or prove access works.

**Evidence:** explain `state`, `model`, and `questions`, and find an answer using its question ID. Consult the [API reference](https://docs.typesafe.ai/api) only to resolve a field or error you encounter.

## 30–50 minutes: isolate the three question types

Keep Choice for department and Noul for urgency. Add a Score question to `make_request` called `frustration`, with your own ordered levels: neutral tone, expressed dissatisfaction, strongly angry tone. Print its answer. For offline work, handcraft a clearly labeled Score answer with probabilities `{0: 0.5, 1: 0.5, 2: 0}` and verify that its weighted score is 0.5. Score confidence follows a separate formula; consult its documentation rather than reusing Choice's formula.

Try these two states live, or predict them offline:

- “I am furious about the invoice, but next week is fine.”
- “Please help today; our entire team is locked out. Thank you.”

**Evidence:** distinguish frustration from urgency. Explain why a Noul of 0.5 and a Score of 0.5 mean different things. Each question sees the same state independently; do not expect a later question to see an earlier answer. [Question independence and answer types](https://docs.typesafe.ai/primitives).

## 50–75 minutes: break and debug the policy

Run the uncertain fixture with two thresholds:

```sh
python3 project/jev_lab.py --fixture uncertain --threshold 0.8
python3 project/jev_lab.py --fixture uncertain --threshold 0.2
```

Predict the proposed queue first. Explain why one threshold sends the ticket to review while the other selects billing. These thresholds are exercise settings, not validated production recommendations.

Intentionally replace the priority assignment in `decide` with:

```python
priority = "urgent" if p_urgent else "normal"
```

Run the clear fixture: why did 0.05 become urgent? Inspect the value and Python's truthiness rule, restore explicit probability thresholds, and write one regression assertion that the clear fixture's priority is normal. Add an assertion that the uncertain fixture's queue is human_review at 0.8. Two focused checks are enough.

Finally run `--fixture confidently_wrong`. The fabricated answer is confident but sends a login failure to billing. Explain why schema validation and confidence gating cannot guarantee semantic correctness. Read only [known limitations → Literal reading / Math and Numbers](https://docs.typesafe.ai/model-jaggedness/jev-1.13) when deciding what belongs in prompts versus code.

**Evidence:** reproduce, diagnose, fix, and verify the truthiness bug; explain the confidently wrong case without calling it a formatting failure.

## 75–105 minutes: build and evaluate a tiny router

Rebuild `decide` yourself without looking at its original body. Then add a loop over six messages:

| Message | Your intended handling |
|---|---|
| “Send my invoice when convenient.” | Billing; normal |
| “All customers are locked out right now.” | Technical; urgent |
| “Do you sponsor community events?” | Other → review; normal |
| “Something is wrong with my account.” | Ambiguous; review preferred |
| “I hate this invoice. Next week is fine.” | Billing; normal despite anger |
| “This is not urgent. Where is my invoice?” | Billing; normal |

Write down or say your expected labels before making calls. Keep each message as one state. If live access works, call Jev once per message and compare results with those expectations. If access remains blocked, supply your own labeled fake answers and verify only the routing logic.

For the same saved responses, compare confidence thresholds 0.5 and 0.8. Count automatic routes, reviewed tickets, and wrong automatic routes. Exclude review-only cases from any label-accuracy denominator; state your denominator. Six cases are a learning exercise, not an accuracy or calibration benchmark.

Keep responsibilities visible: input data → request builder → API/fixture → pure decision policy → printed action. Test a missing required answer with a fake response: the application should report failure rather than silently selecting a queue. The starter already stops on that error; inspect why. Don't build a dashboard or backend.

**Evidence:** a small runnable router, a review path, one known failure, and an explanation of what raising the threshold changed on your examples.

## 105–120 minutes: transfer and explain

Design a second use case without copying the support categories: route app feedback to bug report, feature request, or other. Write the Choice criteria, one Noul question, and two tricky test inputs. Make one live call if available, otherwise inspect the request and say what remains untested.

Explain aloud, in two minutes: what TypeSafe and Jev each are; which question type fits which decision; which work remains ordinary code; how your app treats uncertainty; and why a well-formed answer can still be wrong.

You are done when you can change the questions, trace the returned data into policy, and debug a wrong action. With no account access, you have learned the contract and policy design; live API operation and model evaluation remain the next step. No notes document or production deployment required.

Sources checked October 9, 2026. Starter verified with offline fixtures; a real Jev call has not been tested in this workspace.
