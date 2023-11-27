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
from ..spiders.metodos import Metodos as truco

class ZapatillasSpider(scrapy.Spider):
    name = "Zapatillas_Nike_Air"
    link_raiz = 'https://www.nike.com/us/es/w/calzado-y7ok' #https://www.nike.com/us/es/w/negro-air-max-calzado-90poyza6d8hzy7ok
    # link_raiz = "https://www.nike.com/us/es/w/negro-air-max-calzado-90poyza6d8hzy7ok"
    # allowed_domains = ["x"]
    # start_urls = ["https://www.nike.com/us/es/t/calzado-talla-grande-free-run-2-bLrw0d/DD0163-101"]
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
#s
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
        # Obtener el HTML de la respuesta
        # html_content = response.body.decode(response.encoding)
        # truco.save_html_to_file(html_content=html_content,titulo='HTML_Nike')
        div_descripcion = '//div[@class="css-mso6zd"]'
        item = ZapatillaItem()
        item['modelo'] = response.xpath('//h1[@id="pdp_product_title"]//text()').get()
        item['marca']  = 'Nike'
        item['color']  = str(response.xpath(div_descripcion+'//li[@class="description-preview__color-description ncss-li"]//text()').get()).replace('Color que se muestra: ','')
        item['descripcion'] = response.xpath('//h2[@class="headline-5 pb1-sm d-sm-ib"]/text()').get()
        item['url_raiz'] = self.link_raiz
        item['url_calzado'] = response.url
        text_tallas = response.xpath("//script[@id='__NEXT_DATA__']/text()").get()
        json_contenido='['+text_tallas+']'
        # Cargo un json para obtener datos que no cargan en el HTML
        data_json=json.loads(json_contenido)
        # Mediante el metodo find_jsonLabel>= Se encuentra la propiedad buscada de forma exhaustiva de la pagina web
        tallas=truco.find_jsonLabel(obj=data_json,etiqueta='nikeSize')
        # Obtener el codigo del calzado mediante el ultimo path del link del calzado
        codigo_calzado = str(response.url).split("/")[-1]
        # print(f'Data espeficica:')
        data= truco.find_jsonLabel(obj=data_json,etiqueta=codigo_calzado)
        # Obtener la propiedad para obtener imagenes del calzado
        data_imgs = truco.find_jsonLabel(obj=data,etiqueta="squarishURL")
        # Obtener el precio como propiedad del json
        data_price = truco.find_jsonLabel(obj=data,etiqueta="fullPrice")[0]
        # print(f'Precio calzado: {truco.eliminar_duplicados_obtener_maximo(precio)}')
        item['imagenes']= truco.limpiar_array_espacios_en_blanco(data_imgs)
        item['tallas'] = truco.limpiar_lista(tallas)
        item['precio'] = data_price #response.xpath('(//div[@data-test="product-price"]//text())[2]').get() # precio[0] 
        yield item
    
## Comando para extraer 
### scrapy crawl Zapatillas_Nike_Air -o Nike_prueba.csv -t csv