import test from 'node:test'
import assert from 'node:assert/strict'
import {orderedOptions,transportGroups,transportKey} from '../src/navigationChoices.js'
const options=[
 {id:'bike-slow',mode:'bike',vehicle_type:'bicycle',area_id:'p1',duration_minutes:12,distance_m:900},
 {id:'walk',mode:'walk',duration_minutes:20,distance_m:700},
 {id:'bus',mode:'bus',duration_minutes:10,distance_m:1100},
 {id:'bike-fast',mode:'bike',vehicle_type:'bicycle',area_id:'p2',duration_minutes:8,distance_m:950},
 {id:'electric',mode:'bike',vehicle_type:'electric',area_id:'p2',duration_minutes:6,distance_m:950},
]
test('first level has one card per mode, ordered by fastest complete trip',()=>{
 const groups=transportGroups(options)
 assert.deepEqual(groups.map(g=>g.key),['electric','bicycle','bus','walk'])
 assert.equal(groups[1].best.id,'bike-fast')
 assert.equal(options[0].id,'bike-slow')
})
test('second level keeps parking alternatives only for selected vehicle type, in time order',()=>{
 const parking=orderedOptions(options.filter(o=>transportKey(o)==='bicycle'&&o.area_id))
 assert.deepEqual(parking.map(o=>o.id),['bike-fast','bike-slow'])
 assert.deepEqual(transportGroups([]),[])
})
