# alignment-comparison-plots

Qt-based forced-alignment comparision plot utils for Praat TextGrid corpora.

Point it at two sets of TextGrid files and get interactive charts that answer:

- Do the two aligners agree on which phonemes appear and how often?
- How well do their interval boundaries agree, per phoneme?
- Which phonemes are consistently mis-labelled or mis-aligned?

Created as part of research at [WiscLab](https://kidspeech.wisc.edu/). The analyses implemented here were originally developed in R by [@tjmahr](https://github.com/tjmahr).

!!! warning "No internal validation"
    The library does not validate paths or file pairs. Validate your path lists before calling any plot function — the right checks depend on your use case.

!!! important "Files are matched by basename"
    `paths_a` and `paths_b` are paired by filename only. Both lists must contain files with identical names (one per recording). **Unmatched files are silently skipped** — mismatched or missing files will not raise an error.

## Install

```bash
pip install alignment-comparison-plots
```

Requires Python ≥ 3.11.
