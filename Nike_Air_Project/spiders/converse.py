import scrapy
# from scrapy.utils.project import get_project_settings
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from Nike_Air_Project.items import ZapatillaItem
import re
# import os

class ZapatillasSpider(scrapy.Spider):
    name = "Zapatillas_Converse"
    link_raiz = 'https://www.converse.com/shop/shoes' 
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        }
    # start_urls = ["https://x"]
    def start_requests(self):
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "translate_whitelists": {"en": "es"},
            "translate": {"enabled": "true"}
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--lang=es")
        driver = webdriver.Chrome(chrome_options)
        driver.maximize_window()
        driver.get(self.link_raiz)

        ###### ELEMENTOS ########
        ###### ELEMENTOS ########
        # Elemento del footer
        footer_xpath = "//div[@class='row grid-no-gutters plp__seo-popular-search']/div"  
        # Elemento de links de productos
        xpath = "//div[@class='product-tile__main product-tile__main--general ratio-container--standard']/a[text()]"
        # Elemento de la descripcion del producto para validar si es calzado uy no otros "shoes"
        xpath_desc = "//div[@class='product-tile__details  text-align--left']/p[text()]"
        # Elemento de cantidad de productos
        xpath_cantiProd = "//div[@class='plp-actions__count']"

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='window-modal__close']"))
            ).click()
        except Exception as e:
            print(f"No se encontró el banner o hubo un error: {e}")

        total_scroll_height = driver.execute_script("return document.body.scrollHeight")
        scroll_fraction = 0.2

        footer_element = driver.find_element(By.XPATH, footer_xpath)
        cantiProductos = int(self.extraer_numero(driver.find_element(By.XPATH, xpath_cantiProd).text))
        print(cantiProductos)
        print(int(cantiProductos * 0.8))
        time.sleep(10)

        # Inicializar el contador de productos extraídos
        cont_produc_extr = 0

        # Realizar el desplazamiento en pequeños pasos
        while True:
            cont_produc_extr = 0
            # Recorrer la barra de desplazamiento
            driver.execute_script(f"window.scrollBy(0, {total_scroll_height * scroll_fraction})")

            # Obtener items de cada calzado
            link_elements = driver.find_elements(By.XPATH, xpath)
            desc_element = driver.find_elements(By.XPATH, xpath_desc)

            # Ciclo para recorrer los elementos extraídos para cada producto de la página
            for link_el, desc_el in zip(link_elements, desc_element):
                cont_produc_extr += 1
                print(f'Número de productos: {cont_produc_extr}')

                # Comprobar si se ha alcanzado el límite de productos
                if cont_produc_extr > int(cantiProductos * 0.8):
                    break

                href = link_el.get_attribute("href")
                # Validar si en la descripción contiene "SHOE"
                if self.buscar_palabra(desc_el.text, "SHOE"):
                    # Solicitud de Links extraídos
                    yield scrapy.Request(href)

            # Comprobar si se ha alcanzado el límite de productos
            if cont_produc_extr > int(cantiProductos * 0.8):
                break

        driver.quit()
    def parse(self, response):
        self.log(f'Ejecutando parse para URL: {response.url}')
        try:
            item = ZapatillaItem()
            item['modelo'] = response.xpath("//h1[@class='pdp-primary-information__product-name display--small-up']/text()").get().strip()
            item['marca']  = "Converse"
            item['precio'] = response.xpath("//div[@class='pdp-primary-information__price body-type display--small-up']//span/text()").get().strip()
            item['color']  = response.xpath("//div[@class='pdp-variations__variation-information text-line--xlarge']//span/text()").get().strip()
            item['descripcion'] = response.xpath("//p[@class='pdp-primary-information__short-description']/text()").get().strip()
            item['url_raiz'] = self.link_raiz
            item['url_calzado'] = response.url
            # item['imagenes']= self.limpiar_data(response.xpath("//div[@class='pdp-images-gallery__gallery-item-container pdp-images-gallery__gallery-item-container--supplementry']//img/@src").getall())
            item['tallas']= self.limpiar_lista_data(response.xpath("//*[@id='variationDropdown-size']/option/text()").getall())
            item['imagenes']= response.xpath("//div[@class='pdp-images-gallery__gallery-item-container pdp-images-gallery__gallery-item-container--supplementry']//img/@data-src").getall()
            # item['imagenes']= response.css("div.pdp-images-gallery__gallery-item-container.pdp-images-gallery__gallery-item-container--supplementry img[src]").getall()
            # item['tallas']= response.xpath("//*[@id='variationDropdown-size']/option/text()").getall()
            yield item
        except Exception as e:
            self.log(f"Error en parse: {e}")
    
    def limpiar_lista_data(self, lista_datos):
        resultado = []
        for data in lista_datos:
            # print('CALZADO DEPORTIVO: '+data)
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
    def is_element_fully_visible(self, element, driver):
        try:
            # Esperar hasta que el elemento sea visible
            WebDriverWait(driver, 10).until(
                EC.visibility_of(element)
            )

            # Obtener la posición y el tamaño del elemento
            location = element.location
            size = element.size

            # Calcular las coordenadas del borde inferior del elemento
            bottom = location['y'] + size['height']

            # Verificar si el borde inferior está dentro de la ventana visible
            return 0 <= bottom <= driver.execute_script("return window.innerHeight;")
        except Exception as e:
            print(f'Error: {e}')
            return False
## Comando para extraer 
### scrapy crawl Zapatillas_Converse -o Converse.json -t json
#   scrapy crawl Zapatillas_Converse -o Converse.csv -t csv