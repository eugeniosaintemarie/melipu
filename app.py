import os
import json
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, messaging, firestore
import datetime
import pytz


firebase_admin_sdk_json_str = os.environ["FIREBASE_ADMIN_SDK"]
firebase_admin_sdk_json = json.loads(firebase_admin_sdk_json_str)
cred = credentials.Certificate(firebase_admin_sdk_json)
firebase_admin.initialize_app(cred)


def obtener_tokens():
    db = firestore.client()
    subcollection_ref = db.collection("tokens").document("YZ1lgw53iAFpxq8fUm8V")
    docs = subcollection_ref.collection("YZ1lgw53iAFpxq8fUm8V").stream()
    if not docs:
        return []
    else:
        tokens = [doc.to_dict().get("token") for doc in docs]
        return tokens


def enviar_notificacion(titulo, cuerpo, tokens):
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=titulo,
            body=cuerpo,
        ),
        tokens=tokens,
    )
    response = messaging.send_multicast(message)


def simular():
    return "Titulo", 100000, 150000, "10%", 90000


def obtener(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    nombre_element = soup.find(class_="ui-pdp-title")
    nombre_obtenido = nombre_element.get_text().strip()
    nombre = (
        nombre_obtenido
        if isinstance(nombre_obtenido, str)
        else nombre_obtenido.get_text().strip() if nombre_obtenido else None
    )

    precio_element = soup.find("div", class_="ui-pdp-price__second-line")

    if precio_element:
        precio_obtenido = precio_element.find(
            "span", class_="andes-money-amount__fraction"
        )
        if precio_obtenido:
            precio_actual = precio_obtenido.get_text().strip()
            precio_actual = precio_actual.replace(".", "").replace(",", ".")
        else:
            precio_actual = None
    else:
        precio_actual = None

    descuento_element = precio_element.select_one(
        ".ui-pdp-price__second-line__label.ui-pdp-color--GREEN.ui-pdp-size--MEDIUM .andes-money-amount__discount"
    )
    if descuento_element:
        descuento = descuento_element.get_text().strip()
    else:
        descuento = None

    contenedor_principal = soup.find(
        "div",
        class_="ui-pdp-container__col col-1 ui-pdp-container--column-right mt-16 pr-16",
    )
    if contenedor_principal:
        contenedor_row = contenedor_principal.find_parent(
            "div",
            class_="ui-pdp--sticky-wrapper ui-pdp--sticky-wrapper-right",
        )
        if contenedor_row:
            contenedor_form = contenedor_row.find_parent(
                "div", class_="ui-pdp-container__row"
            )
            if contenedor_form:
                contenedor_div = contenedor_form.find(
                    "div", class_="ui-pdp-container__row"
                )
                if contenedor_div:
                    oferta_element = contenedor_div.find(
                        "span", attrs={"data-testid": "price-part"}
                    )
                    if oferta_element:
                        oferta = oferta_element.get_text().strip().replace(",", ".")
                    else:
                        oferta = None
                else:
                    oferta = None
            else:
                oferta = None
        else:
            oferta = None

    return nombre, precio_actual, descuento, oferta


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
        <link rel="manifest" href="https://eugeniosaintemarie.github.io/melipu/manifest.json" />
        <link rel="apple-touch-icon" href="https://eugeniosaintemarie.github.io/melipu/image/icon/icon-72x72.png" />
        <link rel="apple-touch-icon" href="https://eugeniosaintemarie.github.io/melipu/image/icon/icon-96x96.png" />
        <link rel="apple-touch-icon" href="https://eugeniosaintemarie.github.io/melipu/image/icon/icon-128x128.png" />
        <link rel="apple-touch-icon" href="https://eugeniosaintemarie.github.io/melipu/image/icon/icon-144x144.png" />
        <link rel="apple-touch-icon" href="https://eugeniosaintemarie.github.io/melipu/image/icon/icon-152x152.png" />
        <link rel="apple-touch-icon" href="https://eugeniosaintemarie.github.io/melipu/image/icon/icon-192x192.png" />
        <link rel="apple-touch-icon" href="https://eugeniosaintemarie.github.io/melipu/image/icon/icon-384x384.png" />
        <link rel="apple-touch-icon" href="https://eugeniosaintemarie.github.io/melipu/image/icon/icon-512x512.png" />
        <meta name="apple-mobile-web-app-status-bar" content="#FFD101" />
        <meta name="theme-color" content="#FFD101" />
        <script src="https://eugeniosaintemarie.github.io/melipu/app.js"></script>
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

    for (
        id_unico,
        enlace,
        (
            nombre,
            precio_nuevo,
            precio_anterior,
            descuento,
            oferta,
        ),
    ) in resultados.items():
        if enlace == "https://google.com":
            nombre_publicacion, precio_actual, descuento, oferta = simular
            precio_nuevo_str = str(precio_nuevo)
            precio_anterior_str = str(precio_anterior)
        else:
            nombre_publicacion, precio_actual, descuento, oferta = obtener(enlace)
            if nombre_publicacion and precio_nuevo:
                nombre_publicacion = nombre_publicacion[:32] + "..."
                precio_nuevo_str = str(precio_nuevo)
                precio_anterior_str = (
                    str(precios_guardados[enlace]["precio_anterior"])
                    if enlace in precios_guardados
                    else None
                )
            else:
                continue
        if enlace not in precios_guardados:
            precios_guardados[enlace] = {
                "precio_actual": precio_nuevo_str,
                "precio_anterior": None,
                "descuento": descuento,
                "oferta": oferta,
            }
        else:
            precios_guardados[enlace]["precio_anterior"] = precios_guardados[enlace][
                "precio_actual"
            ]
            precios_guardados[enlace]["precio_actual"] = precio_nuevo_str

        precio_nuevo = float(precio_nuevo) if precio_nuevo else None
        precio_anterior = float(precio_anterior) if precio_anterior else None
        precio_nuevo_formateado = (
            f"${precio_nuevo:,.0f}".replace(",", ".") if precio_nuevo else ""
        )
        precio_anterior_formateado = (
            f"${precio_anterior:,.0f}".replace(",", ".") if precio_anterior else ""
        )
        descuento = f"{descuento}" if descuento else ""
        oferta = f" {oferta}" if oferta else ""

        html_content += f"""
        <div class="item">
            <a href="{enlace}" class="nombre">{nombre}</a></br>
            <span class="precio_actual" id="{id_unico}"><span class="mark_before">> </span>{precio_nuevo_formateado}</span><span class="descuento"> {descuento}</span><span class="oferta"> {oferta}</span></br>
            <span class="precio_anterior"><span class="mark_after">< </span>{precio_anterior_formateado}</span></br>
        </div>
        """

    actualizacion = datetime.datetime.now(
        pytz.timezone("America/Argentina/Buenos_Aires")
    ).strftime("%Y/%m/%d %H:%M")
    html_content += f"""
    <div class="actualizacion">
        <br/>{actualizacion}
    </div>
    </body>
    </html>
    """
    html_content += """
        <script src="https://eugeniosaintemarie.github.io/melipu/app.js"></script>
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
        nombre, precio_nuevo, precio_anterior, descuento = publicacion_ficticia
        enlace_ficticio = "https://google.com"
        precio_actual_str = str(precio_nuevo)
        precio_anterior_str = str(precio_anterior)
        enlaces.append(enlace_ficticio)

    for enlace in enlaces:
        if enlace in enlaces_procesados:
            continue
        enlaces_procesados.add(enlace)

        if enlace == "https://google.com":
            nombre, precio_nuevo, precio_anterior, descuento = publicacion_ficticia
            precio_nuevo_str = str(precio_nuevo)
        else:
            nombre, precio_nuevo_str, descuento, oferta = obtener(enlace)

            if nombre and precio_nuevo_str:
                nombre = nombre[:32] + "..."
            else:
                continue

        if enlace not in precios_guardados:
            precios_guardados[enlace] = {
                "precio_actual": precio_nuevo_str,
                "precio_anterior": None,
                "descuento": descuento,
                "oferta": oferta,
            }
        else:
            precios_guardados[enlace]["precio_anterior"] = precios_guardados[enlace][
                "precio_actual"
            ]
            precios_guardados[enlace]["precio_actual"] = precio_nuevo_str

        resultados[enlace] = (
            nombre,
            precio_nuevo_str,
            precios_guardados[enlace]["precio_anterior"],
            descuento,
            oferta,
        )

    html_content = generar_html(resultados, precios_guardados, publicacion_ficticia)
    with open("index.html", "w", encoding="utf-8") as html_file:
        html_file.write(html_content)


if __name__ == "__main__":
    main()
