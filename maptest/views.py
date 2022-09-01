from django.shortcuts import render
from .forms import MainForm
from django.forms.utils import ErrorList
from .tools.geodata import get_geo_by_address, get_cities_in_radius, get_map
import logging


logger = logging.getLogger(__name__)


# async
def index(request):
    if request.method == 'POST':
        form = MainForm(request.POST)
        if form.is_valid():
            # Получили данные из формы. Обрабатываем, рисуем карту и возвращаем
            address = form.cleaned_data['address']
            geo_data = {'result': None}
            data = {'error': False, 'error_message': []}
            img = None
            try:
                geo_data = get_geo_by_address(address)
                # todo To delete in final realize
                # Экономим бесплатные запросы на дадата
                # geo_data = {'source': 'Москва', 'result': 'г Москва', 'postal_code': '101000', 'country': 'Россия',
                #             'country_iso_code': 'RU', 'federal_district': 'Центральный',
                #             'region_fias_id': '0c5b2444-70a0-4932-980c-b4dc0d3f02b5',
                #             'region_kladr_id': '7700000000000', 'region_iso_code': 'RU - MOW',
                #             'region_with_type': 'г Москва', 'region_type': 'г',
                #             'region_type_full': 'город', 'region': 'Москва', 'area_fias_id': None,
                #             'area_kladr_id': None, 'area_with_type': None, 'area_type': None, 'area_type_full': None,
                #             'area': None, 'city_fias_id': None, 'city_kladr_id': None, 'city_with_type': None,
                #             'city_type': None, 'city_type_full': None, 'city': None, 'city_area': None,
                #             'city_district_fias_id': None, 'city_district_kladr_id': None,
                #             'city_district_with_type': None, 'city_district_type': None,
                #             'city_district_type_full': None, 'city_district': None, 'settlement_fias_id': None,
                #             'settlement_kladr_id': None, 'settlement_with_type': None, 'settlement_type': None,
                #             'settlement_type_full': None, 'settlement': None, 'street_fias_id': None,
                #             'street_kladr_id': None, 'street_with_type': None, 'street_type': None,
                #             'street_type_full': None, 'street': None, 'house_fias_id': None, 'house_kladr_id': None,
                #             'house_cadnum': None, 'house_type': None, 'house_type_full': None, 'house': None,
                #             'block_type': None, 'block_type_full': None, 'block': None, 'entrance': None,
                #             'floor': None, 'flat_fias_id': None, 'flat_cadnum': None, 'flat_type': None,
                #             'flat_type_full': None, 'flat': None, 'flat_area': None, 'square_meter_price': None,
                #             'flat_price': None, 'postal_box': None, 'fias_id': '0c5b2444-70a0-4932-980c-b4dc0d3f02b5',
                #             'fias_code': '77000000000000000000000', 'fias_level': '1', 'fias_actuality_state': '0',
                #             'kladr_id': '7700000000000', 'capital_marker': '0', 'okato': '45000000000',
                #             'oktmo': '45000000', 'tax_office': '7700', 'tax_office_legal': '7700', 'timezone': 'UTC + 3',
                #             'geo_lat': '55.7540471', 'geo_lon': '37.620405', 'beltway_hit': None,
                #             'beltway_distance': None, 'qc_geo': 4, 'qc_complete': 3, 'qc_house': 10, 'qc': 0,
                #             'unparsed_parts': None, 'metro': None
                #             }
            except Exception as e:
                logger.warning(f'Error get data from dadata! {address=} Err={e}')
                data['error'] = True
                data['error_message'].append('Ошибка доступа к сервису геокодирования')
            if not data['error'] and geo_data['result']:
                # запоминаем session для последующего формирование имени картинки с картой
                if not request.session.session_key:
                    request.session.cycle_key()
                data['session'] = request.session.session_key

                form.set_address(geo_data['result'])
                address = geo_data['result']
                radius = form.cleaned_data['radius']
                if not radius:
                    radius = 0

                data['address'] = address
                data['radius'] = radius
                data['geo_lat'] = float(geo_data['geo_lat'])
                data['geo_lon'] = float(geo_data['geo_lon'])

                if radius > 0:
                    # Получаем список городов, которые попадают в радиус
                    # await
                    data['cities'] = get_cities_in_radius(data)
                # формируем карту
                print('try to get image...')
                # await
                img = get_map(data)
            else:
                if not geo_data['result']:
                    data['error_message'].append('Информация по адресу не найдена! Проверьте исходные данные')
                data['error'] = True
            return render(request, 'maptest/main.html', {'form': form, 'image': 'some_image', 'data': data, 'img': img})
    else:
        form = MainForm()

    return render(request, 'maptest/main.html', {'form': form})
