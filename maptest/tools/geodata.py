import io
import math
import urllib.request
from math import pi, cos, sin, sqrt, atan2
import random

# import asyncio
# import aiohttp
# from asgiref.sync import sync_to_async

from django.conf import settings
import logging

import mercantile
from cairo import ImageSurface, FORMAT_ARGB32, Context

from maptest.models import City
from maptest.tools.dadata import Dadata

logger = logging.getLogger(__name__)

EARTH_RADIUS = 6372795
KM_IN_GRADUS_OF_MERIDIAN = 111.1
KM_IN_GRADUS_OF_0_PARALLEL = 111.3

# добавочный процент к радиусу для формирование полей на карте
MAP_MARGIN_FIELD = 20
# масштаб карты
MAP_ZOOM = 8
# Расстояние в км от центра до края карты если не задан радиус
MAP_DEFAULT_FIELD_NO_RADIUS = 50


def scale(radius):
    """
    Высчитываем масштаб тэйлов от радиуса по уравнению прямой через две точки
    и ограничиваем в рамках от 5 до 10.
    значения подлежат регулировке для получения наилучшего результата :)
    """
    x1, y1 = 20, 11
    x2, y2 = 150, 8
    k = (y2 - y1) / (x2 - x1)
    res = round(k * (radius - x1) + y1)
    res = max(5, res)
    res = min(10, res)
    return int(res)


def get_geo_by_address(address: str):
    """
    запрос к dadata через API
    """
    token = settings.DADATA_API_KEY
    secret = settings.DADATA_SECRET_KEY
    dadata = Dadata(token, secret)
    return dadata.clean("address", address)


def calculate_distance_by_geo(a_lat, a_lon, b_lat, b_lon):
    """
    Вычисляем расстояние между двумя точками A и B, заданные гео координатами
    :param a_lat: широта точки А
    :param a_lon: долгота точки А
    :param b_lat: широта точки В
    :param b_lon: долгота точки В
    :return: Расстояние между точками в километрах
    """

    # переводим координаты в радианы
    lat1 = a_lat * pi / 180
    lat2 = b_lat * pi / 180
    long1 = a_lon * pi / 180
    long2 = b_lon * pi / 180

    # косинусы и синусы широт и разницы долгот
    cl1 = cos(lat1)
    cl2 = cos(lat2)
    sl1 = sin(lat1)
    sl2 = sin(lat2)
    delta = long2 - long1
    cdelta = cos(delta)
    sdelta = sin(delta)

    # вычисляем длину большого круга
    y = sqrt((cl2 * sdelta) ** 2 + (cl1 * sl2 - sl1 * cl2 * cdelta) ** 2)
    x = sl1 * sl2 + cl1 * cl2 * cdelta

    ad = atan2(y, x)
    dist = ad * EARTH_RADIUS

    return int(dist / 1000)


def get_AC_geo(center_geo_lat, center_geo_lon, radius):
    """
    Получаем координаты двух вершин AC квадрата ABCD (точнее трапеции), в которой вписывается круг с нашим радиусом в км.
    Точка А - северо-западнее от центральной точки
    Точка С - юго-восточнее от центральной точки

    :return: (A_lat, A_lon, C_lat, C_lon)
    """
    a_lat = center_geo_lat + radius / KM_IN_GRADUS_OF_MERIDIAN
    a_lon = center_geo_lon - radius / (cos(a_lat * pi / 180) * KM_IN_GRADUS_OF_0_PARALLEL)
    c_lat = center_geo_lat - radius / KM_IN_GRADUS_OF_MERIDIAN
    c_lon = center_geo_lon + radius / (cos(c_lat * pi / 180) * KM_IN_GRADUS_OF_0_PARALLEL)

    return (a_lat, a_lon, c_lat, c_lon)


# @sync_to_async
def get_cities_in_radius(*args):
    """
    Получаем список городов, которые попадают в радиус от центральной точки.
    город в радиусе 10 км от заданной точки в список не попадает

    передаваемые параметры:
    radius
    center_geo_lat
    center_geo_lon
    """
    radius = args[0]['radius']
    center_geo_lat = float(args[0]['geo_lat'])
    center_geo_lon = float(args[0]['geo_lon'])

    #  A ---------- B
    #  |            |
    #  |            |
    #  |<-r->O <-r->|
    #  |            |
    #  |            |
    #  D ---------- C

    # Получаем гео координаты вершин квадрата(трапеции) AC
    ac = get_AC_geo(center_geo_lat, center_geo_lon, radius)

    # Отбираем города которые попадают по координатам в наш квадрат
    cities = City.objects.filter(
        geo_lat__gt=ac[2],
        geo_lat__lt=ac[0],
        geo_lon__gt=ac[1],
        geo_lon__lt=ac[3]
    )
    # Отбираем города которые попадают в заданный радиус
    # и формируем результат
    res_cities = [{'id': o.pk, 'city': o.city, 'city_type': o.city_type, 'geo_lat': o.geo_lat, 'geo_lon': o.geo_lon}
                  for o in cities
                  if 10 <= calculate_distance_by_geo(center_geo_lat, center_geo_lon, float(o.geo_lat),
                                                     float(o.geo_lon)) <= radius
                  ]
    return res_cities


