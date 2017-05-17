from django.db.models import Avg, Max, Min
from itertools import product

from models import HotelRatings

import re


def get_analytics(**kwargs):
    analytics_dict = {}
    if 'topic' in kwargs.keys():
        kwargs['topic'] = get_matching_string(kwargs['topic'])
    objects = HotelRatings.objects.filter(**kwargs).values('hotel__name', 'topic'
        ).annotate(Avg('score'), Max('score'), Min('score'))
    for obj in objects:
        if obj['topic'] not in analytics_dict.keys():
            analytics_dict[obj['topic']] = []
        score_dict = {}
        score_dict['hotel_name'] = obj['hotel__name']
        score_dict['avg'] = round(obj['score__avg'], 1)
        score_dict['max'] = round(obj['score__max'], 1)
        score_dict['min'] = round(obj['score__min'], 1)
        analytics_dict[obj['topic']].append(score_dict)
    return analytics_dict


def get_matching_string(topic):
    from nltk.corpus import wordnet as wn

    keys = list(HotelRatings.objects.all().values_list('topic', flat=True).distinct())
    init_max_score = 0
    new_topic = topic
    for key in keys:
        if topic.lower() in key.lower():
            topic = key

    if topic not in keys:
        maxscore = 0
        for word in keys:
            sem1, sem2 = wn.synsets(topic), wn.synsets(word)
            for i,j in list(product(*[sem1,sem2])):
                score = i.wup_similarity(j)
                maxscore = score if maxscore < score else maxscore
            if maxscore >= 0.75 and init_max_score < maxscore:
                init_max_score = maxscore
                new_topic = word
        topic = new_topic

    return topic
