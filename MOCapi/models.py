from django.db import models

class Tracks(models.Model):
    user_id = models.CharField(max_length=250)
    track_name = models.CharField(max_length=30,null=True)
    created_on = models.DateField()
    
class Users(models.Model):
    user_id = models.CharField(max_length=250)
    name = models.CharField(max_length=250)
    created_on = models.DateField()
    password = models.CharField(max_length=250)
    token = models.CharField(max_length=250)
    token_expiry = models.DateTimeField()
 
