from django.http import JsonResponse

import json

import process_tasks as tasks
import analytic_tasks as analytics


def get_scores(request, topic=''):
    '''
    Reads file/db for reviews and ratings for a hotel.
    '''
    if topic:
        params = { 'topic': topic }
    else:
        params = {}

    if request.method == 'POST':
        file_data = request.FILES.get('file')
        if not file_data:
            return JsonResponse({'Status': 400, 'Message': 'Missing File.'}, status=400)
        try:
            data = json.load(file_data)
        except Exception as e:
            return JsonResponse({'Status': 400, 'Message': 'Invalid file'}, status=400)
        
        hotel = tasks.get_hotel_info(data['HotelInfo'])
        tasks.update_hotel_reviews(data, hotel)

        resp = analytics.get_analytics(**params)
    else:
        resp = analytics.get_analytics(**params)

    if not resp:
            return JsonResponse({'Status': 404, 'Message': 'Invalid topic requested'}, status=404)

    return JsonResponse(resp)