def get_img_coors_by_geo_cors(geo_lat, geo_lon, image):
    """
    Получаем координаты точки в пикселях на изображении карты. Точка задана гео координатами
    :param geo_lat:
    :param geo_lon:
    :param image:
    :return: x,y
    """
    img_w = image['size']['width']
    img_h = image['size']['height']
    img_geo_w = abs(image['bounds']['east'] - image['bounds']['west'])
    img_geo_h = abs(image['bounds']['south'] - image['bounds']['north'])
    kx = img_w / img_geo_w
    ky = img_h / img_geo_h

    # todo проверить работу на всей Земле, есть подозрения, что в разных полушариях работать не будет
    # Спешу, поэтому оставляю так. На территории России работает прекрасно
    res_x = int((geo_lon - image['bounds']['west']) * kx)
    res_y = int(abs(image['bounds']['north'] - geo_lat) * ky)
    return (res_x, res_y)


# async def get_img_tile(session, url, t):
#     async with session.get(url) as res:
#         data_res = await res.read()
#         # todo Добавить в ответ статус, вдруг вернулась не картинка, а, например, 403 ...
#     return (data_res, t)

# async
def get_map(data):
    """
    Рисуем карту
    Необходимые входные данные в data:
    geo_lat, geo_lon,
    radius,
    cities - список городов

    :return:
    """
    if data['radius'] > 0:
        radius = int(data['radius'] * (1 + MAP_MARGIN_FIELD / 100))
    else:
        radius = MAP_DEFAULT_FIELD_NO_RADIUS

    north, west, south, east = get_AC_geo(data['geo_lat'], data['geo_lon'], radius)

    tiles = list(mercantile.tiles(west, south, east, north, scale(radius)))

    min_x = min([t.x for t in tiles])
    min_y = min([t.y for t in tiles])
    max_x = max([t.x for t in tiles])
    max_y = max([t.y for t in tiles])

    tile_size = (256, 256)
    map_image = ImageSurface(
        FORMAT_ARGB32,
        tile_size[0] * (max_x - min_x + 1),
        tile_size[1] * (max_y - min_y + 1)
    )

    ctx = Context(map_image)

    # # ********* ассинхронная загрузка тайлов
    # не работает, т.к. сервер возвращает: Access denied. See https://operations.osmfoundation.org/policies/tiles/
    # actions = []
    # async with aiohttp.ClientSession() as session:
    #     for t in tiles:
    #         server = random.choice(['a', 'b', 'c'])
    #         url = 'https://{server}.tile.openstreetmap.org/{zoom}/{x}/{y}.png'.format(
    #             server=server,
    #             zoom=t.z,
    #             x=t.x,
    #             y=t.y
    #         )
    #         actions.append(asyncio.ensure_future(get_img_tile(session, url, t)))
    #
    #     img_tiles_res = await asyncio.gather(*actions)
    #
    #     for img_tile in img_tiles_res:
    #         img_data, t = img_tile
    #         img = ImageSurface.create_from_png(io.BytesIO(img_data))
    #         ctx.set_source_surface(
    #             img,
    #             (t.x - min_x) * tile_size[0],
    #             (t.y - min_y) * tile_size[0]
    #         )
    #         ctx.paint()
    # # *********
    # ============ Синхронный
    for t in tiles:
        server = random.choice(['a', 'b', 'c'])
        url = 'https://{server}.tile.openstreetmap.org/{zoom}/{x}/{y}.png'.format(
            server=server,
            zoom=t.z,
            x=t.x,
            y=t.y
        )
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
        response = urllib.request.urlopen(req)
        img = ImageSurface.create_from_png(io.BytesIO(response.read()))

        ctx.set_source_surface(
            img,
            (t.x - min_x) * tile_size[0],
            (t.y - min_y) * tile_size[0]
        )
        ctx.paint()
    # ============

    image = {
        'bounds': {
            "west": min([mercantile.bounds(t).west for t in tiles]),
            "east": max([mercantile.bounds(t).east for t in tiles]),
            "south": min([mercantile.bounds(t).south for t in tiles]),
            "north": max([mercantile.bounds(t).north for t in tiles]),
        },
        'size': {
            'width': map_image.get_width(),
            'height': map_image.get_height()
        }
    }

    if data['radius'] > 0:
        # рисуем радиус
        center_x, center_y = get_img_coors_by_geo_cors(data['geo_lat'], data['geo_lon'], image)
        # получаем радиус для карты в пикселях
        ac = get_AC_geo(data['geo_lat'], data['geo_lon'], data['radius'])
        x, y = get_img_coors_by_geo_cors(data['geo_lat'], ac[1], image)
        img_radius = center_x - x

        # радиус
        ctx.set_line_width(1)
        ctx.set_source_rgba(0.2, 0.2, 0.7, 0.2)
        ctx.arc(center_x, center_y, img_radius, 0, 2 * math.pi)
        ctx.stroke_preserve()
        ctx.fill()
        # выделяем центр
        ctx.set_line_width(6)
        ctx.set_source_rgba(0.2, 0.2, 0.7, 0.6)
        ctx.arc(center_x, center_y, 5, 0, 2 * math.pi)
        ctx.stroke_preserve()
        ctx.fill()

        # отмечаем города
        for city in data['cities']:
            center_x, center_y = get_img_coors_by_geo_cors(float(city['geo_lat']), float(city['geo_lon']), image)
            ctx.set_line_width(6)
            ctx.set_source_rgba(0.7, 0.2, 0.2, 0.6)
            ctx.arc(center_x, center_y, 5, 0, 2 * math.pi)
            ctx.stroke_preserve()
            ctx.fill()

    # todo сделать центровку карты по точке
    filename = data['session'] + '.png'
    with open(settings.MEDIA_ROOT / filename, 'wb') as f:
        map_image.write_to_png(f)

    image['image'] = filename

    # todo Не забыть удалять файлы карт
    return image
