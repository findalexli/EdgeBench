Earlier longer text of #41, kept for its control and load tables. Its `timeout_sec` comment was later dropped from the patch.

Task finding: #44. Part of Known issue 3 (host-dependent score). The pool mechanism is the one in #40, fixed for `vibrating_path_graph_coloring` by #36.

## What and why

The README specifies 30 seconds per case, and the evaluator enforces that with a wall-clock timeout. The judge runs 8 cases at once on the official 4 CPUs, so each case gets about half the CPU that 4 at a time would give it. SCHEMA says a parallel grader "sizes the pool with `SFORGE_CPUS`, not `nproc`".

This PR sets the pool to `min(8, SFORGE_CPUS, cases)`. `SFORGE_CPUS` must be a positive integer, and 4 applies only when it is absent (`sforge eval` sets it; `tools/judge_local.py` does not). `timeout_sec` goes from 600 to 1800, because a smaller pool takes longer: 50 cases of 30 s run one at a time take 1500 s. At the official 4 CPUs nothing needs it (longest measured grade 390.8 s), but at 600 a smaller `sforge eval --judge-cpu-limit` lost a real file's score: `c56c7b843057`, which searches for 28.8 s, timed out with no score at limits 1 and 2. A direct Docker run must set both `--cpus N` and `SFORGE_CPUS=N`.

That file at each limit through `sforge eval`:

| `--judge-cpu-limit` | Old | Old cases OK | New | New cases OK | New time |
|---------------------|-----|--------------|-----|--------------|----------|
| 4 (official), true 4 CPUs | 68.33, 68.29 | 50, 50 | 71.99, 72.49 | 50, 50 | 375 s |
| 3 | 47.45 | 49 | 72.23 | 50 | 491 s |
| 2 | 30.88, 19.85 | 48, 47 | 73.28, 73.30 | 50, 50 | 721 s |
| 1 | Not run | - | 72.61, 72.89 | 50, 50 | 1443 s |

Each row is from one worker, and different rows from different workers, so read across a row, not down the table. Limits below 4 aren't official settings. Limits 1 and 2 ran with `timeout_sec` 1800; limit 3 ran with 600 on the same judge image. An earlier run at limit 2 with 600 gave old 17.76, 43 of 50 OK, and new timed out with no score.

## Decision for maintainers

**This does not meet the bar the way #36 did.** There, your regrade showed archived submissions going invalid on the old judge. Here, no real solver we hold loses a case at the official 4 CPUs on a quiet host:

- All 89 grades in our agent runs passed 50 of 50, and so does every real file at true 4 CPUs below, on both judges. Deadline files gain 3.65-10.86 of 100 from extra search time (14 pairs, 7 files, table below), which is a shift, not a repair. The gain is only 0.45-1.38% of the raw score; the scale is steep here. Anchors stay as they are, so they were set on the old pool and new scores sit higher against them. Repeat grades on the old judge spread by up to 2.51 and on the new by up to 1.23 (the 28 s file, n=6).
- A file that loses cases there is our own control: a valid answer plus a fixed 20 s of CPU. It gets 2 of 50 on the old judge and 50 of 50 on the new one. Nothing we hold behaves like that by itself.
- Real files do lose cases when the host is short of CPU (the rows with 5 judges at once), and once on a worker whose cause we never found.

What argues for merging anyway is SCHEMA's rule, and the entries you already hold: the Regression summary's "historical 1 (no time check)", 38.30 / 22.02 and 54.24 / 18.54, and Known issue 3's submission with 3/50 cases in v1 and 45-50/50 now. We don't have those archives. **Could you regrade them on both judges, as you did on #36?** If they lose cases on the old judge and keep them on the new one, the fix removes a real failure. If they don't, this is a resource-policy change that moves deadline solvers by 3-11 points and leaves v1 entries not comparable, and leaving it under Known issue 3 is a reasonable answer.

