import os
import requests
from bs4 import BeautifulSoup
import json
import datetime
import pytz
import firebase_admin
from firebase_admin import credentials, messaging


def simular():
    return "Simulación", 100000, 150000, "10%", 90000


def initialize_firebase():
    try:
        creds_json = os.getenv("FIREBASE_ADMIN_CREDENTIALS")
        if creds_json:
            creds_dict = json.loads(creds_json)
            cred = credentials.Certificate(creds_dict)
        else:
            cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Error inicializando Firebase: {str(e)}")
        raise


def send_notification(token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )
    response = messaging.send(message)


def obtener(link, previous_price, token):
    try:
        response = requests.get(link, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        nombre_element = soup.find(class_="ui-pdp-title")
        nombre = nombre_element.get_text().strip() if nombre_element else None
        precio_actual = None
        precio_anterior = None
        descuento = None

        precio_element = soup.find("div", class_="ui-pdp-price__second-line")
        if precio_element:
            precio_obtenido = precio_element.find(
                "span", class_="andes-money-amount__fraction"
            )
            precio_actual = (
                precio_obtenido.get_text().strip().replace(".", "").replace(",", ".")
                if precio_obtenido
                else None
            )
            precio_anterior_element = precio_element.find(
                "s", class_="andes-money-amount__original"
            )
            precio_anterior = (
                precio_anterior_element.get_text()
                .strip()
                .replace(".", "")
                .replace(",", ".")
                if precio_anterior_element
                else None
            )
            descuento_element = precio_element.find(
                "span", class_="andes-money-amount__discount"
            )
            descuento = (
                descuento_element.get_text().strip() if descuento_element else None
            )
        if (
            precio_actual
            and previous_price
            and float(precio_actual) != float(previous_price)
        ):
            try:
                send_notification(
                    token,
                    "Precio actualizado",
                    f"El nuevo precio es ${float(precio_actual):,.2f}",
                )
            except Exception as e:
                print(f"Error al enviar notificación: {str(e)}")
        return nombre, precio_actual, precio_anterior, descuento

    except requests.RequestException as e:
        print(f"Error al obtener datos de {link}: {str(e)}")
        return None, None, None, None
    except Exception as e:
        print(f"Error inesperado al procesar {link}: {str(e)}")
        return None, None, None, None


def generar_html(resultados, precios_guardados):
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

    for enlace, (
        nombre,
        precio_nuevo,
        precio_anterior,
        descuento,
    ) in resultados.items():
        nombre_publicacion = nombre
        precio_nuevo_str = precio_nuevo
        precio_anterior_str = precio_anterior

        try:
            precio_nuevo = float(precio_nuevo_str) if precio_nuevo_str else None
            id_titulo = (
                nombre_publicacion.replace(" ", "_").replace("...", "").rstrip("_")
            )
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
                <span class="mark_after">< </span><span class="precio_anterior">{precio_anterior_formateado}</span></br>
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
    try:
        mostrar_prueba = False
        publicacion_ficticia = None
        if mostrar_prueba:
            publicacion_ficticia = simular()

        initialize_firebase()

        device_token = "TOKEN_DEL_DISPOSITIVO"

        enlaces, precios_guardados, resultados = [], {}, {}
        enlaces_procesados = set()

        try:
            with open("links.txt", "r", encoding="utf-8") as file:
                enlaces = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print("Error: No se encontró el archivo links.txt")
            return

        if not enlaces:
            print("No hay enlaces para procesar")
            return

        for link in enlaces:
            if link not in enlaces_procesados:
                resultados[link] = obtener(
                    link, precios_guardados.get(link), device_token
                )
                enlaces_procesados.add(link)

        if publicacion_ficticia:
            resultados["https://articulo-de-prueba.meli"] = publicacion_ficticia

        html_content = generar_html(resultados, precios_guardados)

        with open("output.html", "w", encoding="utf-8") as html_file:
            html_file.write(html_content)
        print("HTML generado exitosamente en output.html")
    except Exception as e:
        print(f"Error en la ejecución principal: {str(e)}")


if __name__ == "__main__":
    main()
