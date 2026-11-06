## What and why

Task finding: #<ISSUE>.

The hidden type-system suites, 33.67 of the 100 points, call `.filter` on the return value of `analyze()`. Nothing the agent sees gives that shape, and the starter returns an object. This PR adds one paragraph to `instruction.md`:

> The evaluator calls `analyze(parse(lex(source)))`. `analyze` in `compiler/src/semantic.js` must return an array of diagnostics (empty when there are none), each an object with `level` (`"error"` or `"warning"`) and `message` (a string). The starter's `analyze` returns a different shape.

It is not in the existing Known issues. It goes in `instruction.md` because that file is in neither image.

## Judge unchanged

| Check | Before | After |
|-------|--------|-------|
| Judge image key | `ce45e420e181` | `ce45e420e181` |
| Work image key | `ef303afa4f05` | `ef303afa4f05` |
| Files under `environment/` and `judge/` with the same sha256 | | 190 of 190 |

So every existing score stays as it is, including correct work and the v1 leaderboard. Old vs new grades on the same submissions would be the same image twice, so we did not run them.

## Score effect

No judge change means the effect shows only in what a solver writes. So here is a fixed submission with and without the shape, `tools/judge_local.py`. Three workers each built the judge from 1187e2c (image key `ce45e420e181`) and graded both submissions twice, six grades per row, no spread:

| Submission | Score | Weighted | Type-system cases |
|------------|-------|----------|-------------------|
| Opus 5.5 solver, unchanged, returns an object | 61.31 | 1821 of 2970 | 0 of 128 |
| The same solver with an appended wrapper that returns its own diagnostics as an array | 94.81 | 2816 of 2970 | 127 of 128 |

Only `compiler/src/semantic.js` differs between the two archives.

We did not measure how much the sentence alone helps a new solver. One Opus 5.5 run per variant gave best scores of 61.31 on the original task and 96.06 with wider documentation (this shape, diagnostic wording, semantic rules and the starter's score), at 4 GiB work and 3 GiB judge memory rather than the official limits; it is one run each and does not isolate this sentence.

Existing submissions keep their scores, so one that lost points to this stays low until it is resubmitted. A judge that accepted both shapes would change old scores, and the starter's too, so we did not propose that.

## Checklist for task changes

- [x] `version` in `task.toml` is bumped.
- [x] `NOTES.md`: the change and its score effect are under **Changes**; **Source** notes the instruction change. It is not a listed Known issue.
- [x] Judge unchanged, shown above in place of an old vs new judge table.
- [x] New blobs: none.

Three cases in `round2-type-system` also check message text, 0.51 of 100. We left them out to keep this to the return shape; the Opus 5.5 solver above passes all but one type-system case without being told.

We first found this in [EdgeBench Verified](https://lishengzhi.com/edgebench-verified/tasks/arc_compiler_runtime.html), our audit of EdgeBench's tasks.
