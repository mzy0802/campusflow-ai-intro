from types import SimpleNamespace
import pytest
from app.navigation_grounding import explicit_endpoints
from app.place_search import aliases


def places():
    return [{**p,'aliases':aliases(p)} for p in [
        {'id':'home','name':'朝晖园15号公寓'},
        {'id':'m4','name':'明远教学楼D栋'},
        {'id':'m3','name':'明远教学楼C栋'},
        {'id':'x3','name':'修远教学楼三区'},
        {'id':'x4','name':'修远教学楼四区'}]]


def messages(*texts):return [SimpleNamespace(role='user',content=s) for s in texts]


def test_latest_explicit_request_overrides_historic_destination_and_resolves_aliases():
    fields,error=explicit_endpoints(messages('要从15号到修远3区。','我要从15到明远四区。'),places())
    assert not error and fields=={'origin_id':'home','destination_id':'m4'}
    fields,error=explicit_endpoints(messages('我在15号楼，要去明远四区。'),places())
    assert not error and fields['destination_id']=='m4'


def test_unmatched_and_ambiguous_endpoint_are_questions_not_replacement_buildings():
    fields,error=explicit_endpoints(messages('我要从15到明远六区。'),places())
    assert error and not fields
    items=places()+[{'id':'another','name':'另一园15号楼','aliases':['15号楼']}]
    fields,error=explicit_endpoints(messages('我要从15到明远四区。'),items)
    assert error and '起点' in error


def test_destination_only_correction_keeps_origin_but_replaces_previous_endpoint():
    fields,error=explicit_endpoints(messages('我要从15到修远3区','我要去明远四区'),places())
    assert not error and fields=={'origin_id':'home','destination_id':'m4'}


@pytest.mark.parametrize('text,destination_id',[('我要从15到明远四区。','m4'),('从15到修远4','x4')])
def test_chat_keeps_requested_place_and_returns_both_riding_types(monkeypatch,text,destination_id):
    from fastapi.testclient import TestClient
    from app.main import app
    from app import navigation,traffic_snapshot
    items=[{**p,'longitude':0 if p['id']=='home' else .001,'latitude':0} for p in places()]
    monkeypatch.setattr(navigation,'campus_places',lambda r:items)
    monkeypatch.setattr(navigation,'config',lambda:{})
    monkeypatch.setattr(navigation,'parse_trip',lambda *a:(_ for _ in ()).throw(AssertionError('explicit endpoints must not be guessed by the model')))
    graph={'revision':1,'nodes':[{'id':'a','longitude':0,'latitude':0},{'id':'b','longitude':.001,'latitude':0}],
           'edges':[{'id':'ab','source':'a','target':'b','verified':True,'modes':['walk','bike'],'bidirectional':True,'congestion':1}]}
    monkeypatch.setattr(traffic_snapshot,'snapshot',lambda *a:(graph,[],{'road_users':0,'active_accidents':0}))
    monkeypatch.setattr(navigation,'compute_parking',lambda *a:{'items':[]})
    monkeypatch.setattr(navigation,'bus_options',lambda *a:[])
    client=TestClient(app)
    response=client.post('/api/navigation/chat',json={'messages':[{'role':'user','content':text}],'transport':'bicycle'})
    assert response.status_code==200,response.text
    d=response.json()
    assert d['origin']['id']=='home' and d['destination']['id']==destination_id
    assert {'bicycle','electric'}<={o.get('vehicle_type') for o in d['options']}
    assert d['route']['vehicle_type']=='bicycle'
    assert [o['duration_minutes'] for o in d['options']]==sorted(o['duration_minutes'] for o in d['options'])
    second=client.post('/api/navigation/chat',json={'messages':[{'role':'user','content':text}],'transport':'electric'}).json()
    assert second['route']['vehicle_type']=='electric'
    assert second['route']['duration_minutes']<d['route']['duration_minutes']


def test_only_nearest_feasible_bus_is_returned(monkeypatch):
    from app import navigation,transit
    from app.trip_planner import distance
    stops=[{'id':'near-a','name':'Near A','longitude':0,'latitude':0},{'id':'near-b','name':'Near B','longitude':.01,'latitude':0},
           {'id':'far-a','name':'Far A','longitude':0,'latitude':.002},{'id':'far-b','name':'Far B','longitude':.01,'latitude':.002}]
    data={'stops':stops,'vehicles':[],'routes':[
        {'id':'far','name':'Far','color':'blue','stop_ids':['far-a','far-b'],'points':[stops[2],stops[3]]},
        {'id':'near','name':'Near','color':'blue','stop_ids':['near-a','near-b'],'points':[stops[0],stops[1]]}]}
    monkeypatch.setattr(transit,'configured',lambda s:data)
    def walking(g,body,mode):
        a=body.origin.model_dump();b=body.destination.model_dump();meters=distance(a,b)
        return {'distance_m':meters,'duration_minutes':meters/80,'geojson':{'geometry':{'type':'LineString','coordinates':[[a['longitude'],a['latitude']],[b['longitude'],b['latitude']]]}}}
    monkeypatch.setattr(navigation,'route',walking)
    request=SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(store=None)))
    body=navigation.NavigationRequest(origin={'longitude':0,'latitude':0},destination={'longitude':.01,'latitude':0})
    options=navigation.bus_options({},body,request)
    assert len(options)==1 and options[0]['id']=='bus:near'
    assert options[0]['access_distance_m']==0
    # These saved routes operate one way, so the reverse trip is not offered.
    reverse=body.model_copy(update={'origin':body.destination,'destination':body.origin})
    assert navigation.bus_options({},reverse,request)==[]


def test_ordinary_options_never_calls_model_and_keeps_all_parking_choices_sorted(monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app
    from app import navigation,traffic_snapshot
    monkeypatch.setattr(navigation,'config',lambda:(_ for _ in ()).throw(AssertionError('ordinary route must not call a model')))
    monkeypatch.setattr(traffic_snapshot,'snapshot',lambda *a:({},[],{'road_users':3,'active_accidents':0}))
    geometry={'type':'Feature','geometry':{'type':'LineString','coordinates':[[0,0],[.001,0]]}}
    monkeypatch.setattr(navigation,'route',lambda g,b,m:{'mode':m,'duration_minutes':20,'distance_m':1000,'geojson':geometry})
    lots=[{'area_id':str(i),'name':f'Parking {i}','duration_minutes':minutes,'distance_m':900,'walk_minutes':2,'capacity':100,'free':30,'percent':70,'geojson':geometry} for i,minutes in enumerate([12,8,10])]
    monkeypatch.setattr(navigation,'compute_parking',lambda *a:{'items':lots})
    monkeypatch.setattr(navigation,'bus_options',lambda *a:[])
    response=TestClient(app).post('/api/navigation/options',json={'origin':{'longitude':0,'latitude':0},'destination':{'longitude':.001,'latitude':0}})
    assert response.status_code==200,response.text
    d=response.json();options=d['options']
    assert [o['duration_minutes'] for o in options]==sorted(o['duration_minutes'] for o in options)
    assert sum(o.get('vehicle_type')=='bicycle' for o in options)==3
    assert sum(o.get('vehicle_type')=='electric' for o in options)==3
    assert d['recommended']==options[0]['id']
    assert d['route']['traffic']['road_users']==3
