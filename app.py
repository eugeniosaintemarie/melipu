import requests
from bs4 import BeautifulSoup
import datetime
import pytz


def simular_publicacion_ficticia():
    return "Prueba", 100000, 200000


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
        ".ui-pdp-price__second-line__label.ui-pdp-color--GREEN.ui-pdp-size--MEDIUM"
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


def generar_html(resultados):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Shop publications</title>
        <script src="https://eugeniosaintemarie.github.io/shop-publications/app.js"></script>
        <link rel="icon" type="image/svg+xml" href="https://http2.mlstatic.com/frontend-assets/ml-web-navigation/ui-navigation/5.21.22/mercadolibre/favicon.svg">
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <!--PWA functionality start-->
        <link rel="manifest" href="https://eugeniosaintemarie.github.io/shop-publications/manifest.json" />
        <link rel="apple-touch-icon" href="https://eugeniosaintemarie.github.io/shop-publications/image/icon/icon-72x72.png" />
        <link rel="apple-touch-icon" href="https://eugeniosaintemarie.github.io/shop-publications/image/icon/icon-96x96.png" />
        <link rel="apple-touch-icon" href="https://eugeniosaintemarie.github.io/shop-publications/image/icon/icon-128x128.png" />
        <link rel="apple-touch-icon" href="https://eugeniosaintemarie.github.io/shop-publications/image/icon/icon-144x144.png" />
        <link rel="apple-touch-icon" href="https://eugeniosaintemarie.github.io/shop-publications/image/icon/icon-152x152.png" />
        <link rel="apple-touch-icon" href="https://eugeniosaintemarie.github.io/shop-publications/image/icon/icon-192x192.png" />
        <link rel="apple-touch-icon" href="https://eugeniosaintemarie.github.io/shop-publications/image/icon/icon-384x384.png" />
        <link rel="apple-touch-icon" href="https://eugeniosaintemarie.github.io/shop-publications/image/icon/icon-512x512.png" />
        <meta name="apple-mobile-web-app-status-bar" content="#ffe600" />
        <meta name="theme-color" content="#2d3277" />
        <!--PWA functionality finish-->
        <style>
            body { font-family: 'Roboto', Arial, sans-serif; background-color: black; color: white; }
            .item { margin-bottom: 20px; }
            .nombre { color: white; font-weight: bold; text-decoration: none; }
            .mark { color: white; }
            .precio_actual { color: yellow; }
            .precio_anterior { color: orange; }
            .precio_no_disponible { color: red; }
            .descuento { color: green; font-size: 0.80em; }
            .actualizacion { color: #9E9E9E; font-size: 0.75em; }
        </style>
    </head>
    <body>
    """

    for (
        nombre_publicacion,
        precio_nuevo,
        precio_anterior,
        enlace,
        descuento,
    ) in resultados:
        nombre_publicacion_link = (
            f'<a href="{enlace}" target="_blank" class="nombre">{nombre_publicacion if nombre_publicacion else "No disponible"}</a>'
            if nombre_publicacion
            else f'<a href="{enlace}" target="_blank" class="nombre"><span class="precio_no_disponible">No disponible</span></a>'
        )
        precio_nuevo_formateado = (
            "{:,.0f}".format(float(precio_nuevo)).replace(",", ".")
            if isinstance(precio_nuevo, str)
            and precio_nuevo.replace(".", "", 1).isdigit()
            else "No disponible"
        )
        precio_anterior_formateado = (
            "{:,.0f}".format(float(precio_anterior)).replace(",", ".")
            if isinstance(precio_anterior, str)
            and precio_anterior.replace(".", "", 1).isdigit()
            else "No disponible"
        )
        precio_nuevo_formateado = (
            f'<span class="precio_no_disponible">{precio_nuevo_formateado}</span>'
            if precio_nuevo_formateado == "No disponible"
            else precio_nuevo_formateado
        )
        precio_anterior_formateado = (
            f'<span class="precio_no_disponible">{precio_anterior_formateado}</span>'
            if precio_anterior_formateado == "No disponible"
            else precio_anterior_formateado
        )
        descuento_formateado = (
            f'<span class="descuento">{descuento}</span>' if descuento else ""
        )
        if precio_anterior:
            html_content += f"""
            <div class="item">
                <div>{nombre_publicacion_link}</div>
                <div class="precio_actual"><span class="mark">></span> {precio_nuevo_formateado} {descuento_formateado}</div>
                <div class="precio_anterior"><span class="mark"><</span> {precio_anterior_formateado}</div>
            </div><br/>
            """
        else:
            html_content += f"""
            <div class="item">
                <div>{nombre_publicacion_link}</div>
                <div class="precio_actual"><span class="mark">></span> {precio_nuevo_formateado} {descuento_formateado}</div>
            </div><br/>
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
        <script src="https://eugeniosaintemarie.github.io/shop-publications/app.js"></script>
        </body>
        </html>
    """

    return html_content


def main():
    mostrar_publicacion_ficticia = True
    publicacion_ficticia = (
        simular_publicacion_ficticia() if mostrar_publicacion_ficticia else None
    )

    enlaces = []
    precios_guardados = {}
    resultados = []

    with open("links.txt", "r") as file:
        enlaces = [line.strip() for line in file]

    if publicacion_ficticia:
        nombre_publicacion, precio_actual, precio_anterior = publicacion_ficticia
        enlace_ficticio = "https://google.com"
        precio_actual_str = str(precio_actual)
        precio_anterior_str = (
            str(precio_anterior) if precio_anterior is not None else None
        )
    resultados.append(
        (
            nombre_publicacion,
            precio_actual_str,
            precio_anterior_str,
            enlace_ficticio,
            None,
        )
    )

    for enlace in enlaces:
        nombre_publicacion, precio_nuevo, descuento = obtener_nombre_y_precio(enlace)
        if nombre_publicacion and precio_nuevo:
            nombre_publicacion = nombre_publicacion[:32] + "..."
            if enlace not in precios_guardados:
                precios_guardados[enlace] = {
                    "precio_actual": precio_nuevo,
                    "precio_anterior": None,
                    "descuento": descuento,
                }
                resultados.append(
                    (nombre_publicacion, precio_nuevo, None, enlace, descuento)
                )
            else:
                precios_guardados[enlace]["precio_anterior"] = precios_guardados[
                    enlace
                ]["precio_actual"]
                precios_guardados[enlace]["precio_actual"] = precio_nuevo
                precios_guardados[enlace]["descuento"] = descuento
                resultados.append(
                    (
                        nombre_publicacion,
                        precio_nuevo,
                        precios_guardados[enlace]["precio_anterior"],
                        enlace,
                        descuento,
                    )
                )

        html_content = generar_html(resultados)
        with open("index.html", "w", encoding="utf-8") as html_file:
            html_file.write(html_content)


if __name__ == "__main__":
    main()
