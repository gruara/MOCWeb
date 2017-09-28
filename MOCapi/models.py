from django.db import models

class Tracks(models.Model):
    user_id = models.CharField(max_length=250)
    track_name = models.CharField(max_length=30,null=True)
    created_on = models.DateField()
    
class Users(models.Model):
    user_id = models.CharField(max_length=250,db_index=True,unique=True)
    name = models.CharField(max_length=250)
    created_on = models.DateField()
    password = models.CharField(max_length=250)
    token = models.CharField(max_length=250,db_index=True,unique=False)
    token_expiry = models.DateTimeField()

class TrackDetails(models.Model):
    track_id = models.IntegerField()
    time = models.DateTimeField()
    longitude = models.CharField(max_length=250)
    latitude = models.CharField(max_length=250)
    elevation = models.CharField(max_length=250)
