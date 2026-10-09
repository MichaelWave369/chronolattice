import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { displayTime, EXAMPLES, formatMetric, makeGraph, normalizeDocument } from './chronodata.js';
import './styles.css';

const REPO = 'https://github.com/MichaelWave369/chronolattice';
const threshold = 0.8090169943749475;
const sampleURL = id => import.meta.env.BASE_URL + 'examples/' + id + '.json';
const pretty = s => String(s || 'none').replaceAll('_',' ');
const shortened = s => String(s || '').length > 30 ? String(s).slice(0,16)+'…'+String(s).slice(-9) : String(s||'—');
const formatNumber = n => typeof n === 'number' && Number.isFinite(n) ? String(Math.round(n*1000)/1000) : '—';
const palette = ['#9ae7df','#d6b4ff','#ffd5a0','#b0dca9','#ff9ea9','#b7c5f5','#aee7a3','#ecaaef'];
const linkPositions = (graph,e) => {
  const a=graph.positions[e.source_event_id], b=graph.positions[e.target_event_id];
  if(!a||!b)return null;
  return {a,b};
};

function Icon({name,size=18}) {
  const paths={
    git:<><circle cx="6" cy="4" r="2"/><circle cx="6" cy="20" r="2"/><circle cx="18" cy="6" r="2"/><path d="M6 6v12M6 12c0-4 4-6 10-6"/></>,
    upload:<><path d="M12 16V3m-5 5 5-5 5 5"/><path d="M4 16v4h16v-4"/></>,
    arrow:<path d="M5 12h14m-6-6 6 6-6 6"/>,
    settings:<><circle cx="12" cy="12" r="3"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3M4.9 4.9l2.1 2.1m10 10 2.1 2.1M19.1 4.9 17 7M7 17l-2.1 2.1"/></>,
    layers:<><path d="m12 3 9 5-9 5-9-5 9-5Zm-9 9 9 5 9-5M3 16l9 5 9-5"/></>,
    clock:<><circle cx="12" cy="12" r="9"/><path d="M12 7v5l4 3"/></>,
    check:<path d="m5 12 4 4L19 6"/>,
    alert:<><path d="m12 3 10 18H2L12 3Z"/><path d="M12 9v5m0 3v.2"/></>,
    brain:<><path d="M12 4C9 1 4 4 4 8c-3 2-2 7 1 8-1 4 5 7 7 3V4Zm0 0c3-3 8 0 8 4 3 2 2 7-1 8 1 4-5 7-7 3V4Z"/></>
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]||paths.layers}</svg>;
}

