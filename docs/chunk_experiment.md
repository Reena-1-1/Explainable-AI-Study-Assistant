# Chunk Size Experiment

## Results

| Chunk size | Overlap | Top-1 accuracy | Top-3 accuracy |
|---|---|---|---|
| 600 | 150 | 65% | 75% |
| 1000 | 200 | 65% | 75% |
| 1500 | 300 | 65% | 75% |

## Observations

- All three chunk configurations produced the same Top-1 and Top-3 accuracy on this test set.
- No chunk size clearly outperformed the others based on the measured accuracy.
- The 600/150 configuration is a reasonable starting choice because it uses smaller chunks, but further testing is needed to establish which configuration is best.

**Limitation:** Five questions have `expected_page = 0`, which appears to be a placeholder. These questions were counted as misses, so the reported accuracy may not reflect retrieval quality for those questions.
