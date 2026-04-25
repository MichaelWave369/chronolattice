# ChronoLattice Master Spec (Concise)

## Definition
ChronoLattice v0.1 is a deterministic reconstruction framework that converts event traces into an analyzable lattice across causality, memory, geometry, information, and coherence.

## Laws
1. Prime Statement: ChronoLattice reconstructs the shape of time-space by studying the traces left by events.
2. Core Law: Reality is reconstructed as a lattice of causality, memory, motion, information, and coherence.
3. Determinism Law: Equal inputs + equal seed => equal reconstruction and hashes.

## Object Model
- ChronoConfig
- ChronoEvent
- CausalEdge
- MemoryEdge
- GeometryEdge
- ChronoContradiction
- ChronoReconstruction
- ChronoReceipt

## Runtime Stack
1. Input normalization
2. Stable hashing
3. Causal graph construction
4. Memory graph construction
5. Geometry edge inference
6. Contradiction detection
7. Entropy/information scoring
8. Coherence scoring and stability decision
9. Receipt emission and PhiOS payload projection

## PHI369 Ecosystem Map
- **ChronoLattice**: deterministic reconstruction and scoring core
- **PhiCompute**: compute/orchestration execution layer
- **PhiOS**: visualization and operator-facing payload consumers
- **SCE/SML adapters**: source schema bridges (stubbed in v0.1)

## Roadmap
See `docs/ROADMAP.md`.


## Artifact Compatibility Note
ChronoLattice artifacts should be treated as versioned protocol objects.
Any future schema changes must include explicit migration tests.

Legacy artifacts may be normalized into envelopes before migration.
Normalization wraps the payload but does not rewrite reconstruction meaning.


## Missing Bridge Event Detection
- **Definition:** Identify probable missing transition events when adjacent or strongly related traces show unexplained discontinuity.
- **Gap Types:** actor_discontinuity, memory_discontinuity, coherence_drop, energy_jump, information_jump, geometry_causal_tension, event_type_jump, provenance_gap.
- **Scoring:** Deterministic per-gap score in [0,1] with threshold gating and severity classes for explainable penalties.
- **Why this matters:** Supports reverse reconstruction by surfacing plausible bridge hypotheses without fabricating events.


### Bridge Calibration Profiles
Bridge gap detection supports named deterministic profiles (`conservative`, `balanced`, `sensitive`, `phi_guardian`) that set continuity thresholds without changing model semantics.
Profiles allow controlled sensitivity tuning while preserving deterministic replayability.


- Profile mode for common deterministic presets.
- Manual mode for explicit operator threshold control.
