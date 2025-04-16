import os
import requests
from bs4 import BeautifulSoup
import json
import hashlib
import datetime
import pytz


def simular():
    return "Titulo", 100000, 150000, "10%", 90000


archivo_precios = "precios_guardados.json"


def cargar_precios():
    try:
        with open(archivo_precios, "r") as archivo:
            contenido = archivo.read()
            if not contenido.strip():
                return {}
            return json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(archivo_precios, "w") as archivo:
            json.dump({}, archivo)
        return {}


def guardar_precios(precios):
    precios_existentes = cargar_precios()
    
    for id_unico, datos in precios.items():
        precio_actual = datos.get("precio_actual")
        
        if id_unico in precios_existentes:
            precio_anterior_guardado = precios_existentes[id_unico].get("precio_actual")
            
            if precio_actual and precio_actual != precio_anterior_guardado:
                precios[id_unico]["precio_anterior"] = precio_anterior_guardado
        
        if id_unico in precios_existentes:
            precios_existentes[id_unico].update(precios[id_unico])
        else:
            precios_existentes[id_unico] = precios[id_unico]
    
    with open(archivo_precios, "w") as archivo:
        json.dump(precios_existentes, archivo)


precios_guardados = cargar_precios()


def generar_id_unico(link):
    return hashlib.md5(link.encode()).hexdigest()


