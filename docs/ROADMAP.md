# ChronoLattice Roadmap

- **v0.1 — Initialized (Deterministic Core)**
  - Base deterministic reconstruction core
  - Causality/memory/geometry/information/entropy/coherence scoring
  - CLI + examples + tests

- **v0.1.1 — Hardening**
  - JSON schema validation
  - Reconstruction serialization
  - Receipt round-trip tests
  - CLI read/write hardening

- **Phase 2 — Reverse Reconstruction**
- **Phase 3 — PhiOS Visualization**
- **Phase 4 — SCE/SML Adapters**
- **Phase 5 — Simulation & Prediction**

- **v0.1.2 — Artifact Compatibility**
  - Typed artifact envelopes
  - Schema version compatibility checks
  - Legacy flat payload loading
  - Wrapped CLI output

- **v0.1.3 — Migration Readiness**
  - Migration utility stubs
  - `migration-status` CLI command
  - Optional `migrate` CLI command
  - Future schema upgrade pathway

- **v0.1.4 — Envelope Normalization**
  - Legacy artifact kind detection
  - Envelope normalization
  - `normalize-envelope` CLI command
  - Flat-to-wrapped artifact promotion

- **v0.2.0 — Missing Bridge Event Detection**
  - ChronoBridgeGap model
  - Deterministic bridge gap detection
  - Coherence penalty integration
  - `bridge-gaps` CLI command
  - PhiOS bridge gap payload support

- **v0.2.1 — Bridge Calibration Profiles**
  - Bridge calibration profiles
  - Profile-aware CLI reconstruction
  - `bridge-profiles` command
  - Profile metadata in reconstruction/PhiOS payload

- **v0.2.2 — Manual Bridge Threshold Overrides**
  - `bridge_threshold_mode`
  - Manual threshold CLI flags
  - Effective threshold metadata in reconstruction/PhiOS payload
  - Profile/manual resolution tests

- **v0.2.3 — Threshold Provenance Metadata**
  - `bridge_threshold_provenance` metadata
  - CLI partial manual override provenance
  - PhiOS provenance payload support
  - Schema/serialization compatibility tests

- **v0.2.4 — Bridge Gap Reports**
  - Bridge report builder
  - `bridge-report` CLI command
  - Wrapped bridge report artifact
  - PhiOS report summary
  - Bridge report schema validation
