from django.db import IntegrityError
from dateutil import parser

import unicodedata
import re

from models import HotelInfo, HotelReviews, HotelRatings, SemanticsInfo
import app_settings as aps


positives = {}
negatives = {}
intensifiers = {}

def get_hotel_info(hotel_info):
    street = ""
    locality = ""
    region = ""
    postal = 0
    address = unicodedata.normalize('NFKD', hotel_info['Address']
        ).encode('ascii','ignore')
    if('property="v:street-address"' in address):
        street = address.split('property="v:street-address">', 1
            )[1].partition('</span>')[0]
    if('property="v:locality"' in address):
        locality = address.split('property="v:locality">', 1
            )[1].partition('</span>')[0]
    if('property="v:region"' in address):
        region = address.split('property="v:region">', 1
            )[1].partition('</span>')[0]
    if('property="v:postal-code"' in address):
        postal = int(address.split('property="v:postal-code">', 1
            )[1].partition('</span>')[0])

    name = hotel_info['Name']
    hid = hotel_info['HotelID']
    price = hotel_info['Price']
    url = hotel_info['HotelURL']
    img = hotel_info['ImgURL']
    obj = HotelInfo.objects.get_or_create(name=name, hotel_id=hid, url=url,
                                          image_url=img, address_street=street,
                                          address_locality=locality,
                                          address_region=region,
                                          address_pincode=postal, price=price)
    return obj[0].id


def update_hotel_reviews(data, hid):
    for review in data['Reviews']:
        author = review['Author']
        location = review['AuthorLocation']
        rid = review['ReviewID']
        title = review['Title']
        content = review['Content']
        review_date = parser.parse(review['Date'])

        obj = HotelReviews.objects.get_or_create(
            hotel_id=hid, review_id=rid, title=title, author=author,
            author_location=location, review_date=review_date, content=content)
        update_ratings(review['Ratings'], content, hid, obj[0].id)


def update_ratings(ratings, content, hid, rid):
    entries = []
    for key, value in ratings.iteritems():
        val = float(value)
        entry = HotelRatings(hotel_id=hid, review_id=rid, topic=key, score=val)
        entries.append(entry)
    if content:
        entry = HotelRatings(hotel_id=hid, review_id=rid,
                             topic=aps.CONTENT_RATING_KEY,
                             score=get_intensified_score(content))
        entries.append(entry)

    try:
        HotelRatings.objects.bulk_create(entries)
    except IntegrityError as e:
        keys = ratings.keys()
        keys.append(aps.CONTENT_RATING_KEY)
        HotelRatings.objects.filter(hotel_id=hid, review_id=rid, topic__in=keys).delete()
        HotelRatings.objects.bulk_create(entries)


def get_intensified_score(content):
    points = 0
    if not positives or negatives or intensifiers:
        get_semantics()

    data = re.findall(r"[\w']+", content)
    for prev, word in zip(data, data[1:]):
        if word in positives.keys() and prev in intensifiers.keys():
            points += positives[word]*intensifiers[prev]
        elif word in negatives.keys() and prev in intensifiers.keys():
            points = points - negatives[word]*intensifiers[prev]
        elif word in positives:
            points += positives[word]
        elif word in negatives:
            points = points - negatives[word]

    return points


def get_semantics():
    semantics = SemanticsInfo.objects.all()
    for sem in semantics:
        if sem.semantic_type == 'Positive':
            positives[sem.phrase] = sem.value
        elif sem.semantic_type == 'Negative':
            negatives[sem.semantic_type] = sem.value
        elif sem.semantic_type == 'Intensifier':
            intensifiers[sem.phrase] = sem.value