function LatticeGraph({data,selected,onSelect,layers,actorFilter}) {
  const graph=useMemo(()=>makeGraph(data),[data]);
  const causal = data.kind==='reconstruction' ? data.causalEdges : data.sequenceLinks;
  const memory = data.kind==='reconstruction' ? data.memoryEdges : data.memoryHints;
  const indexed=Object.fromEntries(data.events.map((e,i)=>[e.event_id,i]));
  const active=id=>!actorFilter||data.events.some(e=>e.event_id===id && e.actor===actorFilter);
  const linkPath=(link,high=false)=>{
    const p=linkPositions(graph,link);
    if(!p)return '';
    const {a,b}=p;
    if(!high)return 'M '+a.x+' '+a.y+' Q '+(a.x+b.x)/2+' '+(Math.min(a.y,b.y)-32)+' '+b.x+' '+b.y;
    return 'M '+a.x+' '+a.y+' Q '+(a.x+b.x)/2+' '+(Math.max(a.y,b.y)+55)+' '+b.x+' '+b.y;
  };
  return <div className="graph-scroll" role="region" aria-label="Lattice event visualization, scroll horizontally to explore" tabIndex={0}>
    <svg width={graph.width} height={graph.height} viewBox={'0 0 '+graph.width+' '+graph.height} role="img" aria-label="Event nodes arranged by sequence index horizontally and actor vertically. Select an event below to see its details.">
      <defs>
        <pattern id="dotgrid" x="0" y="0" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1.2" cy="1.2" r=".65" fill="#31505c" opacity=".65"/></pattern>
        <marker id="arrowCausal" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="none" stroke="#7de2cf" strokeWidth="1.2"/></marker>
      </defs>
      <rect width={graph.width} height={graph.height} fill="url(#dotgrid)"/>
      <text x="28" y="29" className="svgmeta">SEQUENCE INDEX →</text>
      <text x={graph.width-26} y="29" textAnchor="end" className="svgmeta">ACTOR LANES / EVENT TRACES</text>
      {graph.actors.map((actor,i)=><g key={actor}>
        <line x1="38" x2={graph.width-38} y1={124+i*90} y2={124+i*90} stroke="#22404d" strokeDasharray="5 10"/>
        <text x="34" y={104+i*90} className="svglane">{actor.toUpperCase()}</text>
      </g>)}
      {layers.causal && causal.map((edge,i)=>{
        const faded=(actorFilter&&!active(edge.source_event_id)&&!active(edge.target_event_id));
        return <path key={'causal'+i} d={linkPath(edge)}
          fill="none" stroke={data.kind==='raw'?'#677f9e':'#7de2cf'} strokeWidth={selected&&(selected===edge.source_event_id||selected===edge.target_event_id)?2.8:1.6}
          strokeDasharray={data.kind==='raw'?'5 6':edge.allowed===false?'4 7':''}
          markerEnd={data.kind==='reconstruction'?'url(#arrowCausal)':undefined}
          opacity={faded ? 0.15 : 0.7}/>;
      })}
      {layers.memory && memory.map((edge,i)=><path key={'memory'+i} d={linkPath(edge,true)} fill="none" stroke="#b595f8" strokeWidth="1.55" strokeDasharray="3 5"
         opacity={actorFilter && !active(edge.source_event_id) && !active(edge.target_event_id) ? 0.12 : 0.67}/>)}
      {data.events.map((e,i)=>{
        const p=graph.positions[e.event_id], current=selected===e.event_id;
        const color=palette[graph.actors.indexOf(e.actor)%palette.length];
        return <g key={e.event_id} className="svgnode" role="button" tabIndex={0} aria-label={'Inspect event '+e.event_id+' by '+e.actor} onClick={()=>onSelect(e.event_id)} onKeyDown={ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();onSelect(e.event_id);}}}
          opacity={actorFilter && actorFilter !== e.actor ? 0.23 : 1}>
          {current&&<circle cx={p.x} cy={p.y} r="31" fill="none" stroke={color} strokeWidth="1" opacity=".38"/>}
          <circle cx={p.x} cy={p.y} r={current?17:13} fill="#0b1b2a" stroke={color} strokeWidth={current?3:2}/>
          <circle cx={p.x} cy={p.y} r="4" fill={color}/>
          <text x={p.x} y={p.y-25} textAnchor="middle" className="svgevent">{e.event_id}</text>
          <text x={p.x} y={p.y+35} textAnchor="middle" className="svgtype">{e.event_type}</text>
          <text x={p.x} y={p.y+49} textAnchor="middle" className="svgseq">#{e.sequence_index}</text>
        </g>;
      })}
      <text x="26" y={graph.height-17} className="svgmeta">NODES: {data.events.length} · {data.kind==='raw'?'DISPLAY LINKS ONLY':'IMPORTED ENGINE EDGES'}</text>
    </svg>
  </div>;
}

