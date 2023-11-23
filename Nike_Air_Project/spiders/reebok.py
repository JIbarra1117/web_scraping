import scrapy
# from scrapy.utils.project import get_project_settings
from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException,NoSuchElementException
import time
from Nike_Air_Project.items import ZapatillaItem
# import os
import json

class ZapatillasSpider(scrapy.Spider):
    name = "Zapatillas_Reebok"
    link_raiz = 'https://www.reebok.com/c/600000057/collection-shoes?page=1' #https://www.nike.com/us/es/w/negro-air-max-calzado-90poyza6d8hzy7ok
    # link_raiz = "https://www.nike.com/us/es/w/negro-air-max-calzado-90poyza6d8hzy7ok"
    # allowed_domains = ["x"]
    # start_urls = ["https://x"]
    def start_requests(self):
        chrome_options = webdriver.ChromeOptions()
        prefs ={    "profile.default_content_setting_values.notifications":2,
                    "translate_whitelists": {"en":"es"},
                    "translate":{"enabled":"true"}}
        chrome_options.add_experimental_option("prefs",prefs )
        # Establecer a español
        chrome_options.add_argument("--lang=es")  
        # Opciones de navegación
        driver = webdriver.Chrome(chrome_options)
        driver.maximize_window()
        driver.get(self.link_raiz)
        links_aux = []

        # Recorrer paginas para tener todos los items
        while True:
            # Esperar 5 segundos
            time.sleep(3)

            # Obtener items de cada calzado
            xpath = "//div[@class='col--TywhC      product-card-container-holder--KN3Mh']/a"
            link_elements = driver.find_elements(By.XPATH,xpath)

            for link_el in link_elements:
                href = link_el.get_attribute("href")
                # Probar links
                links_aux.append(href)
                # time.sleep(10)
                yield scrapy.Request(href)
            # Validar si se puede hacer click en el elemento
            try:
                # Elemento para clickear siguiente pagina
                xpath_nextPage= "//div[@class='col--TywhC      pagination-next--nMfGO']/label[@class='pagination-next--nMfGO ']"
                # xpath_nextPage="//div[@class='collapse-icon-wrapper--1THl7']"
                # Validar si el elemento existe
                try:
                    element = driver.find_element(By.XPATH,xpath_nextPage)

                    # Esperar 5 segundos
                    time.sleep(2)
                    element.click()
                except NoSuchElementException:
                    print("No hay el elemento")
                    break
            except ElementClickInterceptedException:
                print("No se pudo hacer clic en el elemento, maneja el error aquí.")

            time.sleep(2)
        driver.quit()
        print(links_aux)


    def parse(self, response):
        # div_descripcion = '//div[@class="css-mso6zd"]'
        item = ZapatillaItem()
        item['modelo'] = response.xpath("//div[@class='col--TywhC   col-breakpoints--2NB5_ col-lg-4--1ct9j']//h1/text()").getall()
        item['marca']  = 'Reebok'
        item['precio'] = response.xpath("//div[@class='flex-row--1XndU column-gap-5--vYgBs  text-align-left--3KlWV']//p/text()").getall()
        item['color']  = response.xpath("//div[@class='flex-row--1XndU text-align-left--3KlWV']/p[@class='tag_p--1xo5V']/text()").getall()
        item['descripcion'] = response.xpath("//h2[@class='tag_h1_w_bold--3Xher  product-detail-case--uvj_l']/text()").getall()
        item['url_raiz'] = self.link_raiz
        item['url_calzado'] = response.url
        # Elemento que contiene el json para obtener caracteristicas
        text_tallas = response.xpath("//script[@id='__NEXT_DATA__']/text()").get()
        json_contenido='['+text_tallas+']'
        data_json=json.loads(json_contenido)
        # Función recursiva para buscar la propiedad del json
        def find_jsonLabel(obj, etiqueta):
            resultado = []
            def buscar_recursivamente(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key == etiqueta:
                            resultado.append(value)
                        elif isinstance(value, (dict, list)):
                            buscar_recursivamente(value)
                elif isinstance(obj, list):
                    for item in obj:
                        buscar_recursivamente(item)

            buscar_recursivamente(obj)
            return resultado
        tallas=find_jsonLabel(obj=data_json,etiqueta='sizeFilter')
        item['imagenes']=(find_jsonLabel(obj=data_json,etiqueta='url'))
        item['tallas']=tallas
        yield item
    
## Comando para extraer 
### scrapy crawl Zapatillas_Reebok -o Nike_Air.csv -t csv