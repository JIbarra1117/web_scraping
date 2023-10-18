import scrapy
# from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from Nike_Air_Project.items import ZapatillaItem
# import os
import json

class ZapatillasSpider(scrapy.Spider):
    name = "Zapatillas_Nike_Air"
    link_raiz = 'https://www.nike.com/us/es/w/calzado-y7ok' #https://www.nike.com/us/es/w/negro-air-max-calzado-90poyza6d8hzy7ok
    # link_raiz = "https://www.nike.com/us/es/w/negro-air-max-calzado-90poyza6d8hzy7ok"
    # allowed_domains = ["x"]
    # start_urls = ["https://x"]
    def start_requests(self):
        chrome_options = webdriver.ChromeOptions()
        prefs ={"profile.default_content_setting_values.notifications":2}
        chrome_options.add_experimental_option("prefs",prefs )
        # Opciones de navegación
        driver = webdriver.Chrome(chrome_options)
        driver.maximize_window()
        driver.get(self.link_raiz)

        # Realiza una acción que cierra la ventana emergente, como hacer clic en un enlace
        button = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"button[aria-label='Close Menu']"))).click()
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        time.sleep(5)
        # Realiza el scroll hasta que no se pueda hacer más
        while True:
            # Realiza un scroll hacia abajo
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

            # Espera un momento para que cargue el contenido (ajusta el tiempo según tu página)
            driver.implicitly_wait(10)
            time.sleep(5)
            # Obtiene la nueva altura de la página
            new_height = driver.execute_script("return document.body.scrollHeight")

            # Compara la altura anterior con la nueva altura
            if new_height == last_height:
                break  # Si no hubo cambio en la altura, termina el scroll
            last_height = new_height
        # Esperar 5 segundos
        time.sleep(5)
        # Obtener items de cada calzado
        xpath = '//div[@class="product-card__body"]//a[text()]' 
        link_elements = driver.find_elements(By.XPATH,xpath)

        for link_el in link_elements:
            href = link_el.get_attribute("href")
            yield scrapy.Request(href)
        
        driver.quit()


    def parse(self, response):
        div_descripcion = '//div[@class="css-mso6zd"]'
        item = ZapatillaItem()
        item['modelo'] = response.xpath('//h1[@id="pdp_product_title"]//text()').getall()
        item['marca']  = 'Nike'
        item['precio'] = response.xpath('//div[@data-test="product-price"]//text()').getall()
        item['color']  = response.xpath(div_descripcion+'//li[@class="description-preview__color-description ncss-li"]//text()').getall()
        item['tipo'] = response.xpath('//h2[@class="headline-5 pb1-sm d-sm-ib"]/text()').getall()
        item['url_raiz'] = self.link_raiz
        item['url_calzado'] = response.url
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
        tallas=find_jsonLabel(obj=data_json,etiqueta='nikeSize')
        item['imagenes']=(find_jsonLabel(obj=data_json,etiqueta='squarishURL'))
        item['tallas']=tallas
        yield item
    
## Comando para extraer 
### scrapy crawl Zapatillas_Nike_Air -o Nike_Air.csv -t csv