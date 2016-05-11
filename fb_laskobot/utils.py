# -*- coding: UTF-8 -*-
import lemmagen.lemmatizer
import re
from lemmagen.lemmatizer import Lemmatizer
import slopos
lemmatizer = Lemmatizer(dictionary=lemmagen.DICTIONARY_SLOVENE)

def sentenceToDict(sentence):
	sentence = normalize_sentence(sentence)
	lem_sentence = lemmatize_words(sentence)
	tags = slopos.tag(lem_sentence)
	return [{"original": word[0], "lema": word[1], "tag": word[2]}for word in zip(sentence, lem_sentence, tags)]

def normalize_sentence(sentence):
	q = False
	if "?" in sentence:
		q = True
	sentence = re.sub('[!,?.]', '', sentence)
	sentence = sentence.lower()
	return sentence.split(" "), q

def lemmatize_words(words):
	return [lemmatizer.lemmatize(word) for word in words]
