"""Xiaobai presentation timetable on owner-drawn geometry, never invented roads."""
import math
from .trip_planner import distance

DEPARTURES=(180,900)
SPEED_KMH=18
DWELL_SECONDS=18
COLOR='#159fbd'


def project_stop(stop,points,lengths):
    sx=111320*math.cos(math.radians(stop['latitude']));sy=111320
    best=(float('inf'),0)
    for i,(a,b) in enumerate(zip(points,points[1:])):
        dx=(b['longitude']-a['longitude'])*sx;dy=(b['latitude']-a['latitude'])*sy
        t=max(0,min(1,((stop['longitude']-a['longitude'])*sx*dx+(stop['latitude']-a['latitude'])*sy*dy)/(dx*dx+dy*dy or 1)))
        gap=math.hypot((stop['longitude']-a['longitude'])*sx-t*dx,(stop['latitude']-a['latitude'])*sy-t*dy)
        if gap<best[0]:best=(gap,lengths[i]+t*(lengths[i+1]-lengths[i]))
    return best


def timetable(data):
    stops={s['id']:s for s in data['stops']};trips=[];warnings=[]
    for route in data['routes']:
        points=route['points']
        if len(points)<2:continue
        lengths=[0.]
        for a,b in zip(points,points[1:]):lengths.append(lengths[-1]+distance(a,b))
        total=lengths[-1]
        if total<1:continue
        visits=[]
        for sid in route['stop_ids']:
            stop=stops.get(sid)
            if not stop:continue
            gap,at=project_stop(stop,points,lengths)
            if gap>80:
                warnings.append(f"{route['name']}：{stop['name']}距已绘线路约{round(gap)}米，暂不作为停靠点")
                continue
            if not any(abs(at-v['distance_m'])<8 for v in visits):visits.append({'id':sid,'name':stop['name'],'distance_m':at})
        visits.sort(key=lambda s:s['distance_m'])
        # Eight-metre integration keeps bends and station positions exact.
        marks=sorted(set([0.,total]+lengths+[min(total,float(i)) for i in range(8,int(total),8)]+[s['distance_m'] for s in visits]))
        profile=[[0.,0.]];elapsed=0.;station_times=[]
        for i,at in enumerate(marks):
            if i:
                middle=(at+marks[i-1])/2
                vertex=min(range(1,len(lengths)-1),key=lambda k:abs(lengths[k]-middle)) if len(lengths)>2 else None
                bend=1.
                if vertex and abs(lengths[vertex]-middle)<16:
                    a,b,c=points[vertex-1:vertex+2]
                    u=((b['longitude']-a['longitude'])*math.cos(math.radians(b['latitude'])),b['latitude']-a['latitude'])
                    v=((c['longitude']-b['longitude'])*math.cos(math.radians(b['latitude'])),c['latitude']-b['latitude'])
                    dot=sum(x*y for x,y in zip(u,v))/(math.hypot(*u)*math.hypot(*v) or 1)
                    bend=max(.44,(max(-1,min(1,dot))+1)/2)
                wave=1+.10*math.sin(middle/55)
                elapsed+=(at-marks[i-1])/(SPEED_KMH/3.6*bend*wave)
                profile.append([round(elapsed,3),round(at/total,8)])
            for stop in visits:
                if abs(stop['distance_m']-at)>.001:continue
                interior=at>8 and at<total-8
                station_times.append({**stop,'arrival_seconds':round(elapsed,3),'departure_seconds':round(elapsed+(DWELL_SECONDS if interior else 0),3)})
                if interior:
                    elapsed+=DWELL_SECONDS;profile.append([round(elapsed,3),round(at/total,8)])
        vehicles=[v for v in data['vehicles'] if v['route_id']==route['id']]
        used=set()
        for index,departure in enumerate(DEPARTURES,1):
            chosen=next((v for v in vehicles if v['id'] not in used and v['name'].strip().endswith(f'{index}车')),None)
            if chosen is None:chosen=next((v for v in vehicles if v['id'] not in used),None)
            if chosen:used.add(chosen['id'])
            trips.append({'id':f"{route['id']}-departure-{index}",'vehicle_id':chosen['id'] if chosen else None,'name':chosen['name'] if chosen else f"{route['name']}{index}车",'route_id':route['id'],'route_name':route['name'],'departure_seconds':departure,'arrival_seconds':round(departure+elapsed,3),'duration_seconds':round(elapsed,3),'distance_m':round(total,1),'speed_kmh':SPEED_KMH,'capacity':chosen['capacity'] if chosen else None,'observation':chosen.get('observation') if chosen else None,'coordinates':[[p['longitude'],p['latitude']] for p in points],'profile':profile,'stops':station_times})
    return {'trips':trips,'warnings':warnings,'color':COLOR,'departures':['08:03','08:15'],'speed_kmh':SPEED_KMH,'stop_seconds':DWELL_SECONDS,'notice':'演示班次；按已绘线路方向单程运行，弯道减速及站点停靠；非实际运营时刻表'}
