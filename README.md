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


## Deterministic JSON Round Trips
Reconstruction outputs can be serialized to JSON, reloaded, and rehydrated into typed reconstruction models without losing structure.
Receipts can also be round-tripped through JSON deterministically.
Stable hashes protect replayability and auditability across runs.
This hardening prepares clean handoffs for future PhiOS visualization and SCE/SML adapter integrations.


## Artifact Compatibility
Reconstruction, receipt, and PhiOS payload files now use typed envelopes with `kind`, `schema_version`, and `payload`.
Legacy flat v0.1.1 reconstruction/receipt payloads still load for backwards compatibility.
Schema versioning prepares ChronoLattice for deterministic migrations across future releases.


## Schema Migration Readiness
v0.1.3 adds conservative migration utilities for future schema upgrades.
No real migrations are required yet because the current schema version is `0.1`.
Wrapped artifacts are migration-addressable via explicit envelopes.
Legacy flat payloads remain load-compatible, but are not migration-addressable without an envelope.


## Envelope Normalization
Legacy flat reconstruction and receipt JSON files can be promoted into wrapped artifacts with `kind`, `schema_version`, and `payload`.
Normalization does not alter payload content.
This helps older outputs participate cleanly in migration-status, migration, and artifact protocol workflows.


## Missing Bridge Event Detection
ChronoLattice can identify likely missing transition events when the timeline jumps across actor, memory, coherence, energy, information, geometry, provenance, or event-type continuity.

```bash
chronolattice reconstruct data/examples/missing_bridge_gap.json --out out/bridge_reconstruction.json
chronolattice bridge-gaps out/bridge_reconstruction.json
```


## Bridge Gap Calibration Profiles
ChronoLattice bridge detection supports deterministic threshold profiles:
- conservative — fewer bridge gaps, higher confidence
- balanced — default v0.2 behavior
- sensitive — more exploratory, catches smaller discontinuities
- phi_guardian — PHI/LAMBDA-inspired thresholds for PHI369 workflows

```bash
chronolattice bridge-profiles

chronolattice reconstruct data/examples/missing_bridge_gap.json \
  --bridge-profile sensitive \
  --out out/bridge_sensitive.json
```
