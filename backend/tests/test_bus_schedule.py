import copy
import pytest
from app.bus_schedule import timetable


def example():
    return {'routes':[{'id':'r','name':'测试线','points':[{'longitude':108.89,'latitude':34.37},{'longitude':108.891,'latitude':34.37},{'longitude':108.892,'latitude':34.37}],'stop_ids':['end','middle','start']}],
            'stops':[{'id':key,'name':key,'longitude':x,'latitude':34.37} for key,x in [('start',108.89),('middle',108.891),('end',108.892)]],
            'vehicles':[{'id':'one','name':'测试线1车','route_id':'r','capacity':15},{'id':'duplicate','name':'测试线1车','route_id':'r','capacity':15},{'id':'two','name':'测试线2车','route_id':'r','capacity':15}]}


def test_each_route_has_two_departures_and_preserves_saved_geometry_and_vehicles():
    data=example();original=copy.deepcopy(data);out=timetable(data)
    assert [t['departure_seconds'] for t in out['trips']]==[180,900]
    assert [t['vehicle_id'] for t in out['trips']]==['one','two']
    assert data==original
    assert out['trips'][0]['coordinates']==[[108.89,34.37],[108.891,34.37],[108.892,34.37]]
    assert out['trips'][1]['arrival_seconds']-out['trips'][0]['arrival_seconds']==pytest.approx(720)


def test_stops_follow_drawn_direction_with_a_real_pause_and_off_line_warning():
    data=example();data['stops'].append({'id':'far','name':'离线站','longitude':108.9,'latitude':34.38});data['routes'][0]['stop_ids'].append('far')
    out=timetable(data);trip=out['trips'][0]
    assert [s['id'] for s in trip['stops']]==['start','middle','end']
    middle=trip['stops'][1]
    assert middle['departure_seconds']-middle['arrival_seconds']==pytest.approx(18)
    assert any(p==q and t<u for (t,p),(u,q) in zip(trip['profile'],trip['profile'][1:]))
    assert out['warnings'] and '离线站' in out['warnings'][0]
    assert all(a[0]<=b[0] and a[1]<=b[1] for a,b in zip(trip['profile'],trip['profile'][1:]))
    assert trip['profile'][0]==[0,0] and trip['profile'][-1][1]==1


def test_unassigned_route_still_gets_two_demo_trips_without_invented_observations():
    data=example();data['vehicles']=[]
    trips=timetable(data)['trips']
    assert len(trips)==2 and all(t['observation'] is None and t['vehicle_id'] is None for t in trips)