Deterministic solutions that produce the same output and finish on both judges keep their scores. There is no mapping for the others; #36 is precedent for accepting that only once the failure is shown.

## Old vs new judge

Old judge: image key `506688ea9aec`. New judge: `71e8a001fed1`, the same files as this branch, for the nine-file and limit tables. The A-D table ran on an earlier key, `2ff94d55a66d`. It has the same `eval_apple_incremental_game.py`; only comments in `grade.py` and `Dockerfile` differ since.

`sforge eval` (sets `SFORGE_CPUS=4`). Scores 0..100, all grades valid. This is every grade from these jobs, not a selection. Pool table script and files: https://github.com/findalexli/EdgeBench/tree/7f9709bfb8767156ca0ef8990a490ca587c97604.

| File | Condition | n old, new | Old | New | Cases OK, old | Cases OK, new |
|------|-----------|------------|-----|-----|---------------|---------------|
| A: searches for 28 s by the clock | True 4 CPUs | 6, 6 | 68.10-70.60 | 73.25-74.49 | 50 | 50 |
| A | Quota 4 of 8 vCPUs, 1 judge | 11, 2 | 65.49-71.05 | 72.65-73.14 | 50 | 50 |
| A | 2 judges at once, 8 vCPUs | 2, 2 | 67.89-68.12 | 72.98-73.36 | 50 | 50 |
| A | 3 judges at once, 8 vCPUs | 3, 3 | 63.96-65.28 | 70.48-71.80 | 50 | 50 |
| A | 5 judges at once, 8 vCPUs, 4 workers | 25, 25 | 3.09-31.08 | 17.81-68.89 | 14-48 | 43-50 |
| B: searches to a deadline by the clock | True 4 CPUs | 4, 3 | 62.95-64.61 | 67.47-69.04 | 50 | 50 |
| B | Quota 4 of 8 vCPUs, 1 judge | 1, 1 | 61.37 | 67.68 | 50 | 50 |
| B | 3 judges at once, 8 vCPUs | 3, 3 | 58.94-60.17 | 63.84-65.39 | 50 | 50 |
| B | 5 judges at once, 8 vCPUs | 5, 5 | 54.11-55.37 | 60.54-61.57 | 50 | 50 |
| C: about 8 s of CPU, own 22 s cutoff | True 4 CPUs | 2, 2 | 19.88 | 19.88 | 50 | 50 |
| D: no clock, 0.1 s of CPU per case | True 4 CPUs | 3, 3 | 6.37 | 6.37 | 50 | 50 |
| D | Quota 4 of 8 vCPUs, 1 judge | 1, 0 | 6.37 | Not run | 50 | - |

Nine real files from our agent runs, true 4 CPUs, one judge at a time, both judges on one worker per pair, 18 pairs on three workers, with judge order reversed in each file's second pair. Each row keeps its pairs in order. No score fell, and every grade is 50 of 50 OK. Longest `runtime_seconds` 202.6 old, 375.3 new (command elapsed 218 s, 392 s).

| `solution.py` sha256 | Pair 1, first judge | Old | New | Change | Pair 2, first judge | Old | New | Change |
|----------------------|---------------------|-----|-----|--------|---------------------|-----|-----|--------|
| `7a30c585eb86` | Old | 37.89 | 48.75 | +10.86 | New | 41.80 | 51.27 | +9.47 |
| `28cb741436cc` | New | 49.09 | 59.23 | +10.13 | Old | 54.85 | 63.91 | +9.05 |
| `9713841d2083` | Old | 31.75 | 38.75 | +7.00 | New | 33.70 | 42.29 | +8.59 |
| `a430ebe934de` | Old | 51.99 | 58.90 | +6.91 | New | 51.36 | 58.53 | +7.17 |
| `3d9f0e536d61` | Old | 67.25 | 72.84 | +5.59 | New | 69.65 | 74.01 | +4.36 |
| `19c47bd860dd` | New | 67.48 | 72.32 | +4.84 | Old | 69.97 | 73.93 | +3.96 |
| `c56c7b843057` | Old | 68.33 | 71.99 | +3.65 | New | 68.29 | 72.49 | +4.20 |
| `84027bd4fa94` | New | 19.88 | 19.88 | 0.00 | Old | 19.88 | 19.88 | 0.00 |
| `e918edc4d5cd` | Old | 19.58 | 19.58 | 0.00 | New | 19.58 | 19.58 | 0.00 |

