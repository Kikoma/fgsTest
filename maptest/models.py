from django.db import models


# Create your models here.
class City(models.Model):
    # длинна строк в файле
    # {0: 69, 1: 11, 2: 9, 3: 17, 4: 11, 5: 40, 6: 9, 7: 27, 8: 9, 9: 25, 10: 15, 11: 11, 12: 13, 13: 36, 14: 10, 15: 14,
    #  16: 11, 17: 11, 18: 10, 19: 8, 20: 10, 21: 11, 22: 10, 23: 18}
    address = models.CharField(max_length=70, blank=True, default='')
    postal_code = models.CharField(max_length=11, blank=True, default='')
    country = models.CharField(max_length=10, blank=True, default='')
    federal_district = models.CharField(max_length=20, blank=True, default='')
    region_type = models.CharField(max_length=11, blank=True, default='')
    region = models.CharField(max_length=40, blank=True, default='')
    area_type = models.CharField(max_length=10, blank=True, default='')
    area = models.CharField(max_length=30, blank=True, default='')
    city_type = models.CharField(max_length=10, blank=True, default='')
    city = models.CharField(max_length=30, blank=True, default='')
    settlement_type = models.CharField(max_length=20, blank=True, default='')
    settlement = models.CharField(max_length=20, blank=True, default='')
    kladr_id = models.CharField(max_length=20, blank=True, default='')
    fias_id = models.CharField(max_length=36, blank=True, default='')
    fias_level = models.CharField(max_length=20, blank=True, default='')
    capital_marker = models.CharField(max_length=20, blank=True, default='')
    okato = models.CharField(max_length=20, blank=True, default='')
    oktmo = models.CharField(max_length=20, blank=True, default='')
    tax_office = models.CharField(max_length=20, blank=True, default='')
    timezone = models.CharField(max_length=20, blank=True, default='')
    geo_lat = models.CharField(max_length=20, blank=True, default='')
    geo_lon = models.CharField(max_length=20, blank=True, default='')
    population = models.CharField(max_length=20, blank=True, default='')
    foundation_year = models.CharField(max_length=20, blank=True, default='')

    def __str__(self):
        res = self.country + ', ' + self.region + ' ' + self.region_type
        res += ', ' + self.area + ' ' + self.area_type if len(self.area) > 0 else ''
        res += ', ' + self.city_type + ' ' + self.city
        return res
