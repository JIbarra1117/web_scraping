import scrapy
# from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException,StaleElementReferenceException,NoSuchElementException
import time
from Nike_Air_Project.items import ZapatillaItem
import json
from ..spiders.metodos import Metodos as truco

class ZapatillasSpider(scrapy.Spider):
    cont_links = 0
    name = "Under_Armour"
    link_raiz = 'https://www.underarmour.com/en-us/c/shoes/' 
    # allowed_domains = ["x"]
    # start_urls = ["https://www.underarmour.com/en-us/p/running/womens_ua_hovr_mega_warm_running_shoes/3026820.html?dwvar_3026820_color=100"]
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

        # Elemento para cerrar cookies
        # Esperar a que aparezca banner y consecuentemente cerrarlo
        try:
            # aceptar las cookies
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//button[@id='truste-consent-button']"))
            ).click()
        except Exception as e:
            print(f"No se encontró el banner o hubo un error: {e}")
        ##### ELEMENTOS #####
        # Elemento para obtener la descripcion y conseguir solo calzado
        xpath_desc = "//div[@class='MuiGrid-root MuiGrid-container products_list css-1qpk5ww']//a[@class='ProductTile_product-item-link__tSc19']"
        # Elemento para obtener links de cada calzado
        xpath_links = "//div[@class='MuiGrid-root MuiGrid-container products_list css-1qpk5ww']/div/div/a[text()]"
        link_elements =[]

        while True:
            # Esperar 1 segundos
            time.sleep(3)
            # Validar que los productos sean calzados deportivos
            for link, desc in zip(driver.find_elements(By.XPATH, xpath_links), driver.find_elements(By.XPATH, xpath_desc)):
                
                # Validar si en la descripción contiene "SHOE"
                href = link.get_attribute("href")
                if self.buscar_palabra(desc.text, "Shoes"):
                    self.cont_links = self.cont_links + 1
                    # Solicitud de Links extraídos
                    link_elements.append(href)
                    yield scrapy.Request(href)

            # Validar si el elemento se pudo dar click
            try:
                # Elemento boton para avanzar
                boton_avanzar = driver.find_element(By.LINK_TEXT, 'Next')

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
        item = ZapatillaItem()
        item['modelo'] = response.xpath("//h1[@class='ProductDetailContent_productNameWording__PNuV_']/text()").get()
        item['marca']  = 'Under Armour'
        item['precio'] = truco.obtener_valor_mayor_de_string(response.xpath("//div[@id='product-price']/div/span/text()").get())
        item['color']  = response.xpath("//fieldset[@name='color-swatches']/legend/span[2]/text()").get()
        descs = response.xpath("//nav[@class='Breadcrumbs_breadcrumbs__ADNo9 ProductDetailContent_breadcrumbs__Zjc_n']//li/a/text()").getall()
        item['descripcion'] = " / ".join(descs)
        item['url_raiz'] = self.link_raiz
        item['url_calzado'] = response.url
        item['imagenes'] = response.xpath("//div[@class='MuiGrid-root MuiGrid-item MuiGrid-grid-xs-6 ProductDetailContent_desktop-only__Qpk8D css-1s50f5r']//img/@src").getall()
        # Elemento que contiene el json para obtener caracteristicas
        json_element = response.xpath("//script[@id='__NEXT_DATA__']/text()").get()
        json_contenido='['+json_element+']'
        data_json=json.loads(json_contenido)
        tallas=self.find_jsonLabel(obj=data_json,etiqueta='baseSizeDisplayName')
        item['tallas']=tallas
        yield item

    def limpiar_lista_data(self, lista_datos):
        resultado = []
        for data in lista_datos:
            val = data.strip()
            if 'Pick' not in val:
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
        
    def find_jsonLabel(self, obj, etiqueta):
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
    
## Comando para extraer 
### scrapy crawl Under_Armour -o Under_Armour.csv -t csv