import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Nike_Air_Project.items import ZapatillaItem
# Herramientas de limpieza
import re
import json
import time
# Metodos de optimizacion
from ..spiders.metodos import Metodos as truco

class ZapatillasSpider(scrapy.Spider):
    name = "Zapatillas_Puma"
    link_raiz = 'https://us.puma.com/us/en/puma/shop-all-shoes' 
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        }
    # start_urls = ["https://us.puma.com/us/en/pd/puma-x-miraculous-rs-x-toddler-sneakers/391823?swatch=01&referrer=carousel"]
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
        xpath = "//li[@data-test-id]/a"

        # Elemento de cantidad de productos
        xpath_cantiProd = "//span[@class='uppercase font-bold text-lg md:text-xl']/span"

        # try:
        #     WebDriverWait(driver, 10).until(
        #         EC.presence_of_element_located((By.XPATH, "//button[@class='window-modal__close']"))
        #     ).click()
        # except Exception as e:
        #     print(f"No se encontró el banner o hubo un error: {e}")

        total_scroll_height = driver.execute_script("return document.body.scrollHeight")
        scroll_fraction = 0.2

        cantiProductos = int(truco.extraer_numero(driver.find_element(By.XPATH, xpath_cantiProd).text))
        print(cantiProductos)
        print(int(cantiProductos * 0.9))
        time.sleep(10)

        # Inicializar el contador de productos extraídos
        cont_produc_extr = 0
        link_elements = []
        # Realizar el desplazamiento en pequeños pasos
        while True:
            # time.sleep(2)
            cont_produc_extr = 0

            link_elements = driver.find_elements(By.XPATH, xpath)
            for link_el in link_elements:
                cont_produc_extr += 1
            # Recorrer la barra de desplazamiento
            driver.execute_script(f"window.scrollBy(0, {total_scroll_height * scroll_fraction})")

            print(f'Cantidad: {cont_produc_extr} / {int(cantiProductos * 0.95)}')
            # Comprobar si se ha alcanzado el límite de productos
            if cont_produc_extr > int(int(cantiProductos * 0.95)):
                break
                    # Obtener items de cada calzado
            # Ciclo para recorrer los elementos extraídos para cada producto de la página
        print(f'Total: {cont_produc_extr} / {int(cantiProductos * 0.95)}')
        
        # Almacenamiento de links de los productos extraidos
        link_elements = driver.find_elements(By.XPATH, xpath)     
        for link_el in link_elements:
            # cont_produc_extr += 1
            href = link_el.get_attribute("href")
            # Validar si en la descripción contiene "SHOE"
            yield scrapy.Request(href)
        driver.quit()

    def parse(self, response):

        item = ZapatillaItem()
        item['modelo'] = response.xpath("//div[@class='tw-1uc1ku0 tw-1p4ksvz']/h1/text()").get().strip()
        item['marca']  = "Puma"
        item['precio'] = response.xpath("//div[@class='tw-qlq5hv tw-1p4ksvz']/span/text()").get().strip()
        item['color']  = response.xpath("//div[@class='tw-xf6gca tw-1p4ksvz']/h4/text()" ).get().strip()
        item['url_raiz'] = self.link_raiz
        item['url_calzado'] = response.url
        item['imagenes']= response.xpath("//section[@class='order-1 relative md:col-span-4 lg:col-span-8']//div/img/@src").getall()
        # Elemento que contiene el json para obtener caracteristicas
        json_element = response.xpath("//script[@id='__NEXT_DATA__']/text()").get()
        # Formatear json
        data_json = json.loads(json_element)
        # Obtener objetos denomigos :data:
        json_aux=truco.find_jsonLabel(obj=data_json,etiqueta='data')
        # data_json=json.loads(json_aux[4])
        tallas = []
        descripcion = []
        # estableci esta logica porque algunas pagians tienen diferentes formastos de json, asi que tuve que recorresr y obtener valroes semejantes para luego limpiarlo y obtenerlo
        # Primero recorro todos los objetos data resultantes
        for json_producto in json_aux:
            # print('JSON DATA :')
            # print(json_producto)
            # Le doy formato al json de todos los que se recorre uno por uno
            json_producto=json.loads(json_producto)
            # Obtengo los siguiente objetos de cada json obtenido >> Devuelve un objeto tipo lista
            tall=truco.find_jsonLabel(obj=json_producto,etiqueta='label')
            desc=truco.find_jsonLabel(obj=json_producto,etiqueta='description')
            # print('TALLAS')
            # print(tallas)
            # print('DESCRIPCIONES')
            # print(desc)
            # Verifico si las tallas tienen mas de 1 valor 
            if len(tall)>0:
                # print('random')
                # print(tall)
                for tallas_aux in tall:
                    # Validar si el valor es un entero o no
                    if tallas_aux is not None and truco.es_entero(str(tallas_aux)):
                        tallas.append(tallas_aux)
            # Verifico si las descripciones tienen mas de 1 valor        
            if len(desc)>0:
                for desc_aux in desc:
                    descripcion.append(desc_aux)
        print('TALLAS')
        print(tallas)
        print('DESCRIPCION')
        print(response.xpath("//div[@class='tw-1uc1ku0 tw-1p4ksvz pb-4']/div/text()").get())
        item['tallas'] =  truco.convertir_string_decimal(truco.limpiar_lista(tallas))
        # item['descripcion'] = truco.obtener_texto_especifico_desde_html(response.xpath("//section[@id='product-story']/text()").get())
        item['descripcion'] = str(truco.obtener_contenido_p(truco.limpiar_lista(descripcion)[0].strip())).split('\n')[0]
        yield item
    
    # def limpiar_lista_data(self, lista_datos):
    #     resultado = []
    #     for data in lista_datos:
    #         # print('CALZADO DEPORTIVO: '+data)
    #         val = data.strip()
    #         resultado.append(val)
    #     return resultado

    # def buscar_palabra(self, cadena, palabra):
    #     # Convierte la cadena y la palabra a minúsculas para hacer la búsqueda insensible a mayúsculas
    #     cadena = cadena.lower()
    #     palabra = palabra.lower()
    #     # Verifica si la palabra está presente en la cadena
    #     if palabra in cadena:
    #         return True
    #     else:
    #         return False
    # def extraer_numero(self, cadena):
    #     cadena =  cadena.replace(',','')
    #     # Usar una expresión regular para encontrar el número en la cadena
    #     numero_encontrado = re.search(r'\b\d+\b', cadena)

    #     # Verificar si se encontró un número
    #     if numero_encontrado:
    #         return numero_encontrado.group()
    #     else:
    #         return None
    #         # Función para verificar si el elemento está completamente dentro de la vista

    # def is_element_fully_visible(self, element, driver):
    #     try:
    #         # Esperar hasta que el elemento sea visible
    #         WebDriverWait(driver, 10).until(
    #             EC.visibility_of(element)
    #         )

    #         # Obtener la posición y el tamaño del elemento
    #         location = element.location
    #         size = element.size

    #         # Calcular las coordenadas del borde inferior del elemento
    #         bottom = location['y'] + size['height']

    #         # Verificar si el borde inferior está dentro de la ventana visible
    #         return 0 <= bottom <= driver.execute_script("return window.innerHeight;")
    #     except Exception as e:
    #         print(f'Error: {e}')
    #         return False
        
    # def find_jsonLabel(self, obj, etiqueta):
    #         resultado = []
    #         def buscar_recursivamente(obj):
    #             if isinstance(obj, dict):
    #                 for key, value in obj.items():
    #                     if key == etiqueta:
    #                         resultado.append(value)
    #                     elif isinstance(value, (dict, list)):
    #                         buscar_recursivamente(value)
    #             elif isinstance(obj, list):
    #                 for item in obj:
    #                     buscar_recursivamente(item)

    #         buscar_recursivamente(obj)
    #         return resultado
    # def limpiar_lista(self, lista):
    #     # Eliminar valores None
    #     lista_sin_none = [valor for valor in lista if valor is not None]

    #     # Eliminar duplicados y mantener el orden original
    #     lista_sin_duplicados = []
    #     conjunto_auxiliar = set()

    #     for valor in lista_sin_none:
    #         if valor not in conjunto_auxiliar:
    #             conjunto_auxiliar.add(valor)
    #             lista_sin_duplicados.append(valor)

    #     return lista_sin_duplicados
    # def es_entero(self, valor):
    #     try:
    #         float(valor)
    #         return True
    #     except ValueError:
    #         return False
    
    # def convertir_string_decimal(self, array):
    #     # Convertir a datos decimales
    #     array = [float(valor) for valor in array]

    #     # Ordenar de mayor a menor
    #     return sorted(array)
## Comando para extraer 
### scrapy crawl Zapatillas_Puma -o Puma.json -t json
#   scrapy crawl Zapatillas_Puma -o Puma.csv -t csv