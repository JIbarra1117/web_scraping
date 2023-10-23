# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ZapatillaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    modelo = scrapy.Field()
    marca = scrapy.Field()
    tallas = scrapy.Field()
    color = scrapy.Field()
    precio = scrapy.Field()
    imagenes = scrapy.Field()
    descripcion = scrapy.Field()
    url_raiz = scrapy.Field()
    url_calzado = scrapy.Field()