from django.db.models import Avg, Max, Min

from models import HotelRatings

def get_analytics(**kwargs):
    analytics_dict = {}
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
