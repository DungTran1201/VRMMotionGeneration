# DiP Text-to-Motion Formal Benchmark & Performance Report

**Experiment**: `exp/dip-viser/`  
**Execution Date**: 2026-10-21  
**Hardware Platform**: Intel Core i5-12400F, 8 GB RAM, NVIDIA GeForce GTX 1650 (4 GB VRAM)  
**Operating System**: Windows 10 Pro 64-bit (Build 19045)  
**Software Stack**: Python 3.10.20, PyTorch 2.5.1+cu121, CUDA 12.1, Viser 1.1.1  
**Status**: `VERIFIED WITH LIVE BENCHMARKS`

---

## 1. Executive Summary

This report provides empirical timing and throughput metrics for the official DiP (Diffusion Planner) autoregressive text-to-motion model executing on an entry-level NVIDIA Turing GPU (GTX 1650, 4 GB VRAM).

### Key Takeaways
1. **Batch-to-Playback, Not Streaming**:
   - Measured warm Real-Time Factor (RTF) is **2.696x – 3.066x** (median: **2.918x**).
   - Generating a 4.0-second motion takes ~10.8s to 12.3s.
   - Because RTF > 1.0, generation speed is slower than real-time playback. The system operates as a **batch generation followed by continuous interactive playback** architecture. It must **not** be advertised as a real-time streaming pipeline.
2. **Cold Start Overhead**:
   - Cold start latency is **14.637s** (includes subprocess spawn, PyTorch CUDA context initialization, checkpoint loading, and CLIP tokenization).
   - Warm inference latency stabilizes at **10.784s – 12.265s**, showing a ~26% reduction compared to cold initialization.
3. **Decoupled Viewer Rendering**:
   - Viser's browser rendering loop runs independently at **~30–60 FPS**, decoupled from model generation.
   - Looping the already-generated motion sequence incurs **0% model re-inference overhead**.

---

## 2. Hardware and Checkpoint Configuration

| Component | Specification |
|---|---|
| **CPU** | Intel Core i5-12400F (6 Cores, 12 Threads) |
| **System RAM** | 8.0 GB DDR4 |
| **GPU** | NVIDIA GeForce GTX 1650 (TU117, 4 GB GDDR6) |
| **GPU Driver** | NVIDIA 591.74 |
| **CUDA Runtime** | 12.1 |
| **PyTorch** | 2.5.1+cu121 |
| **Viser** | 1.1.1 |
| **Checkpoint Path** | `checkpoints/DiP_no-target_10steps_context20_predict40/model000600343.pt` |
| **Checkpoint Size** | 232,011,477 bytes (~221.3 MB) |
| **Checkpoint SHA-256** | `bcf3e482a5236a21731af571c66bd7d0274f5ddf0b6974825fa69333c77f3144` |
| **Conditioning** | CLIP ViT-B/32 text encoder + GloVe vocabulary embeddings |

---

## 3. Empirical Benchmark Results

### 3.1 Aggregated Metrics Table

| Metric | Cold Run | Warm Min | Warm Median | Warm Max |
|---|---|---|---|---|
| **Inference Latency (s)** | 14.637 s | 10.784 s | 11.671 s | 12.265 s |
| **Decoding Latency (s)** | 0.010 s | 0.007 s | 0.008 s | 0.009 s |
| **Time to First Motion (s)** | 14.647 s | 10.791 s | 11.678 s | 12.272 s |
| **Generated Motion FPS** | 5.5 fps | 6.5 fps | 6.8 fps | 7.4 fps |
| **Real-Time Factor (RTF)** | 3.659x | 2.696x | 2.918x | 3.066x |
| **Peak VRAM Allocated** | ~1.6 GB | ~1.6 GB | ~1.6 GB | ~1.6 GB |

### 3.2 Individual Trial Details

| # | Trial Type | Prompt | Duration | Frames | Latency (s) | RTF | Gen FPS |
|---|---|---|---|---|---|---|---|
| 1 | **Cold Start** | *"A person walks forward and waves."* | 4.0 s | 80 | 14.637 s | 3.659x | 5.5 fps |
| 2 | **Warm Run 1** | *"A person walks forward and waves."* | 4.0 s | 80 | 12.265 s | 3.066x | 6.5 fps |
| 3 | **Warm Run 2** | *"A person walks forward and waves."* | 4.0 s | 80 | 11.671 s | 2.918x | 6.8 fps |
| 4 | **Warm Run 3** | *"A person walks forward and waves."* | 4.0 s | 80 | 10.784 s | 2.696x | 7.4 fps |

---

## 4. Analysis and Observations

### 4.1 Real-Time Factor (RTF) Definition
$$\text{RTF} = \frac{\text{Total Generation Time (seconds)}}{\text{Generated Motion Playback Duration (seconds)}}$$

- **RTF < 1.0**: Model generates faster than real-time (can support streaming).
- **RTF = 1.0**: Model generates exactly at playback speed.
- **RTF > 1.0**: Model generates slower than real-time (requires batch buffering).

With an RTF of ~2.7x–3.6x on a GTX 1650, the model produces ~6.8 motion frames per real second, while HumanML3D playback requires 20 frames per second. Therefore, full sequence generation is buffered before playback initiates.

### 4.2 Generation FPS vs Viewer Render FPS
It is vital to distinguish:
1. **Generated Motion FPS ($\approx 6.8\text{ fps}$)**: The computational throughput of the diffusion sampling pipeline.
2. **Native Motion FPS ($20.0\text{ fps}$)**: The temporal sampling rate of the HumanML3D motion dataset representation.
3. **Viewer Playback Rate ($30-60\text{ fps}$)**: The Three.js WebGL rendering refresh rate in the client browser.

Viser linearly or stepwise interpolates between the 20 FPS keyframes at the client display refresh rate, ensuring silky smooth visual playback despite the offline generation time.

---

## 5. Artifact Locations

- Raw JSON Telemetry: `artifacts/benchmarks/benchmark_results.json`
- Markdown Summary: `artifacts/benchmarks/benchmark_summary.md`
- Generated Sample: `artifacts/samples/sample_01/results.npy` (with `metadata.json`)
