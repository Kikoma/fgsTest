from django.shortcuts import render
from .forms import MainForm
from django.forms.utils import ErrorList
from .tools.geodata import get_geo_by_address, get_cities_in_radius, get_map


def index(request):
    if request.method == 'POST':
        form = MainForm(request.POST)
        if form.is_valid():
            # Получили данные из формы. Обрабатываем, рисуем карту и возвращаем
            address = form.cleaned_data['address']
            try:
                # todo раскоментировать (Экономим бесплатные запросы на дадата)
                geo_data = get_geo_by_address(address)
                # geo_data = {
                #     'result': 'Алтайский край, г Бийск',
                #     'address': 'Алтайский край, г Бийск',
                #     'geo_lat': '52.5393864',
                #     'geo_lon': '85.2138453'
                # }
            except:
                # todo Что делаем если ошибка при запросе дадата?
                print('Error dadata!!!')
                geo_data = {
                    'result': 'Алтайский край, г Бийск',
                    'address': 'Алтайский край, г Бийск',
                    'geo_lat': '52.5393864',
                    'geo_lon': '85.2138453'
                }
            data = dict()
            if geo_data['result']:
                # запоминаем session для последующего формирование имени картинки с картой
                if not request.session.session_key:
                    request.session.cycle_key()
                data['session'] = request.session.session_key

                form.set_address(geo_data['result'])
                address = geo_data['result']
                radius = form.cleaned_data['radius']

                data['address'] = address
                data['radius'] = radius
                data['geo_lat'] = float(geo_data['geo_lat'])
                data['geo_lon'] = float(geo_data['geo_lon'])

                if radius > 0:
                    # Получаем список городов, которые попадают в радиус
                    data['cities'] = get_cities_in_radius(data)

                # формируем карту
                img = get_map(data)
            else:
                form._errors['address'] = ErrorList([u'Ошибка! Ничего не найдено! Проверьте исходные данные'])
                data['error'] = True
            return render(request, 'maptest/main.html', {'form': form, 'image': 'some_image', 'data': data, 'img': img})
    else:
        form = MainForm()

    return render(request, 'maptest/main.html', {'form': form})
