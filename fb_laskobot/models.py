# -*- coding: UTF-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.

@python_2_unicode_compatible
class Feed(models.Model):
	name = models.CharField(max_length=30)

	def __str__(self):
		return self.name


@python_2_unicode_compatible
class Person(models.Model):
	fb_id = models.CharField(max_length=30)
	reg_feeds = models.ManyToManyField(Feed)

	def __str__(self):
		return self.fb_id


@python_2_unicode_compatible
class Events(models.Model):
	startTime = models.DateTimeField()
	message = models.TextField(max_length=512)
	feed = models.ForeignKey("Feed")
	sent = models.BooleanField(default=False)

	def __str__(self):
		return self.feed + "_" + message[:20]



#Facebook messageing
BUTTON_TYPES = (
    ('web_url', 'web_url'),
    ('postback', 'postback'),
)

@python_2_unicode_compatible
class FbButton(models.Model):
	button_type = models.CharField(max_length=16,
                                   choices=BUTTON_TYPES,
                                   default="postback")
	title = models.CharField(max_length=128)
	url = models.URLField(max_length=128, blank=True, null=True)
	payload = models.CharField(max_length=128, blank=True, null=True)

	def __str__(self):
		return self.title

@python_2_unicode_compatible
class FbCard(models.Model):
	title = models.CharField(max_length=128, blank=True, null=True)
	subtitle = models.CharField(max_length=128, blank=True, null=True)
	image = models.URLField(max_length=128, blank=True, null=True)
	buttons = models.ManyToManyField(FbButton)

	keyword = models.CharField(max_length=128, blank=True, null=True)

	def __str__(self):
		return self.title

	def getDictionary(self):
		outDict = {}
		if self.title:
			outDict.update({"title":self.title})
		if self.subtitle:
			outDict.update({"subtitle":self.subtitle})
		if self.image:
			outDict.update({"image_url":self.image})
		if self.buttons.all():
			outDict.update({"buttons":[]})
			tempButton = {}
			for button in self.buttons.all():
				tempButton.update({"type":button.button_type})
				tempButton.update({"title":button.title})
				if button.url:
					tempButton.update({"url":button.url})
				if button.payload:
					tempButton.update({"payload":button.payload})

				outDict["buttons"].append(tempButton)
				tempButton = {}
		return outDict

