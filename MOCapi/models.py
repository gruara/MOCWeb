from django.db import models

class Tracks(models.Model):
    user_id = models.CharField(max_length=250)
    track_name = models.CharField(max_length=30,null=True)
    created_on = models.DateField()
    
