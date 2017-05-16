from django.http import JsonResponse

import json

import process_tasks as tasks


def get_scores(request):
    '''
    Reads file/db for reviews and ratings for a hotel.
    '''
    if request.method == 'POST':
        file_data = request.FILES.get('file')
        data = json.load(file_data)
        
        hotel = tasks.get_hotel_info(data['HotelInfo'])
        tasks.update_hotel_reviews(data, hotel)

    return JsonResponse({'status': 200})
