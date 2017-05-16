from django.http import JsonResponse
# from django.core.exceptions import ValidationError
from django.db import IntegrityError
from dateutil import parser

from models import HotelInfo, HotelReviews, HotelRatings

import json
import unicodedata


def get_scores(request):
    '''
    Reads file/db for reviews and ratings for a hotel.
    '''
    if request.method == 'POST':
        file_data = request.FILES.get('file')
        data = json.load(file_data)
        
        hotel = get_hotel_info(data['HotelInfo'])
        update_hotel_reviews(data, hotel)

    return JsonResponse({'status': 200})


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
        print "Date: ", review['Date']
        review_date = parser.parse(review['Date'])
        print "RDate: ", review_date

        obj = HotelReviews.objects.get_or_create(
            hotel_id=hid, review_id=rid, title=title, author=author,
            author_location=location, review_date=review_date, content=content)
        update_ratings(review['Ratings'], hid, obj[0].id)


def update_ratings(ratings, hid, rid):
    entries = []
    for key, value in ratings.iteritems():
        val = float(str(value))
        entry = HotelRatings(hotel_id=hid, review_id=rid, topic=key, score=val)
        entries.append(entry)
    try:
        HotelRatings.objects.bulk_create(entries)
    except IntegrityError as e:
        print "Validation Error raised"
