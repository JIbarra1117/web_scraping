
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
from bs4 import BeautifulSoup
import os
import re

class Metodos():
        
    def limpiar_lista_data(lista_datos):
        resultado = []
        for data in lista_datos:
            # print('CALZADO DEPORTIVO: '+data)
            val = data.strip()
            resultado.append(val)
        return resultado

    def buscar_palabra(cadena, palabra):
        # Convierte la cadena y la palabra a minúsculas para hacer la búsqueda insensible a mayúsculas
        cadena = cadena.lower()
        palabra = palabra.lower()
        # Verifica si la palabra está presente en la cadena
        if palabra in cadena:
            return True
        else:
            return False
    def extraer_numero(cadena):
        cadena =  cadena.replace(',','')
        # Usar una expresión regular para encontrar el número en la cadena
        numero_encontrado = re.search(r'\b\d+\b', cadena)

        # Verificar si se encontró un número
        if numero_encontrado:
            return numero_encontrado.group()
        else:
            return None
            # Función para verificar si el elemento está completamente dentro de la vista

    def is_element_fully_visible(element, driver):
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
    def limpiar_lista(lista):
        # Eliminar valores None
        lista_sin_none = [valor for valor in lista if valor is not None]

        # Eliminar duplicados y mantener el orden original
        lista_sin_duplicados = []
        conjunto_auxiliar = set()

        for valor in lista_sin_none:
            if valor not in conjunto_auxiliar:
                conjunto_auxiliar.add(valor)
                lista_sin_duplicados.append(valor)

        return lista_sin_duplicados
    def es_entero(valor):
        try:
            float(valor)
            return True
        except ValueError:
            return False
    
    def convertir_string_decimal(array):
        # Convertir a datos decimales
        array = [float(valor) for valor in array]

        # Ordenar de mayor a menor
        return sorted(array)
    
    def convertir_string_entero(array):
        # Convertir a datos decimales
        array = [int(valor) for valor in array]

        # Ordenar de mayor a menor
        return sorted(array)
    
    def save_html_to_file(html_content, titulo):
        # Directorio donde se almacenarán los archivos HTML
        output_directory = 'HTML'

        # Crear el directorio si no existe
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Nombre del archivo HTML
        filename = os.path.join(output_directory, titulo+'.html')

        # Guardar el HTML en el archivo
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(html_content)
    # Cerrar Alertas mediante javascript
    def cerrar_alerta(driver):
        try:
            # driver.driver = driver
            driver.wait = WebDriverWait(driver, 10)
            # Esperar hasta que la alerta esté presente
            alert = driver.wait.until(EC.alert_is_present())
            # Cerrar la alerta (puedes usar accept() para aceptarla)
            alert.dismiss()
            print("Alerta cerrada con éxito.")
        except TimeoutException:
            print("No se encontró ninguna alerta en este momento.")
            # WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.XPATH, "//button[@class='window-modal__close']")) )
    
    def obtener_primeros_ocho(datos):
        """
        Obtiene los primeros 8 elementos de una lista.

        Parameters:
        - datos (list): La lista de la cual se obtendrán los elementos.

        Returns:
        - list: Los primeros 8 elementos de la lista.
        """
        if len(datos)>7:
            return datos[:8]
        else:
            return datos
    
    def posicion_scroll(driver):
        # Ejecutar JavaScript para obtener la posición del scroll
        return driver.execute_script("return (window.pageYOffset !== undefined) ? window.pageYOffset : (document.documentElement || document.body.parentNode || document.body).scrollTop;")
    # Reconocer cuando un elemento es visible
    def is_element_visible_in_viewport(driver, element):
        rect = element.rect
        viewport_height = driver.execute_script("return window.innerHeight;")
        return rect['y'] >= 0 and rect['y'] <= viewport_height
    

    def eliminar_caracter_y_convertir_a_float(df, nombre_columna, caracter_a_eliminar):
        """
        Elimina un carácter específico de una columna en un DataFrame y convierte la columna a tipo float.

        Parameters:
            df (pandas.DataFrame): El DataFrame.
            nombre_columna (str): El nombre de la columna que se va a modificar.
            caracter_a_eliminar (str): El carácter que se va a eliminar de la columna.

        Returns:
            pandas.DataFrame: El DataFrame actualizado.
        """
        # Utilizar una función lambda para aplicar la conversión solo a valores que sean numéricos
        df[nombre_columna] = df[nombre_columna].apply(lambda x: float(x.replace(caracter_a_eliminar, '')) if str(x).replace(caracter_a_eliminar, '').replace('.', '').isdigit() else x)
        return df
    def obtener_contenido_p(html):
        """
        Extrae el contenido dentro de las etiquetas <p> del texto HTML.

        Parameters:
            html (str): El texto HTML.

        Returns:
            str: El contenido dentro de las etiquetas <p> o el texto original si no se encuentra ninguna etiqueta <p>.
        """
        # Utilizar BeautifulSoup para analizar el HTML
        soup = BeautifulSoup(html, 'html.parser')
        try:
            parser = html.fromstring(html) 
            # Encontrar todas las etiquetas <p>
            etiquetas_p = soup.find_all('p')
            etiquetas_span_1 = parser.xpath("(//span/span/span/span/text())[1]")
            etiquetas_span_2 = parser.xpath("(//span/span/span/span/text())[2]")

            if etiquetas_p:
                # Extraer el texto dentro de las etiquetas <p>
                contenido_p = [p.get_text(strip=True) for p in etiquetas_p]
                # Unir el contenido en una cadena
                contenido_p = ' '.join(contenido_p)
                return contenido_p
            else:
                # Devolver el texto original si no se encuentra ninguna etiqueta <p>
                return etiquetas_span_1+etiquetas_span_2
        except:
            print('No se pudo obtener html')
            return Metodos.eliminar_html_completo(html)
    # Elimina todo el texto que se encuentre dentro de un html
    def eliminar_html_completo(texto_html):
        """
        Elimina todo el contenido HTML y conserva solo el texto sin formato.

        Parameters:
            texto_html (str): El texto con formato HTML.

        Returns:
            str: El texto sin formato.
        """
        try:
            # Utilizar BeautifulSoup para eliminar todo el contenido HTML
            soup = BeautifulSoup(texto_html, 'html.parser')
            texto_sin_html = soup.get_text(separator='\n', strip=True)

            return texto_sin_html
        except:
            print('Error en eliminar HTML')
    def obtener_texto_especifico_desde_html(html):
        """
        Obtiene el texto específico deseado desde un fragmento HTML.

        Parameters:
            html (str): El fragmento HTML.

        Returns:
            str: El texto específico deseado.
        """
        # Crear un objeto BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Buscar todos los elementos de texto dentro del fragmento HTML
        texto_elementos = soup.find_all(text=True, recursive=False)

        # Unir el texto de los elementos encontrados
        texto_deseado = ' '.join(texto_elementos).strip()

        return texto_deseado
    
    def obtener_valor_mayor_de_string(rango_precio):
        '''
        Limpia el dato de un string para obtener el precio en float
        rango precio: "$118.97 - $140.00" o "$48.00" pero no "2"
        '''
        # Utilizar expresiones regulares para encontrar los valores entre '$'
        valores = re.findall(r'\$\s*([\d,]+(?:\.\d{2})?)', rango_precio)

        # Convertir los valores a números de punto flotante
        valores_float = [float(valor.replace(',', '')) for valor in valores]

        # Obtener el valor mayor
        valor_mayor = max(valores_float, default=None)

        return valor_mayor
    
    def obtener_texto_antes_de_caracter(texto,caracter_limite):
        # Divide el texto en una lista usando el punto como separador
        partes = texto.split(caracter_limite)
        
        # Toma la primera parte de la lista (antes del primer punto)
        texto_antes_del_punto = partes[0] if partes else texto
        
        return texto_antes_del_punto
    
    def eliminar_duplicados_obtener_maximo(lista):
        """
        Elimina valores duplicados y se obtiene el maximo
        """
        # Eliminar duplicados
        lista_sin_duplicados = list(set(lista))

        # Obtener el máximo
        maximo = max(lista_sin_duplicados)

        return maximo#lista_sin_duplicados, maximo
    
    def limpiar_array_espacios_en_blanco(array):
        return [elemento for elemento in array if elemento != '']
    

    class colors:
        RESET = '\033[0m'
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'

    # Función para imprimir con color
    def print_color(text, color):
        print(f"{color}{text}{Metodos.colors.RESET}")