# Pass 13 — Frozen Core Out-of-Sample Validation

**Domain:** temporal / causal reconstruction  
**Repository:** `MichaelWave369/chronolattice`  
**Base:** native `main` at `ce9d1061560bfed8cd0de4f8adf121c42e89c735`  
**Frozen candidate:** `parallax.core.candidate.v0`  
**Candidate SHA-256:** `7df6b6ed596862c5d0aad794039424d4487cdb1d3cb43d2a50ede548dda6f96e`

## Method

ChronoLattice was selected only after the Pass-12 candidate was frozen. This branch starts from native `main`, not the older Parallax interop branch.

No ChronoLattice product code is changed for Pass 13. The branch adds only:

- the exact frozen candidate fixture;
- a machine-readable mapping;
- tests against existing native APIs;
- an isolated PR-only CI workflow;
- this explanation.

If native behavior cannot satisfy one of the frozen seven primitives, the result should be recorded as a core-candidate failure rather than repaired by changing the theory mid-test.

## Out-of-sample mapping

| Frozen primitive | ChronoLattice native witness |
|---|---|
| P1 Native Authority | Native `ChronoEvent`, `ChronoReconstruction`, and `ChronoReceipt` remain authoritative; the test probe is read-only. |
| P2 Exact Subject Identity | `stable_hash`, `input_hash`, `reconstruction_hash`, `run_id`, and `receipt_id` deterministically bind subject state. |
| P3 Evidence / Truth Separation | The README explicitly says this version does not claim full physical simulation; reports advise review before trusting inferred continuity. |
| P4 Explicit Human Boundary | Missing bridge transitions are emitted as gaps/hints/recommendations; the engine does not insert inferred events into observed history. |
| P5 Authority Phase Separation | Reconstruction, contradiction/gap evidence, recommendations, and receipts are separate; generating a receipt performs no execution. |
| P6 Fail-Closed Transition | Unsupported schema/migration transitions raise errors rather than silently coercing artifacts. |
| P7 Immutable Receipt / Lineage | Native frozen dataclasses plus deterministic hashes preserve prior receipt identity when a later rerun changes. |

## What would falsify the candidate here

Any of the following is a Pass-13 failure:

1. the candidate fixture does not match the Pass-12 frozen hash;
2. observing conformance requires rewriting native input/state;
3. changed event state can retain the same bound identity/receipt;
4. reconstruction identity is treated as proof of factual physical truth;
5. inferred missing events are silently inserted as observed history;
6. a receipt/recommendation silently becomes permission or execution;
7. unsupported schema transitions continue silently;
8. later reruns rewrite prior receipt identity;
9. an eighth semantic primitive is required merely to explain safe native behavior.

## Claim boundary

A green result means the seven-principle candidate successfully predicts the tested safety/identity structure of this third domain without changing the candidate or product code.

It does **not**:

- prove ChronoLattice's scientific model is physically true;
- make ChronoLattice a canonical Parallax profile;
- make `parallax.core.candidate.v0` canonical;
- prove seven primitives are universally sufficient;
- authorize merge or release.
