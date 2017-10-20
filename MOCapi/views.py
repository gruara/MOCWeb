from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from MOCapi.models import Tracks, Users, Images, TrackDetails
from passlib.hash import pbkdf2_sha256
from django.conf import settings
import json
import logging
import uuid
import datetime
#import pytz
import re

import xml.etree.ElementTree as ET
from werkzeug.wsgi import responder

session = {}
summary = {}


logging.basicConfig(format=settings.FORMAT,filename=settings.LOGFILE,filemode='a')
d = {'clientip': '192.168.0.1', 'user': 'unknown'}
logger = logging.getLogger(__name__)
logger.setLevel(settings.LOGLEVEL)
logger.warning('Process started', extra=d)


def index(request):
    HttpResponse.status_code = 501
    resp = {
            'error_code' : 501,
            'error_message' : 'Method not supported' }
    return JsonResponse(resp, safe=False)

# Create your views here.
@csrf_exempt
def tracks(request, end_path, resource_id):
    logger.info(requestDetails(request))
    
    if authorized(request) is False:
        resp = {
            'error_code' : 401,
            'error_message' : 'Not authorised' }
    else:
        if request.method == 'GET' and resource_id is None:
            resp = getAllTracks(request)
        elif request.method == 'GET' and resource_id is not None:
            resp = getOneTrack(request, resource_id)
        elif request.method == 'PUT' and resource_id is not None:
            resp = updateTrack(request, resource_id)
        elif request.method == 'POST' and resource_id is None:
            resp = insertTrack(request)
        else:
            resp = {
                    'error_code' : 501,
                    'error_message' : 'Method not supported' }
    if 'error_code' in resp:
        HttpResponse.status_code = resp['error_code']
    else:
        HttpResponse.status_code = 200
   
    return JsonResponse(resp, safe=False)
            
def getAllTracks(request):
    try:
        tracks = Tracks.objects.all().filter(user_id=session['user_id'])
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
    resp = {'tracks' : payload}
    return resp
    
def getOneTrack(request, track_id):
#    extra=d allows non standard entries to be added
    logger.info('getOneTrack Started', extra=d)
    logger.error('It is going to blow Jim', extra=d)
    try:
        track = Tracks.objects.get(pk=track_id)
    except:
        error = {
                'error_code' : 404,
                'error_message' : 'Track not found' }
        return error
    payload = buildTrackDict(track)
    return payload
    
def insertTrack(request):
    payload = json.loads(request.body)
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
                'error_message' : e.__cause__.pgerror}
        return error
    except:
        error = {
                'error_code' : 500,
                'error_message' : "Unexpected Database Error"}
        return error

    response = {'message' : (track.id, ' Inserted'),  }
    return response
    
def updateTrack(request, track_id):
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
def trackdetails(request, end_path, resource_id):
    global summary
    summary['id'] = resource_id
    if authorized(request) is False:
        resp = {
            'error_code' : 401,
            'error_message' : 'Not authorised' }
    else:
        if request.method == 'GET' and resource_id is not None:
            resp = getTrackDetails(resource_id)
        elif request.method == 'POST' and resource_id is not None:
            resp = parseTrackDetails(request)
        else:
            resp = {
                    'error_code' : 501,
                    'error_message' : 'Method not supported' }
    if 'error_code' in resp:
        HttpResponse.status_code = resp['error_code']
    else:
        HttpResponse.status_code = 200
   
    return JsonResponse(resp, safe=False)

def getTrackDetails(track):
    try:
        track = Tracks.objects.get(pk=summary['id'])
    except:
        error = {
                'error_code' : 404,
                'error_message' : 'Track not found' }
        return error
    header = {'id' : track.id,
              'user_id' : track.user_id,
              'created_on' : track.created_on,
              'track_name' : track.track_name}
    
    try:
        trackdets = TrackDetails.objects.all().filter(track=track.id)
    except:
        error = {
                'error_code' : 500,
                'error_message' : 'Unexpected database error' }
        return error
    body = []
    for trackdet in trackdets:
        body.append({
            "time" : trackdet.time,
            "longitude" : trackdet.longitude,
            "latitude" : trackdet.latitude,
            "elevation" : trackdet.elevation})
        
    
    resp = {'track' : header,
            'details' : body}
    return resp


