import {paceAt,routePoint} from './simulationMath.js'
export const BUS_COLOR='#159fbd'
export function busState(trip,time){
 const elapsed=time-trip.departure_seconds
 const progress=elapsed<0?0:paceAt(trip.profile,elapsed)??0
 const stop=(trip.stops||[]).find(s=>elapsed>=s.arrival_seconds&&elapsed<s.departure_seconds)
 const kind=elapsed<0?'waiting':time>=trip.arrival_seconds?'arrived':stop?'stopped':'moving'
 return {kind,progress,position:routePoint(trip.coordinates,progress),stop:stop?.name,
  visible:kind==='moving'||kind==='stopped'}
}
export function busStatus(trip,time){const s=busState(trip,time);return s.kind==='waiting'?'待发车':s.kind==='arrived'?'已到终点':s.kind==='stopped'?`${s.stop}停靠`:'行驶中'}

// Parked buses sharing a terminus fan out in screen space, without moving their route coordinates.
export function busDisplayOffset(trip,trips,time){
 const state=busState(trip,time)
 if(!['waiting','arrived'].includes(state.kind))return {x:0,y:0}
 const neighbours=trips.filter(t=>{const s=busState(t,time);return s.kind===state.kind&&Math.hypot((s.position[0]-state.position[0])*.83,s.position[1]-state.position[1])<.0002})
 const index=neighbours.findIndex(t=>t.id===trip.id),cols=Math.min(2,neighbours.length)
 return {x:((index%cols)-(cols-1)/2)*64,y:Math.floor(index/cols)*54}
}

export function busCountsAt(trips,time){
 const counts={waiting:0,running:0,arrived:0}
 for(const trip of trips){const kind=busState(trip,time).kind;counts[kind==='moving'||kind==='stopped'?'running':kind]++}
 return counts
}
