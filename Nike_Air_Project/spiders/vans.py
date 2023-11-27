import scrapy
# from scrapy.utils.project import get_project_settings
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException,StaleElementReferenceException,NoSuchElementException
import time
from Nike_Air_Project.items import ZapatillaItem
from ..spiders.metodos import Metodos as truco

# import os

class ZapatillasSpider(scrapy.Spider):
    name = "vans"
    link_raiz = 'https://www.vans.com/en-us/shoes-c00081' 
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        }
    # start_urls = ["https://www.vans.com/en-us/shoes-c00081/old-skool-shoe-pvn000d3hn3u"]
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
        # Elemento de links de productos
        xpath = "//div[@class='products-grid products-grid--redesign']/div/div/div/div/div/a[1]"
        # Elemento boton de cargar mas
        xpath_button_cargMas = "//div[@class='column small-12 medium-10 large-10']/div/button[2]"
        # Elemento de catnidad productos
        xpath_cantProd = "(//div[@class='vf-heading page-header__title']/p)[2]"
         # Proceso de extraccion
        cantiProductos = int(truco.extraer_numero(driver.find_element(By.XPATH, xpath_cantProd).text))
    
        total_scroll_height = driver.execute_script("return document.body.scrollHeight")
        scroll_fraction = 0.1
        
        print(f'Cantidad de productos: {cantiProductos}')
        print(f'95% de Productos: {int(cantiProductos * 0.95)}')
        time.sleep(5)

        # Inicializar el contador de productos extraídos
        cont_produc = 0
        # Caluclo de numero de clicks
        # cantidad_clicks = int(round(cantiProductos / 24))
        links = set()
        try:
            # aceptar las cookies
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, xpath_button_cargMas))
            ).click()
        except Exception as e:
            print(f"No se encontró el banner o hubo un error: {e}")
        recorrido = total_scroll_height * 0.1
        driver.execute_script(f"window.scrollBy(0, {recorrido})")
        while True:
            # Esperar antes de realizar el scroll
            time.sleep(3)

            # Obtener items de cada calzado
            link_elements = driver.find_elements(By.XPATH, xpath)
            print(f'Numero datos extraidos: {len(link_elements)}')
            # Ciclo para recorrer los elementos extraídos para cada producto de la página
            for link_el in link_elements:
                href = link_el.get_attribute("href")
                print(f'Link obtenido: {href}')
                links.add(href)
            # Obtener el número de enlaces únicos
            cont_produc = len(links)
            if cont_produc> cantiProductos*0.95:
                break
            recorrido = total_scroll_height * scroll_fraction
            driver.execute_script(f"window.scrollBy(0, {recorrido})")

            print(f'Número de productos: {cont_produc}/{cantiProductos}')
        links = list(links)
        print(f'Links obtenidos: {links}')
        for link in links:
            yield scrapy.Request(link)
        driver.quit()


    def parse(self, response):
        # html_content = response.body.decode(response.encoding)
        # truco.save_html_to_file(html_content=html_content,titulo='HTML_Vans')
        self.log(f'Ejecutando parse para URL: {response.url}')
        item = ZapatillaItem()
        item['modelo'] = response.xpath("//div[@class='container nested']//h1[@class='vf-text vf-heading__title vf-text--title-2 vf-text--sm-left-text-align vf-text--md-left-text-align vf-text--lg-left-text-align']/text()").get().strip()
        item['marca']  = "Vans"
        item['precio'] = response.xpath("(//div[@class='vf-product-price']/div[@class='vf-price product__price']/span/text())[1]").get().strip()
        item['color']  = str(response.xpath("//div[@class='vf-heading product-colors__heading']/h3/text()").get()).strip().replace('Color: ','')
        descripcion = response.xpath("//div[@class='vf-product-details__description ']/p/text()").get()
        descripcion_2 = response.xpath("//div[@class='vf-product-details__description ']/text()").get()
        item['descripcion'] = descripcion.strip().replace('\n', '') if descripcion is not None else (truco.obtener_texto_antes_de_caracter(texto=descripcion_2, caracter_limite='.')).strip().replace('\n', '')
        item['url_raiz'] = self.link_raiz
        item['url_calzado'] = response.url
        tallas = ["B3.5 / W5","B4 / W5.5", "B4.5 / W6", "B5 / W6.5", "B5.5 / W7", "B6 / W7.5", "M6.5 / W8", "M7 / W8.5", "M7.5 / W9", "M8 / W9.5", "M8.5 / W10", "M9 / W10.5", "M9.5 / W11", "M10 / W11.5", "M10.5 / W12", "M11 / W12.5", "M11.5 / W13","M12 / W13.5", "M13 / W14.5"]
        item['tallas']=  tallas#truco.limpiar_lista_data(response.xpath("//*[@id='variationDropdown-size']/option/text()").getall())
        item['imagenes']= response.xpath("//div[@class='image-grid image-grid--redesign']/div/div/div/button/@data-image-hr-src").getall()
        yield item
 

## Comando para extraer 
### scrapy crawl vans -o Vans.json -t json
#   scrapy crawl vans -o Vans.csv -t csv