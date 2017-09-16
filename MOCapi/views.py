from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from MOCapi.models import Tracks, Users
import json

def index(request):
    HttpResponse.status_code = 501
    resp = {
            'error_code' : 501,
            'error_message' : 'Method not supported' }
    return JsonResponse(resp, safe=False)

# Create your views here.
@csrf_exempt
def tracks(request, end_path, resource_id):
    if request.method == 'GET' and resource_id is None:
        resp = getAllTracks()
    else:
        if request.method == 'GET' and resource_id is not None:
            resp = getOneTrack(resource_id)
        else:
            if request.method == 'PUT' and resource_id is not None:
                resp = updateTrack(resource_id)
            else:
                if request.method == 'POST' and resource_id is None:
                    resp = insertTrack(request.body)
                else:
                    resp = {
                            'error_code' : 501,
                            'error_message' : 'Method not supported' }
    if 'error_code' in resp:
        HttpResponse.status_code = resp['error_code']
    else:
        HttpResponse.status_code = 200    
    return JsonResponse(resp, safe=False)
            
def getAllTracks():
    try:
        tracks = Tracks.objects.all().filter(user_id='iola@gruar.co.uk')
    except:
        error = {
                'error_code' : 500,
                'error_message' : 'Unexpected database error' }
        return error

    if Tracks.objects.all().filter(user_id='iola@gruar.co.uk').count() == 0:
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
        return error
    except IntegrityError as e:
        error = {
                'error_code' : 400,
                'error_message' : e.messages }
        return error
    except:
        error = {
                'error_code' : 500,
                'error_message' : "Unexpected Database Error"}
        return error

    response = {'message' : (track.id, ' Inserted'),  }
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

@csrf_exempt    
def users(request, end_path, resource_id):
    print(end_path)
    print(resource_id)
    if request.method == 'GET' and resource_id is not None:
        resp = getUser(resource_id)
    else:
        if request.method == 'POST' and resource_id is None:
            resp = insertUser(request.body)
        else:
            resp = {
                    'error_code' : 501,
                    'error_message' : 'Method not supported' }
    
    if 'error_code' in resp:
        HttpResponse.status_code = resp['error_code']
    else:
        HttpResponse.status_code = 200    
    return JsonResponse(resp, safe=False)

def getUser(user_id):
    try:
        user = Users.objects.get(user_id=user_id.lower())
    except:
        error = {
                'error_code' : 404,
                'error_message' : 'Track not found' }
        return error
    payload = buildUserDict(user)
    return payload

def insertUser(payloadJ):
    payload = json.loads(payloadJ)
    user = Users(
                    user_id = payload['user_id'].lower(),
                    name = payload['name'],
                    created_on = payload['created_on'],
                    token = 'None Assigned',
                    token_expiry = '2000-01-01 00:00:01'
                       )
    try:                
        user.save()
    except ValidationError as e:
        error = {
                'error_code' : 400,
                'error_message' : e.messages }
        return error
    except IntegrityError as e:
        error = {
                'error_code' : 400,
                'error_message' : e.__cause__.pgerror} 
        return error
    except:
        error = {
                'error_code' : 500,
                'error_message' : "Unexpected  Error"}
        return error

    response = {'message' : (user.id, ' Inserted'),  }
    return response


def buildUserDict(user):
    user = {
            'id': user.id,
            'user_id' : user.user_id,
            'name' : user.name,
            'created_on' : user.created_on,
            'password' : user.password
        }
    return user