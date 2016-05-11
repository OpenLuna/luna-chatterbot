from django.db import models

# Create your models here.

class Feed(models.Model):
	name = models.CharField(max_length=30)


class Person(models.Model):
	fb_id = models.CharField(max_length=30)
	reg_feeds = models.ManyToManyField(Feed)


class Events(models.Model):
	startTime = models.DateTimeField()
	message = models.TextField(max_length=512)
	feed = models.ForeignKey("Feed")
	sent = models.BooleanField(default=False)
