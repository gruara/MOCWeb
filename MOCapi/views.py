from django.shortcuts import render
from django.http import HttpResponse#
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.http import JsonResponse
from MOCapi.models import Tracks
import json

def index(request):
    return HttpResponse("Go away")

# Create your views here.
@csrf_exempt
def tracks(request, end_path, resource_id):
    path = request.path

    HttpResponse.status_code = 200
    
    
    if request.method == 'GET' and resource_id is None:
        resp = getAllTracks()
        if resp is None:
            HttpResponse.status_code = 500
            return HttpResponse('Failure')
        else:
            return JsonResponse(resp, safe=False)
    else:
        if request.method == 'GET' and resource_id is not None:
            resp = getOneTrack(resource_id)
            if resp is None:
                HttpResponse.status_code = 404
                return HttpResponse('Not found')
            else:
                return JsonResponse(resp,safe=False)
        else:
            if request.method == 'PUT' and resource_id is not None:
                resp = updateTrack(resource_id)
                return HttpResponse("Putting on the Ritz")
            else:
                if request.method == 'POST' and resource_id is None:
                    resp = insertTrack(request.body)
                    if resp is None:
                        HttpResponse.status_code = 500
                        return HttpResponse('Failure')
                    else:
                        return HttpResponse("Return to sender")
                else:
                    HttpResponse.status_code = 501
                    return HttpResponse("I give up")
            
def getAllTracks():
    try:
        tracks = Tracks.objects.all().filter(user_id='andrew@gruar.co.uk')
    except:
        return None
    payload = []
    for track in tracks:
        dict = buildTrackDict(track)
        payload.append(dict)
    
#     print(tracks.count())
#     payload = serializers.serialize('json', tracks)
    print(payload)
    return payload
    
def getOneTrack(track_id):
    try:
        track = Tracks.objects.get(pk=track_id)
    except:
        return None
    payload = buildTrackDict(track)
    return payload
    
def insertTrack(payloadJ):
    payload = json.loads(payloadJ)
    print(payload['track_name'])
    track = Tracks(
                    user_id = payload['user_id'],
                    track_name = payload['track_name'],
                    created_on = payload['created_on']
                       )
    try:                
        track.save()
#     except ValidationError, e:
#         HttpResponse.status_code = 400
#         return None
    except:
        HttpResponse.status_code = 500
        return None
    print(track)
    return track.id
    
def updateTrack(track_id):
    return ('update', track_id )
    
def buildTrackDict(track):
    trackDict = {
            'id': track.id,
            'user_id' : track.user_id,
            'track_name' : track.track_name,
            'created_on' : track.created_on
        }
#    print(row[4])
    return trackDict    
    
                
    