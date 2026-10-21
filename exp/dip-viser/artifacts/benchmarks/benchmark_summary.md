# DiP Text-to-Motion Benchmark Summary

- **Total Runs**: 4
- **Successful Runs**: 4
- **Device**: NVIDIA GeForce GTX 1650 (cuda:0)
- **Checkpoint**: `model000600343.pt`

## Summary Metrics

| Metric | Min | Median | Max |
|---|---|---|---|
| Inference Latency (s) | 10.784 | 11.968 | 14.637 |
| Real-Time Factor (RTF) | 2.696 | 2.992 | 3.659 |
| Generated Motion FPS | 5.5 | 6.7 | 7.4 |

> **Note on Real-Time**: RTF < 1.0 means generation is faster than playback duration.

## Trial Details

| # | Prompt | Warm | Latency (s) | RTF | Gen FPS | VRAM (MB) |
|---|---|---|---|---|---|---|
| 1 | "A person walks forward and waves." | No (Cold) | 14.637 | 3.659 | 5.5 | 0.0 |
| 2 | "A person walks forward and waves." | Yes | 12.265 | 3.066 | 6.5 | 0.0 |
| 3 | "A person walks forward and waves." | Yes | 11.671 | 2.918 | 6.8 | 0.0 |
| 4 | "A person walks forward and waves." | Yes | 10.784 | 2.696 | 7.4 | 0.0 |
