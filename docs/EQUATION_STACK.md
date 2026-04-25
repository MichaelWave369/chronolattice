# ChronoLattice Equation Stack

## Master Reconstruction Equation
`Θ* = arg min_Θ [ L_obs + αL_geometry + βLcausality + γLentropy + δLenergy + εLmemory + ζLinfo + ηLcoherence ]`

## Geometry
`L_geometry` approximates inferred distance consistency over sequence, memory linkage, actor alignment, causal linkage, and information deltas.

## Causality
`L_causality` penalizes sequence-incompatible influence and timestamp inversions.

## Entropy
`L_entropy` models complexity from diversity of event types, actors, and memory references.

## Energy/Load
`L_energy` is represented by event-level energy deltas in v0.1 (no physical simulation).

## Information
`L_info` is the bounded average information_value across events.

## Memory
`L_memory` scores overlap and drift across shared memory references.

## Coherence
Global coherence is a weighted blend of causal, memory, geometry, entropy, information, and receipt fitness minus contradiction penalties.

## Reverse Reconstruction (Placeholder)
Phase 2 introduces reverse reconstruction operators for backward consistency checks and branch hypothesis search.


## Schema Stability Note
Equations remain stable across v0.1.x while artifact schemas evolve with explicit versioned envelopes for compatibility.
