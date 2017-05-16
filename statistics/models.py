from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

import app_settings


class HotelInfo(models.Model):
    '''
    Stores basic information of Hotel
    '''
    hotel_id = models.CharField(max_length=64)
    name = models.CharField(max_length=512)
    url = models.CharField(max_length=256)
    image_url = models.CharField(max_length=256)
    address_street = models.CharField(max_length=64, blank=True, null=True)
    address_locality = models.CharField(max_length=64, blank=True)
    address_region = models.CharField(max_length=64, blank=True)
    address_pincode = models.IntegerField(default=0)
    price = models.CharField(max_length=16, blank=True, null=True)


class HotelReviews(models.Model):
    '''
    Stores review details (except ratings) for each review for a hotel
    '''
    hotel = models.ForeignKey(HotelInfo)
    review_id = models.CharField(max_length=64)
    title = models.CharField(max_length=128)
    author = models.CharField(max_length=128)
    author_location = models.CharField(max_length=128)
    review_date = models.DateTimeField(default=timezone.now())
    content = models.CharField(max_length=5126)


class HotelRatings(models.Model):
    '''
    Stores rating information for hotels (on a scale of 5)
    '''
    hotel = models.ForeignKey(HotelInfo)
    review = models.ForeignKey(HotelReviews)
    topic = models.CharField(max_length=64)
    score = models.IntegerField(default=0,
                                validators=[MaxValueValidator(5),
                                            MinValueValidator(0)])
    class Meta:
        unique_together = ('hotel', 'review', 'topic')


class SemanticsInfo(models.Model):
    '''
    Stores information of positive/negative semantics and/or intensifier
    '''
    phrase = models.CharField(max_length=32)
    semantic_type = models.CharField(max_length=16,
                                     choices=app_settings.SEMANTIC_TYPES)
    value = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
