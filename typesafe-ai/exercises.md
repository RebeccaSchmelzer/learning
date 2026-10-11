# TypeSafe AI + Jev exercise worksheet

Follow the [learning path](learning-path.md) for timing and exact commands. This worksheet is optional: spoken predictions, code comments, and passing checks count as evidence. These exercises fit inside the same two hours, rather than adding more work.

## 1. Trace the example · 0–10 minutes

- [ ] Predict the queue and priority for the invoice fixture, then run it.
- [ ] Locate state, questions, answers, and decision policy in [the starter](project/jev_lab.py).
- [ ] Check playground access for at most five minutes, then continue offline if needed.

| Before running: prediction | After running: observation | What explains the result? |
|---|---|---|
| | | |

Which function performs a model call in live mode, and which produces an invented response offline?

## 2. Inspect the API contract · 10–30 minutes

- [ ] Print the request. Explain the roles of `state`, `model`, and `questions`.
- [ ] If access works, make a live call and change only the message. Otherwise compare the clear and uncertain fixtures.
- [ ] Find the response fields your policy actually reads.

| Input / one change | Expected behavior | Observed behavior | Live or fixture? |
|---|---|---|---|
| Original message | | | |
| New message | | | |
| Revised question wording | | | |

Mark unrun cases as untested. Offline responses cannot establish how Jev behaves on new text.

## 3. Choose the right primitive · 30–50 minutes

- [ ] Add the frustration Score described in the learning path.
- [ ] Compare an angry message with no deadline and a polite message reporting an outage.
- [ ] Explain why urgency, frustration, and department are separate judgments.

| Judgment | Choice, Noul, or Score? | What does the returned value mean? |
|---|---|---|
| Which support queue? | | |
| Does this need attention today? | | |
| How frustrated is the writer? | | |

Explain the difference between a Noul of 0.5 and a Score of 0.5 on a three-level rubric. Explain why a question cannot depend on another answer in the same request.

## 4. Break, debug, and verify · 50–75 minutes

- [ ] Predict and compare routing at thresholds 0.8 and 0.2.
- [ ] Introduce the truthiness bug in the learning path and reproduce it using the clear fixture.
- [ ] Inspect the value causing the wrong action, restore explicit thresholds, and add a focused regression assertion.
- [ ] Assert that the uncertain fixture goes to human review at 0.8.
- [ ] Run the confidently wrong fixture and explain why its mistake passes a confidence gate.

| Symptom | Hypothesis | Observation that tests it | Fix / verification |
|---|---|---|---|
| | | | |

## 5. Rebuild and evaluate · 75–105 minutes

Rebuild `decide` yourself before looking at the original body. Add a loop over the six messages in the learning path. State the expected handling before inspecting outputs.

| Case | Expected queue / priority | Observed queue / priority | Correct, review, or wrong? | Live or fixture? |
|---|---|---|---|---|
| Invoice copy | | | | |
| Everyone locked out | | | | |
| Sponsorship request | | | | |
| Vague account problem | | | | |
| Angry but can wait | | | | |
| Explicitly not urgent | | | | |

Reuse the same saved responses for the threshold comparison; do not mix a model change with a policy change.

| Choice confidence threshold | Automatic routes | Reviewed tickets | Wrong automatic routes |
|---|---|---|---|
| 0.5 | | | |
| 0.8 | | | |

These are learning examples, not a benchmark. Say which cases and denominator you use for any accuracy calculation. A review is a separate outcome, not an automatically correct label.

Remove a required answer from an invented response. Confirm that the program reports failure instead of selecting a queue. Trace where that error is caught.

## 6. Transfer and explain · 105–120 minutes

- [ ] Design a Choice that routes app feedback to bug report, feature request, or other.
- [ ] Add one focused Noul question and two tricky input messages.
- [ ] Run one request if access works, or inspect it and identify what remains untested.
- [ ] Explain the architecture in two minutes without reading the docs.

Be able to answer:

- What are TypeSafe AI and Jev?
- Which decisions belong to Jev, and which belong to ordinary code?
- What does each question type return?
- What happens when the answer is uncertain or the request fails?
- How can a confident answer still produce the wrong action?

Optional resumption note: **Tried / observed / next**. No separate notes file is required.
