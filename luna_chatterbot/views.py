# -*- coding: UTF-8 -*-
from django.views.generic import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from pymongo import MongoClient
from bson.code import Code
from .models import ChatHistory
from fb_laskobot.utils import normalize_sentence

dbClient = MongoClient('localhost', 27017)
learn=True
db = dbClient.bot_database

mapper = Code("""
	function(){
						emit(this.request, 1);
				}
""")
reducer = Code("""
    function(key, value) { return null; }
""")


class ChatterBotView(View):

    def get(self, request, *args, **kwargs):
        data = {
            'detail': 'You should make a POST request to this endpoint.'
        }

        # Return a method not allowed response
        return JsonResponse(data, status=405)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        input_statement = request.POST.get('text')

        response_data = get_response("1", input_statement)

        return JsonResponse(response_data)


def get_response(fb_id, text):
	print "finding"
	mr = db.bot.map_reduce(mapper, reducer, out = {'inline' : 1}, full_response = True)
	keys = [item["_id"] for item in mr["results"]]

	ntext, isQuestion = normalize_sentence(text)
	if learn:
		if ChatHistory.objects.filter(fb_id=str(fb_id)) and list(ChatHistory.objects.filter(fb_id=str(fb_id)).order_by("id"))[-1].text == None:
			#print "Sharni " + text.decode("utf-8") + "za response od prejsnega"
			if ntext[0] == "x":
				ChatHistory(fb_id=str(fb_id), text="x", request=False).save()
				return "Če mi nočeš pomagat pa nič :("
			req = list(ChatHistory.objects.all().order_by("id"))[-2]
			pair = {"request":req.text, "response": text, "question": req.isQuestion}
			db.bot.insert_one(pair)
			ChatHistory(fb_id=str(fb_id), text=text, request=False).save()
			return "Zapomnil sem si tvoj predlog. Nadaljuj s pogovorm."
		else:
			ChatHistory(fb_id=str(fb_id), text=" ".join(ntext), request=True, isQuestion=isQuestion).save()
	if " ".join(ntext) in keys:
		resp = db.bot.find_one({'request': " ".join(ntext)})["response"]
		ChatHistory(fb_id=str(fb_id), text=resp, request=False).save()
		return resp
	else:
		ChatHistory(fb_id=str(fb_id), text=None, request=False).save()

		return "Na tvoj stavek se še ne znam odzivat. Predlagaj mi kaj naj rečem."


