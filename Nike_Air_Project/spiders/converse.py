import scrapy
# from scrapy.utils.project import get_project_settings
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from Nike_Air_Project.items import ZapatillaItem
# import os

class ZapatillasSpider(scrapy.Spider):
    name = "Zapatillas_Converse"
    link_raiz = 'https://www.converse.com/shop/shoes' #https://www.nike.com/us/es/w/negro-air-max-calzado-90poyza6d8hzy7ok
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        }

    # allowed_domains = ["x"]
    # start_urls = ["https://www.converse.com/shop/p/run-star-hike-platform-quilted-womens-high-top-shoe/A08720C.html?dwvar_A08720C_color=pink%20sage%2Fegret%2Fblack&styleNo=A08720C&cgid=shoes"]
    # def start_requests(self):
    #     chrome_options = webdriver.ChromeOptions()
    #     prefs ={    "profile.default_content_setting_values.notifications":2,
    #                 "translate_whitelists": {"en":"es"},
    #                 "translate":{"enabled":"true"}}
    #     chrome_options.add_experimental_option("prefs",prefs )
    #     # Establecer a español
    #     chrome_options.add_argument("--lang=es")  
    #     # Opciones de navegación
    #     driver = webdriver.Chrome(chrome_options)
    #     driver.maximize_window()
    #     driver.get(self.link_raiz)
    #     links_aux = []

    #     time.sleep(3)
    #     # Recorrer paginas para tener todos los items
    #     last_height = 0  # Asigna un valor inicial a last_height
    #     cont = 0
    #     while True:
    #         # Realiza un scroll hacia abajo
    #         driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    #         # Espera un momento para que cargue el contenido 
    #         driver.implicitly_wait(10)
    #         # Obtiene la nueva altura de la página
    #         new_height = driver.execute_script("return document.body.scrollHeight")

    #         # hacer un  desplazamiento anterior
    #         driver.execute_script("window.scrollTo(0, document.body.scrollHeight-50)")

    #         # Esperar
    #         time.sleep(2)
            
    #         # Actualizar desplazamiento
    #         driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

    #         # ACtualizar posicion
    #         new_height = driver.execute_script("return document.body.scrollHeight")
            
    #         # Compara la altura anterior con la nueva altura
    #         if new_height == last_height:
    #             break  # Si no hubo cambio en la altura, termina el scroll
            
    #         # Esperar para dar tiempo a volver al inicio
    #         time.sleep(3)

    #          # Actualizar last_height al valor nuevo
    #         last_height = new_height

    #         # Etiqueta del boton banner
    #         etiqueta_banner = "//button[@class='window-modal__close']"
    #         # Validar si existe un banner de sugerencias
    #         # boton_banner = driver.find_element(By.XPATH,etiqueta_banner) is not None
    #         if cont==0:
    #             # Si el botón existe, realiza alguna acción aquí
    #             driver.find_element(By.XPATH,etiqueta_banner).click()
    #         cont=cont+1

    #     time.sleep(3)
    #     # Obtener items de cada calzado
    #     xpath = "//div[@class='product-tile__main product-tile__main--general ratio-container--standard']/a[text()]"
    #     link_elements = driver.find_elements(By.XPATH,xpath)
    #     # Validar si en la descripcion contiene shoes para no obtener otro producto
    #     xpath_desc = "//div[@class='product-tile__details  text-align--left']/p[text()]"
    #     desc_element = driver.find_elements(By.XPATH, xpath_desc)
    #     # Ciclo para recorrer los elementos extraídos para cada producto de la página
    #     for link_el, desc_el in zip(link_elements, desc_element):
    #         href = link_el.get_attribute("href")
    #         # Validar si en la descripción contiene "SHOE"
    #         if self.buscar_palabra(desc_el.text, "SHOE"):
    #             # Solicitud de Links extraídos
    #             yield scrapy.Request(href)
    #     # time.sleep(2)
    #     driver.quit()
        
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

        try:
            # Esperar hasta que el banner esté presente y cerrarlo
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='window-modal__close']"))
            ).click()
        except Exception as e:
            print(f"No se encontró el banner o hubo un error: {e}")

        #     time.sleep(4)
        # Obtener el tamaño total del scroll
        total_scroll_height = driver.execute_script("return document.body.scrollHeight")
        
        # Definir la fracción del scroll para cada paso (puedes ajustar este valor)
        scroll_fraction = 0.1  # Por ejemplo, desplazarse en un 10% de la altura total en cada paso

        # Calcular la cantidad de pasos necesarios
        # num_steps = int(total_scroll_height / (total_scroll_height * scroll_fraction))
        # Elemento del footer
        # footer_xpath = "//footer[@class='footer ']/div[@class='footer__container text-color--neutral-4']/div"  
        footer_xpath = "//div[@class='row grid-no-gutters plp__seo-popular-search']/div"  
        
        # Obtener el elemento del footer
        footer_element = driver.find_element(By.XPATH, footer_xpath)

        # Función para verificar si el elemento está completamente dentro de la vista
        def is_element_fully_visible(element):
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

        # Realizar el desplazamiento en pequeños pasos
        while True:
            # Recorrer la barra de desplamzamiento del 1% del tamaño de la barra de desplazamiento inicial
            driver.execute_script(f"window.scrollBy(0, {total_scroll_height * scroll_fraction})")
            # time.sleep(1)  # Esperar un segundo entre cada paso
            # tamaño_scroll = driver.execute_script("return document.body.scrollHeight")
            
            # Comprobar si el footer está completamente dentro de la vista para terminar el ciclo
            if is_element_fully_visible(footer_element):
                break
        
        # Obtener items de cada calzado
        xpath = "//div[@class='product-tile__main product-tile__main--general ratio-container--standard']/a[text()]"
        link_elements = driver.find_elements(By.XPATH,xpath)
        # Validar si en la descripcion contiene shoes para no obtener otro producto
        xpath_desc = "//div[@class='product-tile__details  text-align--left']/p[text()]"
        desc_element = driver.find_elements(By.XPATH, xpath_desc)
        # Ciclo para recorrer los elementos extraídos para cada producto de la página
        for link_el, desc_el in zip(link_elements, desc_element):
            href = link_el.get_attribute("href")
            # Validar si en la descripción contiene "SHOE"
            if self.buscar_palabra(desc_el.text, "SHOE"):
                # Solicitud de Links extraídos
                yield scrapy.Request(href)
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
    # modelo = scrapy.Field()
    # marca = scrapy.Field()
    # tallas = scrapy.Field()
    # color = scrapy.Field()
    # precio = scrapy.Field()
    # imagenes = scrapy.Field()
    # descripcion = scrapy.Field()
    # url_raiz = scrapy.Field()
    # url_calzado = scrapy.Field()
    
## Comando para extraer 
### scrapy crawl Zapatillas_Converse -o Converse.json -t json
#   scrapy crawl Zapatillas_Converse -o Converse.csv -t csv