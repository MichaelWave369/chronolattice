import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizeDocument, makeGraph, formatMetric } from '../src/chronodata.js';

function event(id,seq,actor='A',time='2026-01-01T00:00:00Z',memory=['shared']) {
  return {event_id:id,sequence_index:seq,actor,event_type:'observe',timestamp:time,memory_refs:memory,coherence:.9};
}

test('raw traces show sequence/memory hints but no engine scores', () => {
  const view=normalizeDocument({run_id:'raw',seed:369369,events:[event('b',2),event('a',1)]});
  assert.equal(view.kind,'raw');
  assert.deepEqual(view.events.map(e=>e.event_id),['a','b']);
  assert.equal(view.sequenceLinks.length,1);
  assert.equal(view.memoryHints.length,1);
  assert.equal(view.coherence,null);
  assert.equal(view.bridges.length,0);
});

test('wrapped reconstruction displays imported scores and authoritative lists as imported data only', () => {
  const payload={run_id:'tested',seed:369369,reconstruction_hash:'abc',
    events:[event('a',1),event('b',2,'B')],
    causal_edges:[{source_event_id:'a',target_event_id:'b',allowed:true}],
    memory_edges:[{source_event_id:'a',target_event_id:'b',shared_refs:['shared']}],
    geometry_edges:[],contradictions:[{contradiction_type:'timestamp_inversion',event_ids:['a','b'],severity:'high'}],
    bridge_gaps:[{gap_type:'actor_discontinuity',source_event_id:'a',target_event_id:'b',severity:'medium',score:.75}],
    coherence:.41,stable:false,entropy_score:.2,information_score:.8,bridge_profile:'balanced'};
  const view=normalizeDocument({kind:'chronolattice.reconstruction',schema_version:'0.1',payload});
  assert.equal(view.kind,'reconstruction');
  assert.equal(view.wrapped,true);
  assert.equal(view.causalEdges.length,1);
  assert.equal(view.memoryEdges.length,1);
  assert.equal(view.bridges.length,1);
  assert.equal(view.contradictions.length,1);
  assert.equal(view.coherence,.41);
  assert.equal(view.stable,false);
  assert.equal(view.schemaVersion,'0.1');
});

test('event coordinates are in increasing sequence order and separated by actor',()=>{
  const view=normalizeDocument({events:[event('b',2,'Y'),event('a',1,'X')]});
  const g=makeGraph(view);
  assert.ok(g.positions.a.x<g.positions.b.x);
  assert.notEqual(g.positions.a.y,g.positions.b.y);
});

test('timestamps can invert without inventing a contradiction verdict',()=>{
  const view=normalizeDocument({events:[
    event('a',1,'X','2026-01-01T00:00:10Z'),
    event('b',2,'X','2026-01-01T00:00:05Z')
  ]});
  assert.equal(view.timeInversions,1);
  assert.equal(view.contradictions.length,0);
});

test('malformed inputs fail closed',()=>{
  assert.throws(()=>normalizeDocument({events:[]}),/no events/i);
  assert.throws(()=>normalizeDocument({events:[event('a',1),event('a',2)]}),/Duplicate/);
  assert.throws(()=>normalizeDocument({kind:'chronolattice.receipt',payload:{events:[event('a',1)]}}),/does not graph/);
  assert.throws(()=>normalizeDocument({kind:'chronolattice.reconstruction',payload:{events:[event('a',1)]}}),/missing required/);
  assert.throws(()=>normalizeDocument({events:[{event_id:'x'}]}),/Invalid event/);
});

test('metric formatting is explicit for unavailable data',()=>{
  assert.equal(formatMetric(null),'—');
  assert.equal(formatMetric(.809016994),'0.809');
});