def obtener(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    nombre_element = soup.find(class_="ui-pdp-title")
    nombre_obtenido = nombre_element.get_text().strip() if nombre_element else None
    nombre = (
        nombre_obtenido
        if isinstance(nombre_obtenido, str)
        else nombre_obtenido.get_text().strip() if nombre_obtenido else None
    )

    precio_actual = None
    descuento = None

    # Buscar el precio de un solo pago (1 pago)
    precio_un_pago = None
    
    # Intentamos diferentes estrategias para encontrar el precio de un solo pago
    
    # Estrategia 1: Buscar elementos con texto "1 pago" o "Precio de contado"
    pago_texts = ['1 pago', 'precio de contado', 'precio contado', 'precio efectivo', 'en un pago']
    for pago_text in pago_texts:
        subtitle_elements = soup.find_all(string=lambda text: text and pago_text in text.lower())
        
        if subtitle_elements:
            for elem in subtitle_elements:
                # Buscar hacia arriba en el árbol DOM para encontrar el contenedor de precio
                parent = elem.parent
                price_container = None
                
                # Buscar hasta 5 niveles hacia arriba
                for _ in range(5):
                    if parent and parent.name:
                        # Primero intentamos encontrar el precio directamente
                        price_container = parent.find('span', class_='andes-money-amount__fraction')
                        if price_container:
                            break
                            
                        # Si no lo encontramos, buscamos en el contenedor padre
                        parent = parent.parent
                    else:
                        break
                
                if price_container:
                    precio_actual = price_container.get_text().strip().replace(".", "").replace(",", ".")
                    break
            
            if precio_actual:
                break
    
    # Estrategia 2: Buscar el precio principal (generalmente el primero)
    if not precio_actual:
        # Buscar todos los contenedores de precio
        price_containers = soup.find_all('div', class_='ui-pdp-price')
        
        if price_containers:
            # Primero intentar encontrar un contenedor que tenga texto de un solo pago
            for container in price_containers:
                # Verificar si este contenedor menciona un solo pago
                pago_element = container.find(string=lambda text: text and any(pago_text in text.lower() for pago_text in pago_texts))
                if pago_element:
                    price_fraction = container.find('span', class_='andes-money-amount__fraction')
                    if price_fraction:
                        precio_actual = price_fraction.get_text().strip().replace(".", "").replace(",", ".")
                        break
            
            # Si no encontramos un contenedor con texto de un solo pago, buscamos uno sin cuotas
            if not precio_actual:
                for container in price_containers:
                    # Verificar si este contenedor no menciona cuotas
                    if not container.find(string=lambda text: text and 'cuota' in text.lower()):
                        price_fraction = container.find('span', class_='andes-money-amount__fraction')
                        if price_fraction:
                            precio_actual = price_fraction.get_text().strip().replace(".", "").replace(",", ".")
                            break
    
    # Estrategia 3: Buscar en todos los elementos de precio y priorizar el que tenga texto de un solo pago
    if not precio_actual:
        precio_elements = soup.find_all("div", class_="ui-pdp-price__second-line")
        
        if precio_elements:
            # Primero intentamos encontrar un elemento que tenga texto de un solo pago
            for precio_element in precio_elements:
                # Buscar si hay algún texto de un solo pago cerca
                parent_container = precio_element.find_parent('div', class_='ui-pdp-price')
                if parent_container:
                    pago_element = parent_container.find(string=lambda text: text and any(pago_text in text.lower() for pago_text in pago_texts))
                    if pago_element:
                        precio_obtenido = precio_element.find("span", class_="andes-money-amount__fraction")
                        if precio_obtenido:
                            precio_actual = precio_obtenido.get_text().strip().replace(".", "").replace(",", ".")
                            break
            
            # Si no encontramos ninguno con texto de un solo pago, usamos el primero como fallback
            if not precio_actual and precio_elements:
                precio_element = precio_elements[0]
                precio_obtenido = precio_element.find("span", class_="andes-money-amount__fraction")
                if precio_obtenido:
                    precio_actual = precio_obtenido.get_text().strip().replace(".", "").replace(",", ".")
    
    # Buscar el descuento
    precio_element = soup.find("div", class_="ui-pdp-price__second-line")
    if precio_element:
        descuento_element = precio_element.find(
            "span", class_="andes-money-amount__discount"
        )
        if descuento_element:
            descuento = descuento_element.get_text().strip()

    return nombre, precio_actual, descuento


def procesar_links():
    nuevos_links = []

    with open("links.txt", "r") as file:
        for link in file:
            link = link.strip()
            id_unico = generar_id_unico(link)
            if id_unico not in precios_guardados:
                precios_guardados[id_unico] = {
                    "link": link,
                    "nombre": None,
                    "precio_actual": None,
                    "precio_anterior": None,
                    "descuento": None,
                }
                nuevos_links.append((id_unico, link))

    guardar_precios(precios_guardados)
    return nuevos_links


def generar_html(resultados):
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MELIPU</title>
        <link rel="icon" type="image/svg+xml" href="https://http2.mlstatic.com/frontend-assets/ml-web-navigation/ui-navigation/5.21.22/mercadolibre/favicon.svg">
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <link rel="manifest" href="./manifest.json" />
        <link rel="apple-touch-icon" href="./image/icon/icon-72x72.png" />
        <link rel="apple-touch-icon" href="./image/icon/icon-96x96.png" />
        <link rel="apple-touch-icon" href="./image/icon/icon-128x128.png" />
        <link rel="apple-touch-icon" href="./image/icon/icon-144x144.png" />
        <link rel="apple-touch-icon" href="./image/icon/icon-152x152.png" />
        <link rel="apple-touch-icon" href="./image/icon/icon-192x192.png" />
        <link rel="apple-touch-icon" href="./image/icon/icon-384x384.png" />
        <link rel="apple-touch-icon" href="./image/icon/icon-512x512.png" />
        <meta name="apple-mobile-web-app-status-bar" content="#FFD101" />
        <meta name="theme-color" content="#FFD101" />
        <style>
            body { font-family: 'Roboto', Arial, sans-serif; background-color: black; color: white; }
            .item { margin-bottom: 20px; }
            .nombre { color: #FAFAFA; font-weight: bold; text-decoration: none; }
            .mark_before { color: #FAFAFA; }
            .mark_after { color: #9E9E9E; }
            .precio_actual { color: #FFEB3B; }
            .precio_anterior { color: #FF9800; }
            .precio_no_disponible { color: #F44336; }
            .descuento { color: #4CAF50; font-size: 12px; }
            .oferta { color: #FFC107; font-size: 14px; }
            .actualizacion { color: #607D8B; align-text: right; font-size: 10px; }
        </style>
    </head>
    <body>
    <br/>
    """

    for id_unico, datos in resultados.items():
        link = datos["link"]
        nombre = datos["nombre"]
        precio_actual = datos["precio_actual"]
        precio_anterior = datos["precio_anterior"]
        descuento = datos["descuento"]

        try:
            precio_nuevo = float(precio_actual) if precio_actual else None
            id_titulo = nombre.replace(" ", "_").replace("...", "").rstrip("_")
            precio_anterior = float(precio_anterior) if precio_anterior else None

            precio_nuevo_formateado = (
                f"${precio_nuevo:,.0f}".replace(",", ".") if precio_nuevo else ""
            )
            precio_anterior_formateado = (
                f"${precio_anterior:,.0f}".replace(",", ".") if precio_anterior else ""
            )
            descuento = f"{descuento}" if descuento else ""

            html_content += f"""
            <div class="item">
                <a href="{link}" class="nombre">{nombre}</a></br>
                <span class="mark_before">> </span><span class="precio_actual" id="{id_titulo}">{precio_nuevo_formateado}</span><span class="descuento"> {descuento}</span></br>
                <span class="mark_after">- </span><span class="precio_anterior">{precio_anterior_formateado}</span></br>
            </div>
            """
        except Exception as e:
            continue

    actualizacion = datetime.datetime.now(
        pytz.timezone("America/Argentina/Buenos_Aires")
    ).strftime("%H:%M %d.%m.%y")

    html_content += f"""
    <div class="actualizacion">
        <br/>{actualizacion}
    </div>
    </body>
    </html>
    """
    return html_content


def main():
    nuevos_links = procesar_links()

    resultados = {}
    for id_unico, datos in precios_guardados.items():
        link = datos["link"]
        nombre, precio_actual, descuento = obtener(link)

        if datos["precio_actual"] != precio_actual:
            precios_guardados[id_unico]["precio_anterior"] = datos["precio_actual"]
            precios_guardados[id_unico]["precio_actual"] = precio_actual

        precios_guardados[id_unico]["nombre"] = nombre
        precios_guardados[id_unico]["descuento"] = descuento

        resultados[id_unico] = precios_guardados[id_unico]

    guardar_precios(precios_guardados)

    html_content = generar_html(resultados)
    with open("index.html", "w", encoding="utf-8") as html_file:
        html_file.write(html_content)


if __name__ == "__main__":
    main()
