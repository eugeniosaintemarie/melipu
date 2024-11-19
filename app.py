import os
import requests
from bs4 import BeautifulSoup
import json
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
    with open(archivo_precios, "w") as archivo:
        json.dump(precios, archivo)


precios_guardados = cargar_precios()


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

    precio_element = soup.find("div", class_="ui-pdp-price__second-line")
    if precio_element:
        precio_obtenido = precio_element.find(
            "span", class_="andes-money-amount__fraction"
        )
        if precio_obtenido:
            precio_actual = (
                precio_obtenido.get_text().strip().replace(".", "").replace(",", ".")
            )

        descuento_element = precio_element.find(
            "span", class_="andes-money-amount__discount"
        )
        if descuento_element:
            descuento = descuento_element.get_text().strip()

    if link not in precios_guardados:
        precios_guardados[link] = {
            "nombre": nombre,
            "precio_actual": precio_actual,
            "precio_anterior": None,
            "descuento": descuento,
        }
    else:
        if precios_guardados[link]["precio_actual"] != precio_actual:
            precios_guardados[link]["precio_anterior"] = precios_guardados[link][
                "precio_actual"
            ]
            precios_guardados[link]["precio_actual"] = precio_actual

        precios_guardados[link]["nombre"] = nombre
        precios_guardados[link]["descuento"] = descuento

    guardar_precios(precios_guardados)

    return (
        precios_guardados[link]["nombre"],
        precios_guardados[link]["precio_actual"],
        precios_guardados[link]["precio_anterior"],
        precios_guardados[link]["descuento"],
    )


def generar_html(resultados, precios_guardados, simular):
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
        <script src="./app.js"></script>
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

    for enlace, datos in resultados.items():
        nombre, precio_nuevo_str, precio_anterior_str, descuento = datos

        try:
            precio_nuevo = float(precio_nuevo_str) if precio_nuevo_str else None
            id_titulo = nombre.replace(" ", "_").replace("...", "").rstrip("_")
            precio_anterior = (
                float(precio_anterior_str) if precio_anterior_str else None
            )

            precio_nuevo_formateado = (
                f"${precio_nuevo:,.0f}".replace(",", ".") if precio_nuevo else ""
            )
            precio_anterior_formateado = (
                f"${precio_anterior:,.0f}".replace(",", ".") if precio_anterior else ""
            )
            descuento = f"{descuento}" if descuento else ""

            html_content += f"""
            <div class="item">
                <a href="{enlace}" class="nombre">{nombre}</a></br>
                <span class="mark_before">> </span><span class="precio_actual" id="{id_titulo}">{precio_nuevo_formateado}</span><span class="descuento"> {descuento}</span></br>
                <span class="mark_after">- </span><span class="precio_anterior">{precio_anterior_formateado}</span></br>
            </div>
            """
        except Exception as e:
            print(f"Error generando HTML para {enlace}: {e}")
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
    mostrar_prueba = False
    publicacion_ficticia = None
    if mostrar_prueba:
        publicacion_ficticia = simular()

    enlaces = []
    precios_guardados = {}
    resultados = {}
    enlaces_procesados = set()

    with open("links.txt", "r") as file:
        enlaces = [line.strip() for line in file]

    if publicacion_ficticia:
        nombre, precio_nuevo, precio_anterior, descuento, oferta = publicacion_ficticia
        enlace_ficticio = "https://google.com"
        precio_actual_str = str(precio_nuevo)
        precio_anterior_str = str(precio_anterior)
        enlaces.append(enlace_ficticio)

    for enlace in enlaces:
        if enlace in enlaces_procesados:
            continue
        enlaces_procesados.add(enlace)

        if enlace == "https://google.com":
            nombre, precio_nuevo, precio_anterior, descuento, oferta = (
                publicacion_ficticia
            )
            precio_nuevo_str = str(precio_nuevo)
        else:
            nombre, precio_nuevo_str, precio_anterior_str, descuento = obtener(enlace)

            if nombre and precio_nuevo_str:
                nombre = nombre[:32] + "..."
            else:
                continue

        if enlace not in precios_guardados:
            precios_guardados[enlace] = {
                "precio_actual": precio_nuevo_str,
                "precio_anterior": None,
                "descuento": descuento,
                "oferta": None,
            }
        else:
            precio_anterior = precios_guardados[enlace]["precio_actual"]
            precios_guardados[enlace]["precio_actual"] = precio_nuevo_str
            precios_guardados[enlace]["precio_anterior"] = precio_anterior

        resultados[enlace] = (
            nombre,
            precio_nuevo_str,
            precios_guardados[enlace]["precio_anterior"],
            descuento,
        )

    html_content = generar_html(resultados, precios_guardados, publicacion_ficticia)
    with open("index.html", "w", encoding="utf-8") as html_file:
        html_file.write(html_content)


if __name__ == "__main__":
    main()