The second pair of six of these ran on another worker, and a file's old score differs by up to 5.76 between its pairs. The last two files have their own cutoffs, at 22 s and 25 s, and score the same on both judges.

A-D were written by Claude Opus 5.5 in our agent runs. sha256 of `solution.py`: A `74dcf0e244df`, B `dbb350cf31c5`, C `79adddf3369d`, D `13fa1efd2e4a`.

"True 4 CPUs" is a worker with 4 vCPUs online and one judge at a time. With 5 judges at once on one of the four workers, the new pool got 43-45 of 50 and the old 14-17; that worker's single-process speed fell from 36.47 to 17.81 Mloops/s during the run, for reasons we did not establish. Known issue 3 stays: the limit is still wall clock.

One earlier worker, not a controlled experiment: file A on `tools/judge_local.py`, one judge at a time, quota 4 of 8 vCPUs, host load unmeasured, gave old 48 and 49 of 50 OK (32.44, 46.81) and new 50 of 50 (70.36, 71.75). Two other workers under the same setup lost no cases.

Mechanism controls: a valid answer plus a fixed cost, not real solvers. `sforge eval`, one judge at a time, limited to 4 CPUs of 8 vCPUs, two grades per judge, reversing judge order, no spread in score:

| Submission | Old | Old time | New | New time |
|------------|-----|----------|-----|----------|
| 20 s of CPU per case | 0, 2 of 50 OK, total 3955266 | 201 s | 5.04, 50 of 50 OK, total 99714418 | 261-267 s |
| 28 s of CPU per case | 0, 2 of 50 OK | 209 s | 5.04, 50 of 50 OK | 365-375 s |

The same forms on `tools/judge_local.py`, changed only to pass `SFORGE_CPUS=4`, which equals this patch's default when the variable is absent. Three grades per judge, no spread in score:

| Submission | Old | Old time | New | New time |
|------------|-----|----------|-----|----------|
| No spin | 5.04, 50 of 50 OK | 1 s | 5.04, 50 of 50 OK | 1 s |
| 12 s of CPU per case | 5.04, 50 of 50 OK | 157 s | 5.04, 50 of 50 OK | 157-161 s |
| Busy for 25 s of wall clock per case | 5.04, 50 of 50 OK | 176 s | 5.04, 50 of 50 OK | 326 s |
| 40 s of CPU per case (over the limit) | 0, 0 of 50 OK | 211 s | 0, 0 of 50 OK | 391 s |

## How to reproduce

This covers the control only. It is one file, `solution.py` (sha256 `3c228ded022c5f6dd7a07e90fb8658b68ab63c2805696e828323b4c3665d427b`): a valid greedy answer that spins until the process has used 20 s of CPU, then prints.

<details><summary>solution.py</summary>

