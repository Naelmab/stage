from django.db import models

class Projet(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    image_url = models.CharField(max_length=2000)