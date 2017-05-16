from django.http import JsonResponse

import json

import process_tasks as tasks
import analytic_tasks as analytics


def get_scores(request, topic=''):
    '''
    Reads file/db for reviews and ratings for a hotel.
    '''
    if request.method == 'POST':
        file_data = request.FILES.get('file')
        if not file_data:
            return JsonResponse({'Status': 400, 'Message': 'Missing File.'})
        data = json.load(file_data)
        
        hotel = tasks.get_hotel_info(data['HotelInfo'])
        tasks.update_hotel_reviews(data, hotel)
        if topic:
            params = { 'topic': topic }
        else:
            params = {}
        resp = analytics.get_analytics(**params)
        if not resp:
            return JsonResponse({'Status': 404, 'Message': 'Invalid topic requested'})
    else:
        return JsonResponse({'Status': 405, 'Message': 'Invalid GET request.'})

    return JsonResponse(resp)
