Earlier combined text of #43 (validator and status change together, key 08140b58c121), kept for its full tables. Issue: #42.

Task finding: #42.

## What and why

Correct `sat` models on at least six hard QF_UFLRA files crash `evaluate.py`'s recursive validator at an 8 MiB stack, and the judge reports a valid 0 for the whole submission. Details and a reproducer are in the issue. Two changes:

1. **`evaluate.py`, judge and workspace copies.** `validate_sat_witness` now runs in a thread with a 2 GiB stack and a recursion limit of 1,000,000. If the thread can't start, or validation runs out of memory, the evaluation ends: that says nothing about the model, so it isn't recorded as an invalid model (a bare `except Exception` in numeric parsing used to turn that `MemoryError` into a rejected model, and now re-raises it).
2. **`run.sh` and `parse_result.py`.** The evaluator's exit status is passed on. No score file and a status other than 0 or 2 now gives `valid: false`, not a valid 0. `evaluate.py`'s "solver is not executable" exit changes from 1 to 2, so a missing `solve` stays a valid 0, as today.

The validator's logic, the cases, the scoring and the scale don't change. Known issue 1 (forging) and the other known issues stay as they are; change 2 looks only at a missing score file. `task.toml` goes to 1.1.0 and NOTES has the Changes entry.

## Decision for maintainers

We recommend both changes. Each alone leaves something wrong:

| | Five files only: real solver | Full hidden set: real solver | A crash with some other cause | Build failure, no `solve`, preflight, `unknown`, wrong answers |
|---|---|---|---|---|
| Today | 0.00 valid, `correct=0/0`, n=3 | 0.00 valid, `correct=0/0`, n=6 | Valid 0 | Unchanged |
| Only `evaluate.py` | 70.00, `correct=5/5`, n=2 | Not run; expected as this PR | **Valid 0 still** | Unchanged |
| Only the outer judge | Invalid, n=3 | Not run; expected invalid, so **correct work stays unscored** | Invalid | Unchanged |
| **Both, this PR** | 70.00, `correct=5/5`, n=2 | 47.34, n=1 on this code; 44.93-46.64, n=4 on an earlier revision | Invalid | Unchanged, n=2 per judge |

The 70.00 is on a hidden set cut down to the first five files, for this test only.

A larger stack alone isn't enough. It turns the crash into `RecursionError`, which the validator counts as an invalid model, so correct answers are rejected. That is why earlier diagnostic runs, the old validator in a 1 GiB thread at limit 20000, scored 47.04 and 46.17, with 90 QF_UFLRA correct and 4-5 invalid models. With the raised limit it is 94 or 95 and 0, n=4.

**How old scores map.** For identical solver outputs, validation verdicts are preserved unless the old validator crashed, rejected a model because of its recursion limit, or ran out of memory. In the other direction, a host that can't reserve 2 GiB of address space per validation now ends the evaluation even on a shallow file that the old validator accepted, and validations that go deeper than the old limit use more memory. On the default stack we saw only crashes, never those rejections. The formula and scale don't change; timed reruns can vary.

We checked this on the real solver's output, on this code. All 774 inputs, its 354 models, each validated by both judges' code on identical input and witness: 322 accepted by both, 28 rejected by both with identical exception types and recorded message prefixes (25 QF_UF congruence, 3 false assertions, none for recursion), and 4 that crash the old code and pass the new. An earlier solver run gave 367 models on the earlier revision: 334, 28, and 5 crashes. Three more models from deep files, the solver run alone, earlier revision: one crash to accepted, two accepted by both. Regrade a valid 0 with `correct=0/0` from a submission that built and ran, which is a crash, and any model rejected for the old limit. Other valid zeros stay.

**Same-host evidence.** Row J is one complete full-set pair on this code: 0.00, then 47.34. Earlier revisions add two complete pairs with new first, 0.00 to 46.58 and 0.00 to 46.45. A worker's 3300 s budget fits one pair at best, so we have no two pairs on one host. Three earlier attempts with old first got 0.00 and then ran out of budget, 1702-1788 s into the new grade, while row J's new grade took 1554 s; we don't know why those ran long. Five of the eight attempts didn't finish a pair, as listed below. The five-file row and failure paths are on one worker. You could settle the rest with your archives if any reach the crash.

