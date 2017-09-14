from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.core.exceptions import ValidationError
from MOCapi.models import Tracks, Users
import json

def index(request):
    HttpResponse.status_code = 501
    error = {
            'error_code' : 501,
            'error_message' : 'Method not supported' }
    return JsonResponse(error, safe=False)

# Create your views here.
@csrf_exempt
def tracks(request, end_path, resource_id):
    path = request.path

    HttpResponse.status_code = 200

    if request.method == 'GET' and resource_id is None:
        resp = getAllTracks()
        return JsonResponse(resp, safe=False)
    else:
        if request.method == 'GET' and resource_id is not None:
            resp = getOneTrack(resource_id)
            return JsonResponse(resp,safe=False)
        else:
            if request.method == 'PUT' and resource_id is not None:
                resp = updateTrack(resource_id)
                return JsonResponse(resp, safe=False)
            else:
                if request.method == 'POST' and resource_id is None:
                    resp = insertTrack(request.body)
                    return JsonResponse(resp, safe=False)
                else:
                    HttpResponse.status_code = 501
                    error = {
                            'error_code' : 501,
                            'error_message' : 'Method not supported' }
                    return JsonResponse(error, safe=False)
            
def getAllTracks():
    try:
        tracks = Tracks.objects.all().filter(user_id='pegi@gruar.co.uk')
    except:
        HttpResponse.status_code = 500
        error = {
                'error_code' : 500,
                'error_message' : 'Unexpected database error' }
        return error

    if Tracks.objects.all().filter(user_id='pegi@gruar.co.uk').count() == 0:
        HttpResponse.status_code = 404
        error = {
                'error_code' : 404,
                'error_message' : 'No matching records' }
        return error
        
    payload = []
    for track in tracks:
        dict = buildTrackDict(track)
        payload.append(dict)
    
    return payload
    
def getOneTrack(track_id):
    try:
        track = Tracks.objects.get(pk=track_id)
    except:
        HttpResponse.status_code = 400
        error = {
                'error_code' : 404,
                'error_message' : 'Track not found' }
        return error
    payload = buildTrackDict(track)
    return payload
    
def insertTrack(payloadJ):
    payload = json.loads(payloadJ)
    track = Tracks(
                    user_id = payload['user_id'],
                    track_name = payload['track_name'],
                    created_on = payload['created_on']
                       )
    try:                
        track.save()
    except ValidationError as e:
        error = {
                'error_code' : 400,
                'error_message' : e.messages }
        
        HttpResponse.status_code = 400

        return error
    except:
        error = {
                'error_code' : 500,
                'error_message' : "Unexpected Database Error"}
        
        HttpResponse.status_code = 500
        return error

    response = {'message' : (track.id, ' Inserted'),  }
    
    HttpResponse.status_code = 201
    
    return response
    
def updateTrack(track_id):
    response = {'message' : 'Track updated' }
    return response
    
def buildTrackDict(track):
    trackDict = {
            'id': track.id,
            'user_id' : track.user_id,
            'track_name' : track.track_name,
            'created_on' : track.created_on
        }
    return trackDict    
    
def users(request, end_path, resource_id):
    path = request.path

    HttpResponse.status_code = 200
    HttpResponse.reason_phrase = 'OK'
    
                    
    