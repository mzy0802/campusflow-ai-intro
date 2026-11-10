export const transportKey=o=>o.vehicle_type||(o.mode==='bike'?'bicycle':o.mode)
export const transportLabel=key=>({walk:'步行',bicycle:'自行车',electric:'电动车',bus:'小白公交'}[key]||key)
export function orderedOptions(options){return [...options].sort((a,b)=>a.duration_minutes-b.duration_minutes||a.distance_m-b.distance_m||String(a.id).localeCompare(String(b.id)))}
export function transportGroups(options){
 const groups=new Map()
 for(const option of orderedOptions(options)){
  const key=transportKey(option)
  if(!groups.has(key))groups.set(key,{key,label:transportLabel(key),best:option,options:[]})
  groups.get(key).options.push(option)
 }
 return [...groups.values()]
}
