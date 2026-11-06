## What and why

Task finding: #<ISSUE>.

Hidden Phase 1 imports names from `schemathesis.specs.openapi.headers` and checks literal format keys and Range forms that `TODO.md` does not give. A module with other names fails the import and loses all of Phase 1, 15.38 of 100 points.

This PR adds a "Target 1 Module Interface" section to `instruction.md` with the module path, the six names, the three format keys, the list spacing the test's regexes require (`bytes=0-499, 500-999` and `"a" , "b"` fail them, though the RFCs allow both) and the Range forms the test checks, and adjusts one rule line to allow it. It is not in the existing Known issues.

It goes in `instruction.md`, not `TODO.md`, because `environment/Dockerfile` commits `TODO.md` into the work image and pins v1's commit (`test "$(git rev-parse HEAD)" = 409ef74...`). `instruction.md` is in neither image. If you would rather have it in `TODO.md`, that also means updating the pin and accepting new image tags.

## Old vs new judge

Both trees build the same images: judge `484f15fd657f`, work `8911231cbfba`; 18 of 18 files under `environment/` and `judge/` have the same sha256. One worker, `tools/judge_local.py`, task limits. "Names" is an alias layer we added to the real archive, standing in for a solver told them; we didn't measure how a solver reacts to this text.

| Submission | Old | New | Phase 1 |
|------------|-----|-----|---------|
| Opus 5.5 solver, unchanged | 72.31 (3 of 3) | 72.31 | 0 of 15 |
| Same, with names and keys | 86.67, 85.64, 86.67 | 85.64 | 13 or 14 of 15 |
| That plus the three literal Range forms | 87.69 (3 of 3) | 87.69 | 15 of 15 |
| Empty starter plus `headers.py` from Schemathesis 4.15.0 | 47.73 (3 of 3) | 47.73 | 15 of 15 |
| Empty starter | 32.35 (3 of 3) | not run | 0 of 15 |

The spread in the second row is an existing unseeded test (below), not the patch. Over all six jobs on this image: 72.31 in 19 of 19 grades, 85.64 or 86.67 in 15, 87.69 in 13, 47.73 in 11 of 12 (46.71 once).

## Not in this PR

- **The flake.** `test_negative_mode_range_has_three_tiers` needs the exact value `bytes=` among 200 unseeded Hypothesis examples, so the same file can lose 1.03 points on one grade. Draws of 200 with no `bytes=`: 30 of 60 for the solver with names only, 1 of 60 for the solver with the three forms, 1 of 60 for Schemathesis 4.15.0. Fixing it changes the test and can move scores, so it needs its own PR. `test_range_slightly_invalid_values_all_patterns` samples the same way in 100 examples.
- **HTTP-date checks.** `HTTP_DATE_RE` accepts impossible dates and wrong weekdays. The eight headers-bearing snapshots we inspected fail the Phase 1 import before this check, and we have not established how often it matters elsewhere. Tightening it lowers scores, so it is a separate change if you want it.

## Checklist for task changes

- [x] `version` in `task.toml` is bumped.
- [x] `NOTES.md`: the change is under **Changes**; **Source** notes the instruction change. It is not a listed Known issue.
- [x] Old vs new judge on the same submissions, above (both trees give the same images).
- [x] New blobs: none.

We first found this in [EdgeBench Verified](https://lishengzhi.com/edgebench-verified/tasks/schemathesis_datagen_pipeline.html), our audit of EdgeBench's tasks.