**Overlap with open PRs.** No file overlap. #16 (`sforge/harness/grading.py`, base `main`) marks an absent structured result invalid. It wouldn't catch this case: `parse_result.py` always prints a valid structured block, so nothing is absent, and it wouldn't credit correct answers. #17 (`examples/portfolio-scoring-repair/`) is the same failure class in another task's scorer, as an opt-in image repair. This PR does for `smt_solver`'s own parser what they do elsewhere.

## Old vs new judge

8 CPUs and 7 GiB, with the evaluator's 16 workers as in `run.sh`, on 8-vCPU, 8 GiB workers; the official 16 CPUs and 16 GiB don't fit. Old judge key `cd3a5bf1f538`, new `08140b58c121`, `ulimit -s` 8192 in the container. Rows J, F and the tables below ran on that key. Rows A-E, G-I ran on earlier revisions, which differ only in how a validator failure is handled and have other keys. Same submission throughout: real solver, sha256 `3c131e4e...`, at https://github.com/findalexli/EdgeBench/tree/7f9709bfb8767156ca0ef8990a490ca587c97604.

| Hidden set | Worker | Order | Old | New |
|------------|--------|-------|-----|-----|
| Full, 774 files, **this code** | J | Old, then new | 0.00, valid, `correct=0/0`, 1495 s | 47.34 (`correct=336/774`), 1554 s |
| Full | A | New, then old | 0.00, valid, `correct=0/0`, 1533 s | 46.58 (`correct=331/774`), 1596 s |
| Full | B | New, then old | 0.00, valid, `correct=0/0`, 1551 s | 46.45 (`correct=330/774`), 1603 s |
| Full | C | New, then old | Unfinished at the budget | 44.93 (`correct=322/774`), 1665 s |
| Full | D | New, then old | Skipped: over budget | 46.64 (`correct=332/774`), 1884 s |
| Full | E | Old, then new | 0.00, valid, `correct=0/0`, 1486 s | Unfinished at the budget, 1749 s in |
| Full | G | Old, then new | 0.00, valid, `correct=0/0`, 1559 s | Unfinished at the budget, 1702 s in |
| Full | H | Old, then new | 0.00, valid, `correct=0/0`, 1484 s | Unfinished at the budget, 1788 s in |
| Full, solver answers `unknown` on the five files | I | Old, then new | 45.84 (`correct=325/774`), 1592 s | 45.58 (`correct=325/774`), 1592 s |
| Five files, cut for this test | F | Old first | 0.00, `correct=0/0`, n=3 | 70.00, `correct=5/5`, n=2, 328-348 s |

On every worker but F the old image is your published tag and the new one is that tag plus the three changed judge files, because a build of both leaves too little of the budget for two full grades; on J those three files are the ones built on worker F. An earlier revision of this branch, differing only in how the thread failure is handled, scored 48.14 (`correct=341/774`) and 47.36 (`correct=336/774`) on separate workers, 1513-1528 s.

Failure paths, on worker F with `sforge build` images, order swapped, n=2 per judge unless noted. Every control matches between judges; the last row is the reproducer, which is meant to differ:

| Submission | Old | New |
|------------|-----|-----|
| Fails to build | 0, valid, `correct=0/0` | Same |
| Missing `solve` | 0, valid, `correct=0/0` | Same |
| Rejected by preflight | 0, valid, `correct=0/0` | Same |
| Empty archive, n=1 | 0, valid, `correct=0/0` | Same |
| Always `unknown` | 0, valid, `correct=0/774` | Same |
| Replay fixture with wrong models | 0, valid, `correct=0/774` | Same |
| Replay fixture with correct models on 42 files, no crash | 6.28, valid, `correct=42/774` | Same |
| The issue's reproducer | 0, valid, `correct=0/0` | 0.11, valid, `correct=1/774` |

