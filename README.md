# ChronoLattice v0.1
**Sovereign Time-Space Reconstruction Framework**

**Prime statement:** ChronoLattice reconstructs the shape of time-space by studying the traces left by events.

**Core law:** Reality is reconstructed as a lattice of causality, memory, motion, information, and coherence.

ChronoLattice v0.1 is a deterministic, auditable, local-first reconstruction engine. It ingests event traces, builds relationship lattices, scores coherence, detects contradictions, and emits deterministic receipts. It does **not** claim full physical simulation in this version.

## Principles
- Deterministic execution (seeded; default seed `369369`)
- Auditable hashes and receipts
- Local-first operation
- No external services
- Stability threshold: `C* = φ/2 ≈ 0.809017`

## Core Equation
`Θ* = arg min_Θ [ L_obs + αL_geometry + βLcausality + γLentropy + δLenergy + εLmemory + ζLinfo + ηLcoherence ]`

## Install and Development
```bash
python -m pip install -e ".[dev]"
pytest -q
chronolattice version
chronolattice reconstruct data/examples/simple_timeline.json --out out/reconstruction.json
```

## CLI Commands
- `chronolattice version`
- `chronolattice validate PATH`
- `chronolattice reconstruct PATH --seed 369369 --out OUT`
- `chronolattice receipt RECONSTRUCTION_PATH --out OUT`
- `chronolattice phios-payload RECONSTRUCTION_PATH --out OUT`
- `chronolattice inspect RECONSTRUCTION_PATH`
- `chronolattice contradictions RECONSTRUCTION_PATH`

## Naming
This layer uses **PhiCompute** for orchestration references. **PhiKernel** is reserved for lower-level sovereign substrate layers.
