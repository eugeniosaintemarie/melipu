import os
import json
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, messaging, firestore
from pyfcm import FCMNotification
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


def simular_publicacion_ficticia():
    return "Producto de prueba", 100000, 150000, "10%"


def obtener_nombre_y_precio(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    class_id_nombre = "ui-pdp-title"
    nombre_element = soup.find(class_=class_id_nombre)
    precio_container = soup.find("div", class_="ui-pdp-price__second-line")
    if precio_container:
        class_id_precio = "andes-money-amount__fraction"
        precio_element = precio_container.find("span", class_=class_id_precio)
    else:
        precio_element = None
    descuento_element = precio_container.select_one(
        ".ui-pdp-price__second-line__label.ui-pdp-color--GREEN.ui-pdp-size--MEDIUM .andes-money-amount__discount"
    )
    descuento = descuento_element.get_text().strip() if descuento_element else None
    if precio_element:
        precio_actual = precio_element.get_text().strip()
        precio_actual = precio_actual.replace(".", "").replace(",", ".")
        nombre_publicacion = (
            nombre_element.get_text().strip() if nombre_element else None
        )
        return nombre_publicacion, precio_actual, descuento
    else:
        return None, None, None


def generar_html(resultados, enlaces, precios_guardados, publicacion_ficticia):
    push_service = FCMNotification(
        api_key="BBZWqDE__B3Y8ApoiALHUXuvQAxMejyJQWF09sKN20auDT1ojrOTt82QLCALgh645j9lZ6ReVokHfkiUyLZVqDw"
    )
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MELIPU</title>
        <script src="https://eugeniosaintemarie.github.io/melipu/app.js"></script>
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
        <meta name="apple-mobile-web-app-status-bar" content="#ffe600" />
        <meta name="theme-color" content="#ffe600" />
        <style>
            body { font-family: 'Roboto', Arial, sans-serif; background-color: black; color: white; }
            .item { margin-bottom: 20px; }
            .nombre { color: white; font-weight: bold; text-decoration: none; }
            .mark_before { color: white; }
            .mark_after { color: grey; }
            .precio_actual { color: yellow; }
            .precio_anterior { color: orange; }
            .precio_no_disponible { color: red; }
            .descuento { color: green; font-size: 0.80em; }
            .actualizacion { color: #FFD100; font-size: 0.75em; }
        </style>
    </head>
    <body>
    <br/>
    """
    for enlace in enlaces:
        if enlace == "https://google.com":
            nombre_publicacion, precio_nuevo, precio_anterior, descuento = (
                publicacion_ficticia
            )
            precio_nuevo_str = str(precio_nuevo)
            precio_anterior_str = str(precio_anterior)
        else:
            nombre_publicacion, precio_nuevo, descuento = obtener_nombre_y_precio(
                enlace
            )
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
                "precio_anterior": precio_anterior_str,
                "descuento": descuento,
            }
            resultados.append(
                (
                    nombre_publicacion,
                    precio_nuevo_str,
                    precio_anterior_str,
                    enlace,
                    descuento,
                )
            )
        else:
            precios_guardados[enlace]["precio_anterior"] = precios_guardados[enlace][
                "precio_actual"
            ]
            precios_guardados[enlace]["precio_actual"] = precio_nuevo_str
            precios_guardados[enlace]["descuento"] = descuento
            resultados.append(
                (
                    nombre_publicacion,
                    precio_nuevo_str,
                    precios_guardados[enlace]["precio_anterior"],
                    enlace,
                    descuento,
                )
            )

    for (
        nombre_publicacion,
        precio_nuevo,
        precio_anterior,
        enlace,
        descuento,
    ) in resultados:
        precio_nuevo = float(precio_nuevo) if precio_nuevo else None
        precio_anterior = float(precio_anterior) if precio_anterior else None
        precio_nuevo_formateado = (
            f"${precio_nuevo:,.0f}".replace(",", ".") if precio_nuevo else "-"
        )
        precio_anterior_formateado = (
            f"${precio_anterior:,.0f}".replace(",", ".") if precio_anterior else "-"
        )
        if descuento and "OFF" not in descuento:
            descuento_texto = f"{descuento} OFF"
        else:
            descuento_texto = descuento if descuento else ""
        html_content += f"""
        <div class="item">
            <a href="{enlace}" class="nombre">{nombre_publicacion}</a></br>
            <span class="precio_actual"><span class="mark_before">> </span>{precio_nuevo_formateado} <span class="descuento">{descuento_texto}</span></span></br>
            <span class="precio_anterior"><span class="mark_after">< </span>{precio_anterior_formateado}</span></br>
        </div>
        """

    actualizacion = datetime.datetime.now(
        pytz.timezone("America/Argentina/Buenos_Aires")
    ).strftime("%Y/%m/%d %H:%M")
    html_content += f"""
    <div class="actualizacion">
        <br/><br/><br/>{actualizacion}
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
    mostrar_publicacion_ficticia = False
    publicacion_ficticia = None
    if mostrar_publicacion_ficticia:
        publicacion_ficticia = simular_publicacion_ficticia()

    enlaces = []
    precios_guardados = {}
    resultados = []
    enlaces_procesados = set()

    with open("links.txt", "r") as file:
        enlaces = [line.strip() for line in file]

    if publicacion_ficticia:
        nombre_publicacion, precio_nuevo, precio_anterior, descuento = (
            publicacion_ficticia
        )
        enlace_ficticio = "https://google.com"
        precio_actual_str = str(precio_nuevo)
        precio_anterior_str = str(precio_anterior)
        enlaces.append(enlace_ficticio)

    for enlace in enlaces:
        if enlace in enlaces_procesados:
            continue
        enlaces_procesados.add(enlace)

        if enlace == "https://google.com":
            nombre_publicacion, precio_nuevo, precio_anterior, descuento = (
                publicacion_ficticia
            )
            precio_nuevo_str = str(precio_nuevo)
            precio_anterior_str = str(precio_anterior)
        else:
            nombre_publicacion, precio_nuevo, descuento = obtener_nombre_y_precio(
                enlace
            )
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

        if enlace not in enlaces_procesados:
            precios_guardados[enlace] = {
                "precio_actual": precio_nuevo_str,
                "precio_anterior": precio_anterior_str,
                "descuento": descuento,
            }
            resultados.append(
                (
                    nombre_publicacion,
                    precio_nuevo_str,
                    precio_anterior_str,
                    enlace,
                    descuento,
                )
            )

    html_content = generar_html(
        resultados, enlaces, precios_guardados, publicacion_ficticia
    )
    with open("index.html", "w", encoding="utf-8") as html_file:
        html_file.write(html_content)


if __name__ == "__main__":
    main()