function EventDetails({event,data}) {
  if(!event)return <div className="empty-detail">Choose an event from the lattice to examine its trace.</div>;
  const links=data.kind==='reconstruction' ? data.causalEdges : data.sequenceLinks;
  const adjacent=links.filter(e=>e.source_event_id===event.event_id||e.target_event_id===event.event_id);
  const related=data.bridges.filter(g=>g.source_event_id===event.event_id||g.target_event_id===event.event_id);
  return <div className="inspect">
    <div className="inspector-head"><span className="tiny">SELECTED EVENT</span><span className="corner">EVENT / {String(event.sequence_index).padStart(3,'0')}</span></div>
    <h2>{event.event_id}</h2><p className="inspector-sub">{event.event_type} <span>·</span> {event.actor}</p>
    <div className="fields">
      <div><span>TIMESTAMP</span><strong>{displayTime(event.timestamp)}</strong></div>
      <div><span>ENERGY Δ</span><strong>{formatNumber(event.energy_delta)}</strong></div>
      <div><span>INFORMATION</span><strong>{formatNumber(event.information_value)}</strong></div>
      <div><span>EVENT COHERENCE</span><strong>{formatNumber(event.coherence)}</strong></div>
      <div><span>PAYLOAD HASH / LABEL</span><strong title={event.payload_hash||''} className="breakword">{shortened(event.payload_hash)}</strong></div>
      <div><span>ADJACENT {data.kind==='raw'?'SEQUENCE LINKS':'CAUSAL EDGES'}</span><strong>{adjacent.length}</strong></div>
    </div>
    <div className="detail-title">MEMORY REFERENCES</div>
    <div className="chips">{event.memory_refs?.length?event.memory_refs.map((m,i)=><span key={i}>{m}</span>):<span className="muted">No references</span>}</div>
    <div className="detail-title">PROVENANCE</div>
    {event.provenance&&Object.keys(event.provenance).length?<div className="provenance">{Object.entries(event.provenance).map(([k,v])=><div key={k}><span>{k}</span><strong>{String(v)}</strong></div>)}</div>:<p className="muted">No provenance fields present.</p>}
    {data.kind==='reconstruction'&&related.length>0&&<><div className="detail-title">IMPORTED BRIDGE GAPS</div>{related.map((g,i)=><div className="gapmini" key={g.gap_id||i}><strong>{pretty(g.gap_type)}</strong><span>{pretty(g.severity)} · {formatMetric(g.score)}</span></div>)}</>}
  </div>;
}