Row I is the preservation check on a real solver: the same solver, except that a `case` on the five input hashes answers `unknown`, so the old judge doesn't crash. Both judges count 325 correct and 28 invalid models. By logic, correct is 75/76, 51/49, 109/109, 90/91 old/new, and the differences are timeouts and solver errors, not validation. The 0.26 gap is smaller than the new judge's own spread on the unguarded solver (44.93-46.64). Judge files differ only in `evaluate.py`, `run.sh` and `parse_result.py`.

Validator failure, the reproducer through the judge's `run.sh` on the new judge under a shell address-space limit:

| `ulimit -v`, KiB | Result | n |
|------------------|--------|---|
| 1800000-2200000 | `ValidatorFailure: cannot start the validator thread`, invalid | 1 each, 5 limits |
| 2300000 | `ValidatorFailure: the validator ran out of memory`, invalid | 2 |
| 2400000, 2500000, 2700000, or none | 0.11, `correct=1/774` | 1 each |

Limits:

- The crash needs the 8 MiB stack, see the issue; CPUs and memory made no difference in what we tested. The full-run score is measured below official resources, and many cases sit near the 60 s limit, so expect a different number at official settings.
- We hold one solver that reaches this crash. No leaderboard submission was available to us.
- With a 1 GiB stack, the deepest captured witness took 279-321 s and up to 1427 MiB peak RSS; the 2 GiB stack diagnostic at the selected recursion limit took 268 s. That doesn't count against the solver's 60 s limit.
- **Memory.** The 2 GiB stacks are address space, committed as the recursion reaches them, but a deep validation does use real memory. At 7 GiB the new judge's grades recorded 6-8 cgroup OOM kills, nearly all from QF_UFLRA onward, and the completed grades have 6-7 QF_UFLRA cases counted as errors. We read those as solver processes killed, but didn't attribute each one. The old judge's recorded 0-2, because it stops at the crash before most of that work. A pool worker killed for memory still ends the evaluation, as today, and with this PR that gives invalid. It didn't happen in our completed grades (`BrokenProcessPool` 0, n=5). We have not measured 16 GiB.
- **Files deeper than the new limit: not covered.** A correct model that goes past 1,000,000 frames still scores as an invalid model, which is wrong for that file, though it no longer ends the evaluation. An iterative validator would remove this limit; we kept the smaller change, and that choice is yours. A heuristic simulation of the validator, with its define cache and no short-circuit, estimates 1.29-3.82 million frames on five `sat` files if a model visits every definition. It is an estimate, not a measurement; the one file we could check against a real witness is `7cf7d9bc1df9f7f0`, estimated at 721,329, whose witness fails at 600,000 and passes at 800,000. Real models on three of the five were accepted in 43-58 s, presumably because `or` short-circuits on those models; the solver gave no model on the other two in 75 s.
- **Deep formulas.** This code on 40 synthetic runs across 15 shapes, at depths around the limit divided by frames per level, up to 2327 MiB peak RSS, and no crash: 27 ended in `RecursionError`, 4 in `unknown symbol 0` (the same limit, reached inside numeric parsing, shown at a lowered limit by `c17_smt_plus_mechanism.py`), all 31 scored as invalid models; 1 was an incomplete witness of ours, correctly rejected; 2 accepted (`define` chains at 100,000 and 200,000); and 6 reached the 330 s cap with no verdict (`not`, `imp` and `mul` at 334,000 and 500,100). So these show the crash is gone in these shapes, not that deep correct models pass, and it isn't a guarantee for every shape.
- **Time.** The validator is slow on deep input, in old and new code alike: nested `and` takes 35-39 s at depth 4000 on both, and 265 s at 8000 on the new. No hidden input nests past 2621 parentheses, and the real solver's models took at most 295 s.
- The deepest captured witness fails at 600,000 and passes at 800,000; 1,000,000 was selected to provide additional margin.

## Checklist for task changes

- [x] `version` in `task.toml` is bumped (any change that can move scores).
- [x] `NOTES.md`: the change and its score effect are under **Changes**. No Known issues entry is removed: this crash wasn't listed.
- [x] Old vs new judge on the same submissions, on the same host: three full-set pairs, each on one worker, one on this code and two on earlier revisions, plus the five-file and failure-path rows. See "Same-host evidence" for what this doesn't cover.
- [x] New blobs: none.
