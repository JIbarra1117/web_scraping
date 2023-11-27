import scrapy
# from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException,StaleElementReferenceException,NoSuchElementException
import time
import re
from Nike_Air_Project.items import ZapatillaItem
import json
from ..spiders.metodos import Metodos as truco

class ZapatillasSpider(scrapy.Spider):
    cont_links = 0
    name = "Adidas"
    link_raiz = 'https://www.adidas.com/us/search?q=shoes' 
    # allowed_domains = ["x"]
    # start_urls = ["https://www.adidas.com/us/predator-accuracy.1-l-firm-ground-soccer-cleats/FZ6277.html"]
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
        ##### ELEMENTOS #####
       # Elemento para obtener links de cada calzado
        xpath_links = "//div[@class='glass-product-card-container with-variation-carousel']/div/a"
        link_elements =[]
        # cont = 0
        while True:
            # cont += 1
            # if cont > 3:
            #     break
            # Esperar 1 segundos
            time.sleep(3)
            # Si aparece una alerta se deberia cerrar la alerta
            truco.cerrar_alerta(driver)

            # Validar que los productos sean calzados deportivos
            for link in (driver.find_elements(By.XPATH, xpath_links)):
                # Validar si en la descripción contiene "SHOE"
                href = link.get_attribute("href")
                yield scrapy.Request(href)

            # Validar si el elemento se pudo dar click
            try:
                # Elemento boton para avanzar
                boton_avanzar = driver.find_element(By.LINK_TEXT, 'NEXT')

                # Clickear
                boton_avanzar.click()

            except StaleElementReferenceException:
                print("Elemento obsoleto. Volviendo a buscar el botón Next.")
                # continue  # Volver al inicio del bucle para intentar de nuevo

            except NoSuchElementException:
                print("No hay más botones Next. Saliendo del bucle.")
                break
            except ElementClickInterceptedException:
                print("No se pudo dar click en el elemento")

        driver.quit()
        print(f'# de links: {self.cont_links}')
        print(f'Links: {link_elements}')

    def parse(self, response):
        # Obtener el HTML de la respuesta
        html_content = response.body.decode(response.encoding)
        truco.save_html_to_file(html_content=html_content,titulo='HTML_Adidas')
        item = ZapatillaItem()
        item['modelo'] = response.xpath("//div[@class='content___1BnBS']//h1[@class='name___120FN']//span/text()").get()
        item['marca']  = 'Adidas'
        item['precio'] = response.xpath("//div[@class='product-price___2Mip5 gl-vspace']/div/div/div/div[1]/text()").get()
        # item['color']  = response.xpath("//div[@class='sidebar-color-chooser___i7JXW']/div[@class='color-label___2hXaD']/text()").get()
        item['url_raiz'] = self.link_raiz
        item['url_calzado'] = response.url
        # Elemento que contiene el json para obtener caracteristicas
        json_element = response.xpath("//body/script[7]/text()").get()
        # print('JSON')
        # print(json_element)
        data_json=json.loads(json_element.replace('window.REACT_QUERY_DATA = ',''))
        # print(f'Data de JSON: {data_aux}')
        data_script = response.xpath("//body[1]/script[6]/text()").get()
        data_match = re.search(r'window\.DATA_STORE = JSON\.parse\((.*?)\);', data_script)

        if data_match:
            data = data_match.group(1)
            data_ex = json.loads(data)
            # print(f'Data de JSON: {data_ex}')
        else:
            truco.print_color("No se encontró el patrón en el script.", '\033[91m')
            # print('No se encontró el patrón en el script.')
        # print("Data loca")
        # print(truco.find_jsonLabel(obj=data_json,etiqueta='subtitle')[0])
        tallas = truco.find_jsonLabel(obj=data_json,etiqueta='size')
        imagenes = truco.find_jsonLabel(obj=data_json,etiqueta='image_url')
        color = truco.find_jsonLabel(obj=data_json,etiqueta='color')[0]
        # item['descripcion'] = response.xpath("//div[@class='text-content___13aRm']/h3/text()").getall()
        item['descripcion'] = str(truco.find_jsonLabel(obj=data_json,etiqueta='subtitle')[0]).strip()

        # print(f'Color calzado: {color}')
        item['tallas'] =  (truco.limpiar_lista(tallas))
        item['imagenes'] = imagenes
        item['color']  = color
        yield item

    
## Comando para extraer 
### scrapy crawl Adidas -o Adidas.csv -t csv