```python
# Test submission: a valid control answer plus 20 s CPU per case, single-threaded. Not a real solver.
import sys, io, time, base64, contextlib
MODE, W = 'cpu', 20
w0 = time.time(); c0 = time.process_time()
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    try:
        exec(compile(base64.b64decode("IyBFQlYgaG9uZXN0IGNvbnRyb2wgZm9yIGFwcGxlX2luY3JlbWVudGFsX2dhbWUgKFJFQURNRSBydWxlcyBvbmx5KTogZWFjaCB0dXJuLCBzdHJlbmd0aGVuIHRoZSBhZmZvcmRhYmxlCiMgbGV2ZWwtMCBtYWNoaW5lIHdob3NlIGV4dHJhIHByb2R1Y3Rpb24gb3ZlciB0aGUgcmVtYWluaW5nIHR1cm5zIHBlciBhcHBsZSBzcGVudCBpcyBsYXJnZXN0LCBpZiBpdCBwYXlzCiMgYmFjayBiZWZvcmUgdGhlIGVuZDsgb3RoZXJ3aXNlIGRvIG5vdGhpbmcuIEV4YWN0bHkgVCBsaW5lcy4KaW1wb3J0IHN5cwoKZGVmIG1haW4oKToKICAgIHQgPSBzeXMuc3RkaW4ucmVhZCgpLnNwbGl0KCkKICAgIE4sIEwsIFQsIEsgPSBtYXAoaW50LCB0Wzo0XSk7IEEgPSBsaXN0KG1hcChpbnQsIHRbNDo0ICsgTl0pKQogICAgQyA9IFtsaXN0KG1hcChpbnQsIHRbNCArIE4gKyBpICogTjo0ICsgTiArIChpICsgMSkgKiBOXSkpIGZvciBpIGluIHJhbmdlKEwpXQogICAgUCA9IFswXSAqIE47IGFwcGxlcyA9IEs7IG91dCA9IFtdCiAgICBmb3IgdHVybiBpbiByYW5nZShUKToKICAgICAgICByZW0gPSBUIC0gdHVybgogICAgICAgIGJlc3QgPSBOb25lOyBiciA9IDAuMAogICAgICAgIGZvciBqIGluIHJhbmdlKE4pOgogICAgICAgICAgICBjID0gQ1swXVtqXSAqIChQW2pdICsgMSkKICAgICAgICAgICAgaWYgYyA8PSBhcHBsZXM6CiAgICAgICAgICAgICAgICBnYWluID0gQVtqXSAqIHJlbQogICAgICAgICAgICAgICAgaWYgZ2FpbiA+IGMgYW5kIGdhaW4gLyBjID4gYnI6CiAgICAgICAgICAgICAgICAgICAgYnIgPSBnYWluIC8gYzsgYmVzdCA9IGoKICAgICAgICBpZiBiZXN0IGlzIG5vdCBOb25lOgogICAgICAgICAgICBhcHBsZXMgLT0gQ1swXVtiZXN0XSAqIChQW2Jlc3RdICsgMSk7IFBbYmVzdF0gKz0gMTsgb3V0LmFwcGVuZChmJzAge2Jlc3R9JykKICAgICAgICBlbHNlOgogICAgICAgICAgICBvdXQuYXBwZW5kKCctMScpCiAgICAgICAgYXBwbGVzICs9IHN1bShBW2pdICogUFtqXSBmb3IgaiBpbiByYW5nZShOKSkKICAgIHByaW50KCdcbicuam9pbihvdXQpKQoKbWFpbigpCg=="), "control", "exec"), {"__name__": "__main__"})
    except SystemExit as e:
        if e.code not in (None, 0):
            raise
if MODE == "cpu":
    while time.process_time() - c0 < W:
        pass
elif MODE == "wall":
    while time.time() - w0 < W:
        pass
sys.stdout.write(buf.getvalue()); sys.stdout.flush()
```

</details>

```
tar czf cpu20.tar.gz solution.py
python -m sforge build --task apple_incremental_game
python -m sforge eval --task apple_incremental_game --archive cpu20.tar.gz --json
```

We ran exactly this: community at `f92857a` gives 2 of 50 OK, score 0; this branch gives 50 of 50 OK, score 5.04 (n=2 per judge, reversing order; grade 201 s and 261 s).

## Checklist for task changes

- [x] `version` in `task.toml` is bumped (any change that can move scores).
- [x] `NOTES.md`: the change and its score effect are under **Changes**. No Known issues entry is fully fixed; issue 3 remains.
- [x] Old vs new judge on the same submissions, on the same host, results above.
- [x] New blobs: none.
