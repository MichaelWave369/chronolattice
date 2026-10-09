export const EXAMPLES = [
  { id: 'simple_timeline', name: 'Simple timeline', tag: 'BASELINE', summary: 'Three observations across a sensor lineage.' },
  { id: 'missing_bridge_gap', name: 'Missing bridge gap', tag: 'DISCONTINUITY', summary: 'An idea, a commit, and a handoff with missing transitions.' },
  { id: 'causal_loop', name: 'Causal inversion', tag: 'TIME ORDER', summary: 'Recorded sequence order clashes with timestamps.' },
  { id: 'coherence_collapse', name: 'Coherence collapse', tag: 'INSTABILITY', summary: 'Descending timestamps and weak event-level coherence.' },
  { id: 'memory_orphan', name: 'Memory orphan', tag: 'MEMORY', summary: 'A memory reference whose provenance is incomplete.' }
];

export function normalizeDocument(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) throw new Error('Expected a ChronoLattice JSON object.');
  const wrapped = typeof input.kind === 'string';
  const raw = wrapped ? input.payload : input;
  if (wrapped && input.kind !== 'chronolattice.reconstruction') {
    throw new Error('Import a raw event timeline or a ChronoLattice reconstruction artifact. This viewer does not graph ' + input.kind + '.');
  }
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) throw new Error('Missing reconstruction payload object.');
  if (!Array.isArray(raw.events)) throw new Error('The artifact needs an events array.');
  if (!raw.events.length) throw new Error('The timeline has no events to display.');
  if (raw.events.length > 200) throw new Error('The viewer supports up to 200 events at once. Export a smaller trace.');
  const ids = new Set();
  const events = raw.events.map((e, index) => {
    if (!e || typeof e !== 'object' || typeof e.event_id !== 'string' || !e.event_id ||
        typeof e.actor !== 'string' || typeof e.timestamp !== 'string' ||
        typeof e.event_type !== 'string' || !Number.isFinite(Number(e.sequence_index)) ||
        !Array.isArray(e.memory_refs)) throw new Error('Invalid event at index ' + index + ': event_id, actor, timestamp, sequence_index, event_type, and memory_refs are required.');
    if (ids.has(e.event_id)) throw new Error('Duplicate event_id ' + e.event_id + '.');
    ids.add(e.event_id);
    return {...e, sequence_index:Number(e.sequence_index)};
  }).sort((a,b) => a.sequence_index - b.sequence_index || a.event_id.localeCompare(b.event_id));
  const isRecon = !!(raw.reconstruction_hash && Array.isArray(raw.causal_edges) && Array.isArray(raw.memory_edges));
  if (wrapped && !isRecon) throw new Error('This reconstruction envelope is missing required engine output fields.');
  const safeArray = field => Array.isArray(raw[field]) ? raw[field] : [];
  const causalEdges = isRecon ? safeArray('causal_edges').filter(edge => ids.has(edge.source_event_id) && ids.has(edge.target_event_id)) : [];
  const memoryEdges = isRecon ? safeArray('memory_edges').filter(edge => ids.has(edge.source_event_id) && ids.has(edge.target_event_id)) : [];
  const geometryEdges = isRecon ? safeArray('geometry_edges') : [];
  const bridges = isRecon ? safeArray('bridge_gaps') : [];
  const contradictions = isRecon ? safeArray('contradictions') : [];
  const sequenceLinks = !isRecon ? events.slice(1).map((e,i) => ({source_event_id:events[i].event_id,target_event_id:e.event_id})) : [];
  const memoryHints = !isRecon ? events.flatMap((a,i) => events.slice(i+1).filter(b =>
    a.memory_refs.some(m => typeof m === 'string' && b.memory_refs.includes(m))
  ).map(b => ({source_event_id:a.event_id,target_event_id:b.event_id,
    shared_refs:a.memory_refs.filter(m=>typeof m==='string' && b.memory_refs.includes(m))}))) : [];
  const timeInversions = events.slice(1).filter((e,i)=>{
    const before=Date.parse(events[i].timestamp), after=Date.parse(e.timestamp);
    return Number.isFinite(before) && Number.isFinite(after) && after < before;
  }).length;
  return {
    kind: isRecon ? 'reconstruction' : 'raw',
    wrapped, schemaVersion: wrapped ? input.schema_version || 'unspecified' : null,
    runId: String(raw.run_id || 'unspecified'),
    seed: raw.seed,
    events, causalEdges, memoryEdges, geometryEdges, bridges, contradictions, sequenceLinks, memoryHints, timeInversions,
    coherence: isRecon && Number.isFinite(raw.coherence) ? raw.coherence : null,
    entropy: isRecon && Number.isFinite(raw.entropy_score) ? raw.entropy_score : null,
    information: isRecon && Number.isFinite(raw.information_score) ? raw.information_score : null,
    stable: isRecon && typeof raw.stable === 'boolean' ? raw.stable : null,
    reconstructionHash: isRecon ? raw.reconstruction_hash : null,
    bridgeProfile: isRecon ? raw.bridge_profile || 'not supplied' : null,
    thresholds: isRecon ? raw.bridge_thresholds || {} : null,
    thresholdProvenance: isRecon ? raw.bridge_threshold_provenance || {} : null
  };
}

export function formatMetric(value) {
  return typeof value === 'number' && Number.isFinite(value) ? value.toFixed(3) : '—';
}

export function makeGraph(document) {
  const events = document.events;
  const actors = [...new Set(events.map(e=>e.actor))];
  const width = Math.max(900,events.length * 144 + 200);
  const height = Math.max(340,actors.length * 90 + 160);
  const usable = width-180;
  const positions = Object.fromEntries(events.map((event,i) => [event.event_id,{
    x: 100 + (events.length === 1 ? usable / 2 : i*usable/(events.length-1)),
    y: 124 + actors.indexOf(event.actor)*90
  }]));
  return {actors,width,height,positions};
}

export function displayTime(iso) {
  const d=new Date(iso);
  return !Number.isNaN(d.valueOf()) ? d.toISOString().replace('T',' ').replace('.000Z',' UTC') : iso;
}
