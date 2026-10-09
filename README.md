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


## Manual Bridge Threshold Mode
ChronoLattice supports two threshold modes:
- profile mode: use named calibration profiles
- manual mode: use explicit threshold values

```bash
chronolattice reconstruct data/examples/missing_bridge_gap.json \
  --bridge-profile sensitive \
  --out out/bridge_sensitive.json

chronolattice reconstruct data/examples/missing_bridge_gap.json \
  --bridge-threshold-mode manual \
  --bridge-gap-threshold 0.75 \
  --coherence-drop-threshold 0.30 \
  --energy-jump-threshold 0.80 \
  --information-jump-threshold 0.70 \
  --out out/bridge_manual.json
```

## Threshold Provenance
ChronoLattice records where each effective bridge threshold came from:
- profile preset
- CLI manual override
- manual default
- programmatic config

## Bridge Gap Reports
Bridge Gap Reports summarize missing transition evidence across:
- severity
- gap type
- affected actors
- suggested missing event types
- threshold metadata
- operator recommendations

```bash
chronolattice reconstruct data/examples/missing_bridge_gap.json \
  --bridge-profile sensitive \
  --out out/bridge_sensitive.json

chronolattice bridge-report out/bridge_sensitive.json \
  --out out/bridge_report.json
```


## Public React lattice explorer

After merging the website pull request and enabling **Settings → Pages → Build and deployment → GitHub Actions**, the public site is available at:

https://michaelwave369.github.io/chronolattice/

The site is a static React/Vite **visualization companion**, not a Python runtime. It renders the project's five sample event streams, browses event properties, and displays imported ChronoLattice reconstruction artifacts with their actual causal/memory edges, contradictions, bridge gaps, and coherence metrics. For raw event inputs, displayed edges are explicitly **sequence/memory visualization hints**, not engine-derived inferences. Imported data never leaves the browser; the site does not verify hashes or run reconstructions, simulations, bridge detection, or deterministic receipts.

### Run the website locally

    cd web
    npm install
    npm run dev

### Make a real reconstruction to import

    python -m pip install -e ".[dev]"
    chronolattice reconstruct data/examples/missing_bridge_gap.json --out out/bridge_reconstruction.json
    chronolattice receipt out/bridge_reconstruction.json --out out/bridge_receipt.json
    chronolattice bridge-report out/bridge_reconstruction.json --out out/bridge_report.json

Import the reconstruction JSON into the site's Lattice View. Raw example traces also work as visualization inputs. Only the Python engine produces authoritative project calculations and versioned artifacts. Receipt hash fields are shown as imported data, not verified client-side.

### Publish the site

1. Merge the website pull request into `main`.
2. Go to repository **Settings → Pages → Build and deployment** and choose **GitHub Actions**.
3. The Pages workflow builds `web/` on pushes affecting it, and can also be started manually from Actions.
4. Open https://michaelwave369.github.io/chronolattice/ once the deploy succeeds.

## License

MIT. See [LICENSE](LICENSE).
