from django.db import models

# Create your models here.
class ChatHistory(models.Model):
	fb_id = models.CharField(max_length=32)
	text = models.CharField(max_length=256, blank=True, null=True)
	request = models.BooleanField(default=True)
	isQuestion = models.BooleanField(default=True)
