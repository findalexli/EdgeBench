Task finding: <issue number>.

## What and why

Five of the eight stored size anchors in `baseline_results.json` are below 8 bits per integer, impossible for the Varint starter they are documented to come from, and all eight are below its real size. This PR stores the starter's exact sizes (from `encoded_bytes`, the same on every grading) and rescales `linear` 0..320, the formula's maximum, 8 x 40. Throughput anchors don't change, so Known issue 2 stays. Known issue 7 (the scale saturates) is fixed and removed.

`runner_judge.py`, `/judge/*` and the formula are byte-identical; only the anchors, the scale, `scoring_scheme.md` and NOTES change.

## Decision for maintainers

CONTRIBUTING asks a fix to keep the scores of correct work or say how old scores map. Size anchors can't be corrected without moving raw scores, so the choice is the scale. All options use exact values. Scores below are for the 27 distinct files in our archive (73 reports).

| Option | Scale | new 0..100 | Top file | Starter | What it does |
|--------|-------|------------|----------|---------|--------------|
| A | 0..100, clipped (no scale change) | min(raw, 100) | 100 | 0.85 | 22 of 27 files tie at 100, so the differences among them disappear |
| **B, this PR** | 0..320 | raw / 3.2 | 52.16 | 0.27 | No clipping; keeps today's lower anchor and adds only the formula's maximum |
| C | 1..320 | max(0, (raw - 1) / 3.19) | 52.01 | 0 | Same order; the starter's raw 0.85 clips to 0 because throughput anchors still put it below the documented 1.0 |

We recommend B. A is one line less to review but erases the ranking for almost every real submission, as Known issue 7 already warned.

**How old scores map.** A report's own per-dataset fields give the new raw exactly, with no regrade:

    new raw = weighted mean of min(B_new / (encoded_bytes * 8 / n), 8) * min(decode_gbps / T_base, 40)

A dataset with `roundtrip_ok` false or an error counts 0 and keeps its weight, as in the judge. Compile errors and invalid results stay as they are. This reproduces all 73 stored scores with the old anchors.

No constant factor exists, because the size ratio differs per dataset: new raw / old raw is approximately 1.775-2.400 on our 71 reports other than the starter. Order changes on 6 of 351 file pairs, the largest an old gap of 5.86 between two files with one report each, and throughput noise on one file reaches more than that (the 47.82-63.60 row below).

The 8x size cap is not reached more often: the number of datasets at the cap is unchanged on all 73 reports.

## Old vs new judge

Both judges built from source with SForge's build function on one 8-vCPU worker, judge at the official 4 CPUs and 8g, graded with `tools/judge_local.py`, interleaved, order swapped each round. n is per judge.

| Submission | n | Old raw (= 0..100) | New raw | New 0..100 |
|------------|---|--------------------|---------|------------|
| Real agent-15 | 4 | 73.78 | 167.38-167.51 | 52.31-52.35 |
| Real auto-3 | 4 | 69.42-74.03 | 161.79-167.22 | 50.56-52.26 |
| Real r2 auto-5 | 4 | 47.82-63.60 | 96.75-126.69 | 30.24-39.59 |
| Starter | 4 | 0.24-0.25 | 0.83-0.88 | 0.26-0.28 |
| Starter with one corrupted value | 4 | 0 | 0 | 0 |

Encoded sizes are identical across both judges and all repeats, and the starter's sizes equal the new anchors. The spread on the real rows is decode throughput. Old-judge reports rescored with the new anchors give the same range as the new judge within that spread (`top` 167.51).

## Checklist for task changes

- [x] `version` in `task.toml` is bumped (any change that can move scores).
- [x] `NOTES.md`: the change and its score effect are under **Changes**, and Known issue 7 is removed. Issue 2 remains, with the starter's new figure.
- [x] Old vs new judge on the same submissions, on the same host, results above.
- [x] New blobs: none.

## Limits

The real submissions are from one agent's two runs on one host. We hold no leaderboard submissions, so the mapping is shown only on ours. `baseline_run.log` and the `S`, `encode_ms` and `decode_ms` fields still hold the old record; the judge reads only `bpi` and `decode_gbps`.
