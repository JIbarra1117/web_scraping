import scrapy
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from Nike_Air_Project.items import ZapatillaItem
import re
# import os

class ZapatillasSpider(scrapy.Spider):
    name = "Skechers"
    link_raiz = 'https://www.skechers.com/shop/?prefn1=productLine&prefv1=FOOTWEAR&start=0&sz' 
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        }
    # start_urls = ["https://www.skechers.com/skechers-slip-ins-arch-fit-2.0---look-ahead/232462_WBK.html"]
    def start_requests(self):
        headers = { "user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"}
        chrome_options = webdriver.ChromeOptions()
        # Para cambiar el User-Agent en Selenium
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36")

        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "translate_whitelists": {"en": "es"},
            "translate": {"enabled": "true"}
        }
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(chrome_options)
        driver.maximize_window()
        driver.get(self.link_raiz)

        ###### ELEMENTOS ########
        # Elemento de links de productos
        xpath = "//div[@class='pdp-link c-product-tile__title__wrap']/a[text()]"

        time.sleep(60)

        # Obtener items de cada calzado
        link_elements = driver.find_elements(By.XPATH, xpath)

        # Ciclo para recorrer los elementos extraídos para cada producto de la página
        for link_elin in link_elements:
            time.sleep(4)
            href = link_elin.get_attribute("href")
            yield scrapy.Request(url=href,headers=headers)
        driver.quit()

    def parse(self, response):
        self.logger.info(f"Precesamiento de url: {response.url}")
        item = ZapatillaItem()
        item['modelo'] = response.xpath("//div[@class='c-product-details__product-info ']/h1/text()").get().strip()
        item['marca']  = "Converse"
        item['precio'] = response.xpath("//div[@class='prices']//span[@class='sales ']/span/text()").get().strip()
        item['color']  = response.xpath("//div[@class='d-flex align-items-center']//span[@class='js-product-details-attr-colorCode c-product-attributes__item__selected-val c-product-attributes__item__selected-val--color ']/text()").get().strip()
        item['descripcion'] = response.xpath("//div[@class='c-product-details__product-info ']/div[@class='c-product-details__label']/text()" ).get().strip()
        item['url_raiz'] = self.link_raiz
        item['url_calzado'] = response.url
        item['tallas']= self.limpiar_lista_data(response.xpath("//div[@class='col-12']/button[@class='c-product-attributes__item__selector button-select-size js-attr-selector ']/span/text()").getall())
        item['imagenes']= response.xpath("//div[@class='order-2 c-pdp-carousel__thumbnails   js-carousel-thumbnails js-carousel-thumbnails--232462_WBK row ']/div/img/@src").getall()
        yield item

    def limpiar_lista_data(self, lista_datos):
        resultado = []
        for data in lista_datos:
            # print('CALZADO DEPORTIVO: '+data)
            val = data.strip()
            resultado.append(val)
        return resultado

    def buscar_palabra(self, cadena, palabra):
        # Convierte la cadena y la palabra a minúsculas para hacer la búsqueda insensible a mayúsculas
        cadena = cadena.lower()
        palabra = palabra.lower()
        # Verifica si la palabra está presente en la cadena
        if palabra in cadena:
            return True
        else:
            return False
        
    def extraer_numero(self, cadena):
        cadena =  cadena.replace(',','')
        # Usar una expresión regular para encontrar el número en la cadena
        numero_encontrado = re.search(r'\b\d+\b', cadena)

        # Verificar si se encontró un número
        if numero_encontrado:
            return numero_encontrado.group()
        else:
            return None
            # Función para verificar si el elemento está completamente dentro de la vista

## Comando para extraer 
### scrapy crawl Skechers -o Skechers.json -t json
#   scrapy crawl Skechers -o Skechers.csv -t csv