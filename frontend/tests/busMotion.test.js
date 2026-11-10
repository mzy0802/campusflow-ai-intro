import test from 'node:test'
import assert from 'node:assert/strict'
import {busState,busStatus,busDisplayOffset,busCountsAt} from '../src/busMotion.js'
const trip={departure_seconds:180,arrival_seconds:300,profile:[[0,0],[40,.5],[58,.5],[120,1]],coordinates:[[108,34],[108.002,34]],stops:[{name:'中间站',arrival_seconds:40,departure_seconds:58}]}
test('Xiaobai departs at 08:03, pauses at stations and rewinds with the shared clock',()=>{
 assert.equal(busState(trip,179).visible,false)
 assert.equal(busState(trip,179).kind,'waiting')
 assert.equal(busState(trip,180).kind,'moving')
 assert.equal(busState(trip,180).visible,true)
 assert.equal(busState(trip,299).visible,true)
 assert.equal(busState(trip,300).visible,false)
 assert.equal(busState(trip,225).visible,true)
 assert.equal(busState(trip,225).kind,'stopped')
 assert.equal(busState(trip,225).progress,busState(trip,235).progress)
 assert.equal(busStatus(trip,225),'中间站停靠')
 assert.equal(busState(trip,300).kind,'arrived')
 assert.equal(busState(trip,1800).visible,false)
 assert.equal(busState(trip,1800).kind,'arrived')
 assert.equal(busState(trip,180).progress,0)
})
test('second trip remains at origin until 08:15',()=>{
 const second={...trip,departure_seconds:900,arrival_seconds:1020}
 assert.equal(busState(second,899).kind,'waiting')
 assert.equal(busState(second,900).progress,0)
 assert.equal(busState(second,1000).kind,'moving')
})

test('waiting buses sharing an origin fan out but moving buses stay on their line',()=>{
 const a={...trip,id:'a'},b={...trip,id:'b'},list=[a,b]
 assert.notDeepEqual(busDisplayOffset(a,list,0),busDisplayOffset(b,list,0))
 assert.deepEqual(busDisplayOffset(a,list,200),{x:0,y:0})
 assert.deepEqual(busState(a,0).position,busState(b,0).position)
})

test('both batches actually move and counts distinguish waiting, running and arrived',()=>{
 const first=Array.from({length:4},(_,i)=>({...trip,id:`first-${i}`}))
 const second=first.map(t=>({...t,id:t.id+'-second',departure_seconds:900,arrival_seconds:1020}))
 const all=[...first,...second]
 assert.deepEqual(busCountsAt(all,0),{waiting:8,running:0,arrived:0})
 assert.deepEqual(busCountsAt(all,200),{waiting:4,running:4,arrived:0})
 assert.notDeepEqual(busState(first[0],200).position,busState(first[0],210).position)
 assert.deepEqual(busCountsAt(all,920),{waiting:0,running:4,arrived:4})
 assert.notDeepEqual(busState(second[0],920).position,busState(second[0],930).position)
 assert.deepEqual(busCountsAt(all,1800),{waiting:0,running:0,arrived:8})
})
