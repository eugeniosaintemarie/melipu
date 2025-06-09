import os
import requests
from bs4 import BeautifulSoup
import json
import hashlib
import datetime
import pytz
import copy


#def simular():
#    return "Titulo", 100000, 150000, "10%", 90000


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


def guardar_precios(data_to_save):
    with open(archivo_precios, "w") as archivo:
        json.dump(data_to_save, archivo)


precios_guardados = cargar_precios()


def generar_id_unico(link):
    return hashlib.md5(link.encode()).hexdigest()


def procesar_links(current_prices_from_json):
    with open("links.txt", "r") as file:
        for link in file:
            link = link.strip()
            id_unico = generar_id_unico(link)
            if id_unico not in current_prices_from_json:
                current_prices_from_json[id_unico] = {
                    "link": link,
                    "nombre": None,
                    "precio_actual": None,
                    "precio_anterior": None,
                    "descuento": None,
                }
    return current_prices_from_json


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
    class_hierarchy = [
        ["andes-money-amount", "ui-pdp-price__part", "andes-money-amount--cents-superscript", "andes-money-amount--compact"],
        ["price-part"],
        ["ui-pdp-price__second-line"],
        ["ui-pdp-price__main-container"]
    ]
    for classes in class_hierarchy:
        selector = "." + ".".join(classes) + " .andes-money-amount__fraction"
        price_fraction = soup.select_one(selector)
        if price_fraction:
            precio_actual = price_fraction.get_text().strip().replace(".", "").replace(",", ".")
            break
    if not precio_actual:
        price_fraction = soup.find('span', class_='andes-money-amount__fraction')
        if price_fraction:
            precio_actual = price_fraction.get_text().strip().replace(".", "").replace(",", ".")
    descuento = soup.find("div", class_="ui-pdp-price__second-line")
    if descuento:
        descuento = descuento.find(
            "span", class_="andes-money-amount__discount"
        )
        if descuento:
            descuento = descuento.get_text().strip()
    return nombre, precio_actual, descuento


def generar_html(resultados):
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MELIPU</title>
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
        <meta http-equiv="Pragma" content="no-cache" />
        <meta http-equiv="Expires" content="0" />
        <link rel="icon" type="image/svg+xml" href="https://http2.mlstatic.com/frontend-assets/ml-web-navigation/ui-navigation/5.21.22/mercadolibre/favicon.svg">
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
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
        <br/>
        <a href="https://mercadotrack.com/MLA" target="_blank" class="actualizacion" style="color:rgb(17 82 253) !important; text-decoration:none !important;">MercadoTrack </a>
        {actualizacion}
        <a href="https://github.com/eugeniosaintemarie/melipu/actions/workflows/python-app.yml" target="_blank" title="Actualizar manualmente" style="margin-left: 5px; color: #607D8B; text-decoration: none;"><i class="fas fa-sync-alt"></i></a>
    </div>
    </body>
    </html>
    """
    return html_content


def main():
    precios_json_inicio_run = cargar_precios()
    items_a_procesar = procesar_links(copy.deepcopy(precios_json_inicio_run))
    resultados_finales = {}
    for id_unico, datos_template in items_a_procesar.items():
        link = datos_template["link"]
        nombre_scraped, precio_actual_scraped, descuento_scraped = obtener(link)
        precio_actual_viejo_de_json = precios_json_inicio_run.get(id_unico, {}).get("precio_actual")
        item_final_data = {}
        item_final_data["link"] = link
        item_final_data["nombre"] = nombre_scraped
        item_final_data["descuento"] = descuento_scraped
        item_final_data["precio_actual"] = precio_actual_scraped
        if precio_actual_scraped is not None and precio_actual_scraped != precio_actual_viejo_de_json:
            item_final_data["precio_anterior"] = precio_actual_viejo_de_json
        elif precio_actual_viejo_de_json is not None and precio_actual_scraped is None:
            item_final_data["precio_anterior"] = precio_actual_viejo_de_json
        else:
            item_final_data["precio_anterior"] = precios_json_inicio_run.get(id_unico, {}).get("precio_anterior")
        resultados_finales[id_unico] = item_final_data
    guardar_precios(resultados_finales)
    html_content = generar_html(resultados_finales)
    with open("index.html", "w", encoding="utf-8") as html_file:
        html_file.write(html_content)


if __name__ == "__main__":
    main()
