from django.core.management.base import BaseCommand
from maptest.models import City
import csv


class Command(BaseCommand):
    help = 'import city.csv'

    def handle(self, *args, **options):
        print('Начало импорта...')
        error_count = 0
        success_count = 0
        with open('city.csv', encoding="utf-8") as f:
            reader = csv.reader(f)
            for line in reader:
                try:
                    city, created = City.objects.get_or_create(
                        address=line[0],
                        postal_code=line[1],
                        country=line[2],
                        federal_district=line[3],
                        region_type=line[4],
                        region=line[5],
                        area_type=line[6],
                        area=line[7],
                        city_type=line[8],
                        city=line[9],
                        settlement_type=line[10],
                        settlement=line[11],
                        kladr_id=line[12],
                        fias_id=line[13],
                        fias_level=line[14],
                        capital_marker=line[15],
                        okato=line[16],
                        oktmo=line[17],
                        tax_office=line[18],
                        timezone=line[19],
                        geo_lat=line[20],
                        geo_lon=line[21],
                        population=line[22],
                        foundation_year=line[23]
                    )
                    if created:
                        success_count += 1
                except:
                    print('Error save line: ', line)
                    error_count += 1
            print('Импорт завершен!')
            if error_count == 0:
                print(f'Добавлено {success_count} записей')
            else:
                print('Количество ошибок: ', error_count)
