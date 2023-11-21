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
    name = "Under_Armour"
    link_raiz = 'https://www.underarmour.com/en-us/c/shoes/' #https://www.nike.com/us/es/w/negro-air-max-calzado-90poyza6d8hzy7ok
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
        try:
            # Esperar hasta que el banner esté presente y cerrarlo
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='LoyaltyEnrollmentDialog_led__close__Ik8_N']"))
            ).click()
        except Exception as e:
            print(f"No se encontró el banner o hubo un error: {e}")
        # Recorrer paginas para tener todos los items
        while True:
            # Esperar 5 segundos
            time.sleep(3)

            # Obtener items de cada calzado
            xpath = "//div[@class='MuiGrid-root MuiGrid-container products_list css-1qpk5ww']/div/div/a[text()]"
            link_elements = driver.find_elements(By.XPATH,xpath)

            for link_el in link_elements:
                href = link_el.get_attribute("href")
            
                # time.sleep(10)
                yield scrapy.Request(href)
            # Validar si se puede hacer click en el elemento
            try:
                # Elemento para clickear siguiente pagina
                xpath_nextPage= "//div[@class='Pagination_nav-control-item__qn4rW Pagination_nav-control-item__right__zvWP1']/a"

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


    def parse(self, response):
        # div_descripcion = '//div[@class="css-mso6zd"]'
        item = ZapatillaItem()
        item['modelo'] = response.xpath("//h1[@class='ProductDetailContent_productNameWording__PNuV_']/text()").get()
        item['marca']  = 'Reebok'
        item['precio'] = response.xpath("//div[@id='product-price']/div/span/text()").get()
        item['color']  = response.xpath("//fieldset[@name='color-swatches']/legend/span[2]/text()").get()
        item['descripcion'] = response.xpath("//nav[@class='Breadcrumbs_breadcrumbs__ADNo9 ProductDetailContent_breadcrumbs__Zjc_n']//li/a/text()").get()
        item['url_raiz'] = self.link_raiz
        item['url_calzado'] = response.url
        # Elemento que contiene el json para obtener caracteristicas
        item['imagenes'] = response.xpath("//div[@class='MuiGrid-root MuiGrid-item MuiGrid-grid-xs-6 ProductDetailContent_desktop-only__Qpk8D css-1s50f5r']//img/@src").getall()
        item['tallas'] = response.xpath("//div[@class='SizeSwatch_size-swatch__2PCRx']/label/span[1]/text()").getall()
        yield item
    
## Comando para extraer 
### scrapy crawl Under_Armour -o Under_Armour.csv -t csv