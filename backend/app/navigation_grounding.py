"""Bind explicitly stated endpoints to catalog aliases before model interpretation."""
import re
from .place_search import normalize


def explicit_endpoints(messages,items):
    fields={}
    for message in messages:
        if message.role!='user':continue
        text=message.content.strip()
        pair=re.search(r'(?:从|我在|现在在)(.+?)(?:出发)?[，,\s]*(?:我)?(?:想要|想|要)?(?:到|去|前往)(.+?)(?:[，,。；;]|$)',text)
        if pair:fields.update(origin=pair[1],destination=pair[2])
        else:
            dest=re.match(r'^(?:我)?(?:想要|想|要)?(?:去|到|前往)(.+?)(?:[，,。；;]|$)',text)
            if dest:fields['destination']=dest[1]
    result={}
    for field,text in fields.items():
        key=normalize(re.sub(r'[，,\s]*(?:我)?(?:想|要)$','',text))
        matches=[p for p in items if text.strip()==p['name'] or (key and key in [normalize(p['name'])]+[normalize(a) for a in p.get('aliases',[])])]
        if len(matches)!=1:
            names='、'.join(p['name'] for p in matches[:5])
            return {},f"请确认{'起点' if field=='origin' else '终点'}“{text}”的完整名称"+(f'：{names}。' if names else '，当前目录没有唯一匹配，不能替换成其他地点。')
        result[field+'_id']=str(matches[0]['id'])
    return result,None