def parseTrackDetails(request):
    global summary
    root = ET.fromstring(request.body)
    for child in root:
        if re.match('.*trk$', child.tag):
            for trk in child:
                if re.match('.*name$', trk.tag):
                    summary['name'] = trk.text
                elif re.match('.*trkseg$', trk.tag):
                    resp = segment(trk)
                    if 'error_code' in resp:
                        return resp
        else:
            if re.match('.*exerciseinfo$', child.tag):
                for det in child:
                    if re.match('.*exercisetype$', det.tag):
                        summary['type'] = det.text
                    elif re.match('.*distance$', det.tag):
                        summary['distance'] = det.text
                    elif re.match('.*duration$', det.tag):
                        summary['duration'] = det.text
                    elif re.match('.*avgspeed$', det.tag):
                        summary['avgspeed'] = det.text
                 
    return {'message' : 'Track Details Inserted'}
    
    
def segment(segment):
    global summary
    try:
        track = Tracks.objects.get(pk=summary['id'])
    except:
        error = {
                'error_code' : 404,
                'error_message' : 'Track not found' }
        return error

    for point in segment:
        pointdet = {'time' : '', 
                    'longitude' : '', 
                    'latitude' : '', 
                    'elevation' : ''}
        pointdet['latitude'] = point.attrib['lat']
        pointdet['longitude'] = point.attrib['lon']
        for det in point:
            if re.match('.*time$', det.tag):
                pointdet['time'] = datetime.datetime.strptime(det.text, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S%Z')
            elif re.match('.*ele$', det.tag):
                pointdet['elevation'] = det.text
    
        resp = insertTrackDetails(pointdet,track)
        if 'error_code' in resp:
            return resp
    return {'message' : 'Track Details Inserted'}
     
        
def insertTrackDetails(detail,track):
    global summary
    trackdet = TrackDetails(
                    track = track,
                    time = detail['time'].lower(),
                    longitude = detail['longitude'],
                    latitude = detail['latitude'],
                    elevation = detail['elevation'],
                       )
    try:                
        trackdet.save()
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

    response = {'message' : (trackdet.id, ' Inserted'),  }
    return response

@csrf_exempt    
def users(request, end_path, resource_id):
    logger.info(requestDetails(request))

    if authorized(request) is False:
        resp = {
                'error_code' : 401,
                'error_message' : 'Not authorised' }
    else:
        if request.method == 'GET' and resource_id is not None:
            resp = getUser(request, resource_id)
        elif request.method == 'POST' and resource_id is None:
            resp = insertUser(request)
        else:
            resp = {
                    'error_code' : 501,
                    'error_message' : 'Method not supported' }

    if 'error_code' in resp:
        HttpResponse.status_code = resp['error_code']
    else:
        HttpResponse.status_code = 200    
    return JsonResponse(resp, safe=False)

def getUser(request, user_id):

    try:
        user = Users.objects.get(user_id=user_id.lower())
    except:
        error = {
                'error_code' : 404,
                'error_message' : 'Track not found' }
        return error
    payload = buildUserDict(user)
    return payload

def insertUser(request):

    payload = json.loads(request.body)
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

@csrf_exempt    
def images(request, end_path, resource_id):
    logger.info(requestDetails(request))

    if authorized(request) is False:
        resp = {
                'error_code' : 401,
                'error_message' : 'Not authorised' }
    else:
        if request.method == 'GET' and resource_id is not None:
            resp = getImage(request, resource_id)
        elif request.method == 'POST' and resource_id is None:
            resp = insertImage(request)
        else:
            resp = {
                    'error_code' : 501,
                    'error_message' : 'Method not supported' }

    if 'error_code' in resp:
        HttpResponse.status_code = resp['error_code']
    else:
        HttpResponse.status_code = 200    
    return JsonResponse(resp, safe=False)

def getImage(request, image_name):

    try:
        image = Images.objects.get(image_name=image_name.lower())
    except:
        error = {
                'error_code' : 404,
                'error_message' : 'Image not found' }
        return error
    payload = buildImageDict(image)
    return payload

def insertImage(request):

    payload = json.loads(request.body)
    image = Images(
                    image_name = payload['image_name'].lower(),
                    licence_no = payload['licence_no'],
                    file_type = payload['file_type'],
                    user_id = payload['user_id'],
                    created_on = payload['created_on'],
                    image = payload['image']
                      )
    try:                
        image.save()
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

    response = {'message' : (image.id, ' Inserted'),  }
    return response

def buildImageDict(image):
    image = {
            'id': image.id,
            'image_name' : image.image_name,
            'licence_no' : image.licence_no,
            'file_type' : image.file_type,
            'user_id' : image.user_id,
            'created_on' : image.created_on,
            'image' : image.image
        }
    return image

@csrf_exempt    
def login(request):
    logger.info(requestDetails(request))

    if request.method == 'POST':
        payload = json.loads(request.body)
        try:
            user = Users.objects.get(user_id=payload['user_id'].lower())
        except:
            resp = {
                    'error_code' : 401,
                    'error_message' : 'Password update failed' }
            HttpResponse.status_code = 401    
            return JsonResponse(resp, safe=False)

        if 'new_password' in payload:
            resp = changepassword(user, payload['password'], payload['new_password'])
        else:
            resp = checkpassword(user, payload['password'])
        try:                
            user.save()
        except ValidationError as e:
            resp = {
                    'error_code' : 400,
                    'error_message' : e.messages }
#            return error
        except IntegrityError as e:
            resp = {
                    'error_code' : 400,
                    'error_message' : e.__cause__.pgerror} 
#            return error
        except:
            resp = {
                    'error_code' : 500,
                    'error_message' : "Unexpected  Error"}
#            return error            
        
    else:
        resp = {
                'error_code' : 501,
                'error_message' : 'Method not supported' }

    if 'error_code' in resp:
        HttpResponse.status_code = resp['error_code']
    else:
        HttpResponse.status_code = 200
    return JsonResponse(resp, safe=False)

def checkpassword(user, password):
    if user.password != ''  and pbkdf2_sha256.verify(password, user.password):
        token = uuid.uuid4()
        user.token = token
        user.token_expiry = datetime.datetime.now() + \
                            datetime.timedelta(minutes=settings.TOKEN_EXPIRY)

        response = {'token' : token,
                    'message' : 'Logged In'  }
    else:
        response = {
                    'error_code' : 401,
                    'error_message' : 'Logon failed' }
    return response

def changepassword(user, old_password, new_password):
    if user.password == "":
        user.password = pbkdf2_sha256.hash(new_password)
    else:
        if pbkdf2_sha256.verify(old_password, user.password):
            user.password = pbkdf2_sha256.hash(new_password)
        else:   
            resp = {
                'error_code' : 401,
                'error_message' : 'Password update failed' }
            return resp
    response = {'message' : 'Password Changed',  }
    return response    

def authorized(request):
    global session
    auth = True

    try:
        user = Users.objects.get(token=request.META['HTTP_AUTHORIZATION'])
    except:
        auth = False
        
    if auth is True:
        if datetime.datetime.now() > user.token_expiry:
            auth = False
        else:
            session['user_id'] = user.user_id
    return auth

def requestDetails(request):
    return '{0} {1} {2}'.format(request.method, request.path, request.META['REMOTE_ADDR'])