function App() {
  const [sample,setSample]=useState('missing_bridge_gap');
  const [doc,setDoc]=useState(null);
  const [source,setSource]=useState('REPOSITORY EXAMPLE');
  const [loadErr,setLoadErr]=useState('');
  const [selected,setSelected]=useState(null);
  const [tab,setTab]=useState('lattice');
  const [layers,setLayers]=useState({causal:true,memory:true});
  const [actorFilter,setActorFilter]=useState('');
  const [notice,setNotice]=useState('');
  const [fileInputKey,setFileInputKey]=useState(0);
  const isDemo=source==='REPOSITORY EXAMPLE';

  async function chooseExample(id){
    if(!EXAMPLES.some(x=>x.id===id))return;
    setSample(id);setLoadErr('');setNotice('');setActorFilter('');
    try{
      const res=await fetch(sampleURL(id));
      if(!res.ok)throw new Error('Example unavailable: '+res.status);
      const body=await res.json();
      const normalized=normalizeDocument(body);
      setDoc(normalized);setSelected(normalized.events[0]?.event_id||null);setSource('REPOSITORY EXAMPLE');setTab('lattice');
    }catch(err){setLoadErr(String(err.message||err));setDoc(null);}
  }
  useEffect(()=>{chooseExample('missing_bridge_gap');},[]);
  async function importFile(event) {
    const file=event.target.files?.[0];if(!file)return;
    setLoadErr('');setNotice('');
    try{
      if(file.size>4*1024*1024)throw new Error('JSON viewer limit: 4 MB per file.');
      const body=JSON.parse(await file.text());
      const normalized=normalizeDocument(body);
      setDoc(normalized);setSource('LOCAL JSON / '+file.name);setSelected(normalized.events[0]?.event_id||null);setActorFilter('');setSample('');setTab('lattice');
      setNotice('Loaded locally. No bytes were uploaded and no hashes have been verified.');
    }catch(err){setLoadErr(String(err.message||err));}
    finally{setFileInputKey(x=>x+1);}
  }
  const actors=doc?[...new Set(doc.events.map(e=>e.actor))]:[];
  const event=doc?.events.find(e=>e.event_id===selected)||doc?.events[0];
  const imported=doc?.kind==='reconstruction';
  const totalLinks=doc ? (imported?doc.causalEdges.length:doc.sequenceLinks.length) : 0;
  const memoryLinks=doc ? (imported?doc.memoryEdges.length:doc.memoryHints.length) : 0;
  return <div className="site">
    <div className="top"><div><span className="pulse"/> <span>ENTER THE FIELD</span><span className="topdivider">/</span><span>CHRONOLATTICE</span></div><div>LOCAL-FIRST RECONSTRUCTION <span className="topdivider">·</span> PUBLIC VIEW</div></div>
    <header className="hero">
      <div className="hero-text">
        <div className="eyebrow"><span className="line"/> SOVEREIGN TIME-SPACE RECONSTRUCTION</div>
        <h1>CHRONO<span>LATTICE</span><i>.</i></h1>
        <p className="hero-desc">Reconstruct the shape of events through <em>causality</em>, <em>memory</em>, and <em>coherence</em>.</p>
        <div className="hero-actions">
          <a className="action-primary" href="#workbench">EXPLORE THE LATTICE <Icon name="arrow" size={17}/></a>
          <a className="action-secondary" href={REPO} target="_blank" rel="noreferrer"><Icon name="git"/> VIEW SOURCE ↗</a>
        </div>
        <p className="prime">PRIME STATEMENT / Study the traces left behind by events.</p>
      </div>
      <div className="hero-visual" aria-hidden="true">
        <svg viewBox="0 0 430 325" width="100%" height="100%">
          <defs><radialGradient id="orbglow"><stop stopColor="#163454" stopOpacity="0.75"/><stop offset="1" stopColor="#081221" stopOpacity="0"/></radialGradient></defs>
          <circle cx="216" cy="160" r="154" fill="url(#orbglow)"/>
          {[40,82,121].map(r=><ellipse key={r} cx="216" cy="160" rx={r+40} ry={r} stroke="#43758a" strokeOpacity=".35" fill="none" transform={'rotate('+(r*.5)+' 216 160)'}/>)}
          {[[60,224],[111,93],[184,166],[251,68],[316,164],[367,92],[350,252],[236,265],[138,287],[81,172]].map(([x,y],i)=>{
            const nxt=[[111,93],[184,166],[251,68],[316,164],[367,92],[350,252],[236,265],[138,287],[81,172],[60,224]][i];
            return <line key={i} x1={x} y1={y} x2={nxt[0]} y2={nxt[1]} stroke="#5e9bba" strokeOpacity=".5"/>;
          })}
          {[[60,224],[111,93],[184,166],[251,68],[316,164],[367,92],[350,252],[236,265],[138,287],[81,172]].map(([x,y],i)=><g key={i}><circle cx={x} cy={y} r={i===2||i===4?8:4} stroke={i===2?'#eac49b':'#76cbd5'} strokeWidth="1.5" fill="#0a2034"/><circle cx={x} cy={y} r="1.5" fill="#a4dfea"/></g>)}
          <path d="M60 224L184 166L316 164L350 252L236 265L138 287L111 93L251 68L367 92" fill="none" stroke="#d9af8e" strokeOpacity=".23" strokeDasharray="3 8"/>
          <text x="175" y="191" fill="#aac9d8" fontFamily="monospace" fontSize="10">T →</text>
        </svg>
        <span>CAUSALITY · MEMORY · GEOMETRY</span>
      </div>
    </header>
    <section className="banner"><span><Icon name="alert" size={17}/> STATIC VISUAL EXPLORER</span><p>This browser displays example traces and imported engine results. It does not run ChronoLattice reconstruction, bridge detection, or receipt verification.</p></section>
    <div id="workbench" className="workspace">
      <div className="workspace-intro">
        <div><span className="eyebrow">01 / EVENT RECONSTRUCTION CONSOLE</span><h2>Explore the event field<span>.</span></h2><p>Choose a real repository fixture or inspect a reconstruction exported by the Python CLI.</p></div>
        <a href={REPO+'/blob/main/docs/MASTER_SPEC.md'} target="_blank" rel="noreferrer">READ THE MASTER SPEC ↗</a>
      </div>
      <div className="console">
        <div className="console-top">
          <div className="console-switch">
            <span className="console-indicator"/>
            <span>RESEARCH CONSOLE / {doc?.runId||'LOADING'}</span>
          </div>
          <div className="console-status"><span>{isDemo?'DEMONSTRATION DATA':'IMPORTED DATA'}</span><span>{doc?.kind==='reconstruction'?'ENGINE OUTPUT':'RAW TRACE'}</span><span>SEED {String(doc?.seed||369369)}</span></div>
        </div>
        <div className="source-bar">
          <div className="selectwrap">
            <label htmlFor="fixture">EXAMPLE SCENARIO</label>
            <select id="fixture" value={sample} onChange={e=>chooseExample(e.target.value)}>
              {!sample&&<option value="">CUSTOM IMPORT ACTIVE</option>}
              {EXAMPLES.map(item=><option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
          </div>
          <span className="or">OR</span>
          <label className="upload-button"><Icon name="upload" size={16}/> IMPORT JSON<input key={fileInputKey} type="file" accept=".json,application/json" onChange={importFile}/></label>
          <div className="source-label" title={source}>SOURCE: {source}</div>
        </div>
        {(loadErr||notice)&&<div role={loadErr?'alert':'status'} className={loadErr?'load-error':'load-notice'}>{loadErr||notice}</div>}
        {doc&&<div className="stat-strip">
          <div><span>EVENTS</span><strong>{doc.events.length}</strong><small>OBSERVED TRACES</small></div>
          <div><span>CAUSAL {imported?'EDGES':'HINTS'}</span><strong>{totalLinks}</strong><small>{imported?'ENGINE OUTPUT':'SEQUENCE DISPLAY'}</small></div>
          <div><span>MEMORY {imported?'EDGES':'HINTS'}</span><strong>{memoryLinks}</strong><small>{imported?'ENGINE OUTPUT':'SHARED REFERENCES'}</small></div>
          <div><span>BRIDGE GAPS</span><strong>{imported?doc.bridges.length:'—'}</strong><small>{imported?'ENGINE OUTPUT':'NOT COMPUTED'}</small></div>
          <div><span>GLOBAL COHERENCE</span><strong className={imported&&doc.stable?'mint':''}>{formatMetric(doc.coherence)}</strong><small>{imported?'ENGINE SCORE':'NOT COMPUTED'}</small></div>
        </div>}
        <nav className="console-tabs" aria-label="Explorer panels">
          {[['lattice','LATTICE VIEW'],['events','EVENT STREAM'],['findings','FINDINGS'],['protocol','PROTOCOL']].map(([id,name])=>
            <button key={id} className={tab===id?'selected':''} onClick={()=>setTab(id)}>{name}</button>)}
        </nav>
        {!doc?<div className="loading">Loading scenario data…</div>:tab==='lattice'?<div className="lattice-pane">
          <div className="viz-top">
            <div><span className="sectionlabel">TEMPORAL LATTICE / INTERACTIVE VIEW</span><p>{imported?'Edges and statuses imported from reconstruction artifact.':'Lines are browser visualization hints, not detected causality or missing bridges.'}</p></div>
            <div className="toggle-buttons">
              <button className={layers.causal?'on':''} onClick={()=>setLayers(v=>({...v,causal:!v.causal}))} aria-pressed={layers.causal}><span className="dot cyan"/> {imported?'CAUSAL':'SEQUENCE'}</button>
              <button className={layers.memory?'on':''} onClick={()=>setLayers(v=>({...v,memory:!v.memory}))} aria-pressed={layers.memory}><span className="dot purple"/> MEMORY</button>
            </div>
          </div>
          <div className="viz-body"><LatticeGraph data={doc} selected={event?.event_id} onSelect={setSelected} layers={layers} actorFilter={actorFilter}/></div>
          <div className="lattice-bottom">
            <div className="event-list">
              <div className="sectionlabel">EVENT INDEX <span>{doc.events.length} NODES</span></div>
              <div className="filter-row"><label htmlFor="actorfilter">ACTOR</label><select id="actorfilter" value={actorFilter} onChange={e=>setActorFilter(e.target.value)}><option value="">ALL ACTORS</option>{actors.map(a=><option key={a} value={a}>{a}</option>)}</select></div>
              <div className="event-scroll">{doc.events.filter(e=>!actorFilter||e.actor===actorFilter).map(e=><button key={e.event_id} className={e.event_id===event?.event_id?'event-option current':'event-option'} onClick={()=>setSelected(e.event_id)}>
                <span className="e-num">{String(e.sequence_index).padStart(2,'0')}</span><span className="e-label"><strong>{e.event_id}</strong><small>{e.actor} / {e.event_type}</small></span><span>↗</span>
              </button>)}</div>
            </div>
            <EventDetails data={doc} event={event}/>
          </div>
        </div>:tab==='events'?<div className="table-pane">
          <div className="sectionlabel">EVENT STREAM <span>SORTED BY SEQUENCE INDEX</span></div>
          <div className="table-scroll"><table><thead><tr><th>SEQ</th><th>ID</th><th>TIME (RECORDED)</th><th>ACTOR</th><th>TYPE</th><th>COHERENCE</th><th>MEMORY REFS</th></tr></thead>
            <tbody>{doc.events.map(e=><tr key={e.event_id} className={e.event_id===event?.event_id?'marked':''} onClick={()=>{setSelected(e.event_id);setTab('lattice');}} title="Click to inspect in lattice view">
              <td>{e.sequence_index}</td><td>{e.event_id}</td><td>{displayTime(e.timestamp)}</td><td>{e.actor}</td><td>{e.event_type}</td><td>{formatMetric(e.coherence)}</td><td>{e.memory_refs.join(', ')||'—'}</td>
            </tr>)}</tbody></table></div>
          <p className="table-foot">This is a trace view. Time ordering is presented as recorded, without assuming the reconstruction proves physical chronology.</p>
        </div>:tab==='findings'?<div className="findings-pane">
          <div className="sectionlabel">FINDINGS & EXCEPTIONS <span>{imported?'FROM IMPORTED RECONSTRUCTION':'RAW EVENT INSPECTION'}</span></div>
          {!imported?<div className="finding-notice">
            <Icon name="alert" size={25}/><div><h3>Engine diagnostics are not available.</h3><p>Raw traces do not include computed bridge gaps, contradictions, or a global coherence result. Run the ChronoLattice Python CLI and import the reconstruction artifact to inspect actual findings here.</p>
              <p><strong>Visualization cue:</strong> {doc.timeInversions} adjacent timestamp inversion(s) in sequence order. This simple display-only check is not an engine contradiction verdict.</p>
            </div>
          </div>:<>
            <div className="finding-stats">
              <div><span>RECONSTRUCTION COHERENCE</span><strong>{formatMetric(doc.coherence)}</strong><small>THRESHOLD C* = {formatMetric(threshold)} · {doc.stable===true?'STABLE':doc.stable===false?'BELOW THRESHOLD':'NOT PROVIDED'}</small></div>
              <div><span>CONTRADICTIONS</span><strong>{doc.contradictions.length}</strong><small>RECORDED BY ENGINE</small></div>
              <div><span>BRIDGE GAPS</span><strong>{doc.bridges.length}</strong><small>PROFILE: {doc.bridgeProfile}</small></div>
              <div><span>ENTROPY / INFO</span><strong className="two-metrics">{formatMetric(doc.entropy)} <i>/</i> {formatMetric(doc.information)}</strong><small>ENGINE SCORES</small></div>
            </div>
            <div className="finding-split">
              <div><h3>Bridge gap evidence</h3>{doc.bridges.length ? doc.bridges.map((g,i)=><article key={g.gap_id||i} className="finding">
                <div className="finding-heading"><strong>{pretty(g.gap_type)}</strong><span className={'severity '+pretty(g.severity)}>{pretty(g.severity)}</span></div>
                <p>{g.source_event_id} → {g.target_event_id} · SCORE {formatMetric(g.score)}</p><p>{g.missing_bridge_hint||'No hint provided.'}</p>
                {g.suggested_event_type&&<small>SUGGESTED EVIDENCE: {g.suggested_event_type}</small>}
              </article>):<p className="muted">No bridge gaps recorded in this artifact.</p>}</div>
              <div><h3>Causal and memory contradictions</h3>{doc.contradictions.length ? doc.contradictions.map((c,i)=><article key={i} className="finding">
                <div className="finding-heading"><strong>{pretty(c.contradiction_type)}</strong><span className={'severity '+pretty(c.severity)}>{pretty(c.severity)}</span></div>
                <p>{c.message}</p><small>EVENTS: {Array.isArray(c.event_ids)?c.event_ids.join(', '):'not supplied'}</small>
              </article>):<p className="muted">No contradictions recorded in this artifact.</p>}
              <h3 className="second-heading">Bridge threshold provenance</h3>
              {Object.keys(doc.thresholds||{}).length ? Object.entries(doc.thresholds).map(([k,v])=><div className="threshold-row" key={k}><span>{pretty(k)}</span><strong>{formatNumber(v)}</strong><small>{doc.thresholdProvenance?.[k]||'not specified'}</small></div>):<p className="muted">No threshold metadata supplied.</p>}
              </div>
            </div>
          </>}
        </div>:<div className="protocol-pane">
          <span className="sectionlabel">HOW CHRONOLATTICE WORKS</span><h2>Evidence is the substrate.</h2>
          <p>The Python engine normalizes events, builds causality and memory links, estimates geometry, scores information and entropy, detects contradictions and bridge gaps, and emits deterministic reconstruction artifacts.</p>
          <div className="pipeline">{['INGEST','NORMALIZE','LINK','SCORE','INTERROGATE','RECEIPT'].map((stage,i)=><div key={stage}><small>{String(i+1).padStart(2,'0')}</small><strong>{stage}</strong></div>)}</div>
          <div className="protocol-grid">
            <div><span>CORE PRINCIPLE</span><h3>Deterministic replay</h3><p>Equal inputs and a matching seed are designed to produce the same reconstruction and hashes in the Python implementation. This page does not re-run the engine.</p></div>
            <div><span>BRIDGE DISCIPLINE</span><h3>Evidence, not invented history</h3><p>Missing-bridge findings propose where transitions could be absent. They do not create missing events or prove that a proposed event happened.</p></div>
            <div><span>LOCAL-FIRST</span><h3>Your data stays local</h3><p>Imported JSON is parsed inside your browser session. There is no upload endpoint, backend service, or automatic storage on the website.</p></div>
          </div>
          <div className="terminal"><div>$ python -m pip install -e ".[dev]"</div><div>$ chronolattice reconstruct data/examples/missing_bridge_gap.json --out out/reconstruction.json</div><div>$ chronolattice bridge-report out/reconstruction.json --out out/bridge_report.json</div><div>$ chronolattice receipt out/reconstruction.json --out out/receipt.json</div></div>
          <a className="action-primary" href={REPO+'/blob/main/docs/MASTER_SPEC.md'} target="_blank" rel="noreferrer">READ THE FULL SPECIFICATION <Icon name="arrow"/></a>
        </div>}
        {doc&&<div className="console-footer"><span><Icon name="layers" size={15}/> {doc.kind==='raw'?'RAW TRACE · NOT ENGINE RECONSTRUCTED':'IMPORTED ENGINE RECONSTRUCTION · HASH NOT VERIFIED'}</span><span>SCHEMA {doc.schemaVersion||'RAW'} · SEED {String(doc.seed||369369)}</span></div>}
      </div>
    </div>
    <section className="deep"><div><span className="eyebrow">02 / THE FRAMEWORK</span><h2>Time is not just<br/><em>a timestamp.</em></h2></div><p>A time-space trace means little without its relationships. ChronoLattice models the interdependence of causal order, memory continuity, geometry, information, and coherence. Its v0.x engine is a deterministic reconstruction prototype, not a claim to physical time travel or complete physics simulation.</p></section>
    <div className="pillars">{[
      ['01','CAUSALITY','Identify ordered influence and detect temporal contradictions.'],
      ['02','MEMORY','Trace shared references and missing continuity links.'],
      ['03','COHERENCE','Score structural consistency against a disclosed threshold.'],
      ['04','PROVENANCE','Preserve inputs, seed, hashes and reportable evidence.']
    ].map(([n,title,desc])=><div key={n}><small>{n} / CORE LAYER</small><h3>{title}</h3><p>{desc}</p></div>)}</div>
    <footer><div><strong>CHRONO<span>LATTICE</span></strong><p>RECONSTRUCT. VERIFY. REMEMBER.</p></div><div className="footerlinks"><a href={REPO} target="_blank" rel="noreferrer">GITHUB ↗</a><a href={REPO+'/blob/main/LICENSE'} target="_blank" rel="noreferrer">MIT LICENSE ↗</a><a href={REPO+'/blob/main/docs/ROADMAP.md'} target="_blank" rel="noreferrer">ROADMAP ↗</a></div><span>BUILT FOR THE FIELD · OPEN RESEARCH</span></footer>
  </div>;
}

createRoot(document.getElementById('root')).render(<App/>);
