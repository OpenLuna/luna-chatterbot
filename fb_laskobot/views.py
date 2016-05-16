# -*- coding: UTF-8 -*-
from django.views import generic
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
import json, requests, random, re
from django.views import generic
from .models import Person, Feed, Events, FbCard
from datetime import datetime
from luna_chatterbot.views import get_response
from django.conf import settings


class Botw(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == 'topaja':
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        print(incoming_message)
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                if 'message' in message.keys():
                    # Print the message to the terminal
                    print(message)
                    parseMessage(message)
        return HttpResponse()


def sendMessageToId(request, fb_id, message):
    post_facebook_message(fb_id, message)
    return HttpResponse()


def sendMessageToFeed(request, feed_name, message):
    feed = Feed.objects.filter(name=feed_name)
    if feed:
        count = sendToFeed(feed, message)
        return HttpResponse("Sporočilo je poslano "+str(count)+ "X.")
    else:
        return HttpResponse("Ni takiga feeda")
    

# what to do with message? Save/Get Person...
def parseMessage(message):
    print("parse")
    person = Person.objects.filter(fb_id=message['sender']['id'])
    if person:
        person = person[0]
    else:
        person = Person(fb_id=message['sender']['id'])
        person.save()
    if not  "text" in message['message'].keys():
        post_facebook_message(message['sender']['id'], "Ne razumem tvoje govorice :D")
        return
    if message['message']['text'][0] == "@":
        feed_register(person, message)
    elif message['message']['text'][0] == "#":
        feed_unregister(person, message)
    else:
        print "parse else"
        if FbCard.objects.filter(keyword=message['message']['text']):
            send_facebook_message_card(list(FbCard.objects.filter(keyword=message['message']['text'])), message['sender']['id'])
        else:
            response = get_response(message['sender']['id'], message['message']['text'])
            post_facebook_message(message['sender']['id'], response) 


#register on feed
def feed_register(person, message):
    feed_name = message['message']['text'][1:]
    if feed_name in person.reg_feeds.all().values_list("name", flat=True):
        post_facebook_message(message['sender']['id'], "Ti si že registriran v obvestila: " + feed_name)
    else:
        print("else")
        if feed_name in Feed.objects.all().values_list("name", flat=True):
            print("sdf")
            feed = Feed.objects.get(name=feed_name)
            person.reg_feeds.add(feed)
            post_facebook_message(message['sender']['id'], "Uspešno si se registriral na obvestila: " + feed_name)
        else:
            post_facebook_message(message['sender']['id'], "Obvestilo: " + feed_name + " ne obstaja.")


#Unregister from feed
def feed_unregister(person, message):
    print("register")
    feed_name = message['message']['text'][1:]
    print( feed_name)
    print( person.reg_feeds.all().values_list("name", flat=True))
    if feed_name in person.reg_feeds.all().values_list("name", flat=True):
        feed = Feed.objects.get(name=feed_name)
        person.reg_feeds.remove(feed)
        post_facebook_message(message['sender']['id'], "Uspešno smo te odjavili od obvestila: " + feed_name)
    else:
        print("second")
        if feed_name in Feed.objects.all().values_list("name", flat=True):
            print("a")
            post_facebook_message(message['sender']['id'], "V ta obvestila nisi prijvlen")
        else:
            print("b")
            post_facebook_message(message['sender']['id'], "Obvestilo " + feed_name + " ne obstaja")


# send message to fb user
def post_facebook_message(fbid, recevied_message):
    print( "post")
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token='+settings.FACEBOOK_SECRET
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":recevied_message}})
    requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)



#Cron job method for sending reminders for events
def sendEventCron():
    for event in Events.objects.filter(startTime__lte=datetime.now(), sent=False):
        sendToFeed(event.feed, event.message)
        event.sent = True
        event.save()


def sendToFeed(feed, message):
    count = 0
    for person in Person.objects.filter(reg_feeds=feed):
        post_facebook_message(person.fb_id, message)
        count+=1
    return count

def test_send_buttons():
    buttons = [{
                "type":"web_url",
                "url":"http://www.lasko.eu/en/",
                "title":"Glej naš pejđ"
              },
              {
                "type":"postback",
                "title":"Naroči pivo",
                "payload":"Narocu bi pivo."
              },
              {
                "type":"postback",
                "title":"Zavriskaj",
                "payload":"vriskam"
              }]
    """send_facebook_message_card("JoJo kake joške", [{
                               "type":"postback",
                               "title":"Primo jo za joško",
                               "payload":"slati"}], 1088696307862513)"""
    send_facebook_message_buttons("Ka boš pil pir al kwa?", buttons, 1088696307862513)
    send_facebook_message_card(list(FbCard.objects.all()[:2]),1088696307862513)


def send_facebook_message_buttons(text, buttons, fbid):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token='+settings.FACEBOOK_SECRET
    response_msg = json.dumps({"recipient":{"id":fbid}, 
                                "message":{
                                "attachment":{
                                  "type":"template",
                                  "payload":{
                                    "template_type":"button",
                                    "image_url": "http://img2.timeinc.net/people/i/2015/news/150831/pamela-anderson-01-660.jpg",
                                    "text":text,
                                    "buttons":[button for button in buttons]
                                  }
                                }
                              }})
    print response_msg
    requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)

def send_facebook_message_card(cards, fbid):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token='+settings.FACEBOOK_SECRET
    response_msg = json.dumps({"recipient":{"id":fbid}, 
                                "message":{
                                "attachment":{
                                  "type":"template",
                                  "payload":{
                                    "template_type":"generic",
                                    "elements":[card.getDictionary() for card in cards],
                                  }
                                }
                              }})
    print response_msg
    requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)



#    image = "http://img2.timeinc.net/people/i/2015/news/150831/pamela-anderson-01-660.jpg"