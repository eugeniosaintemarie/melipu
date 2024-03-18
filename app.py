import requests
from bs4 import BeautifulSoup
import datetime
import pytz


def simular_publicacion_ficticia():
    return "Prueba", 100000, 200000


def obtener_nombre_y_precio(link):
    response = requests.get(link)
    if response.status_code != 200:
        return None, None

    soup = BeautifulSoup(response.text, "html.parser")
    nombre_element = soup.find(class_="ui-pdp-title")
    precio_element = soup.find("span", class_="andes-money-amount__fraction")

    if not nombre_element or not precio_element:
        return None, None

    precio_text = precio_element.get_text().strip().replace(".", "")
    return nombre_element.get_text().strip(), float(precio_text)


def generar_html(resultados):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Publicaciones-Precios</title>
        <link rel="icon" type="image/svg+xml" href="https://http2.mlstatic.com/frontend-assets/ml-web-navigation/ui-navigation/5.21.22/mercadolibre/favicon.svg">
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Roboto', Arial, sans-serif; background-color: black; color: white; }
            .item { margin-bottom: 20px; }
            .nombre { font-weight: bold; color: white; text-decoration: none; }
            .precio_actual { color: yellow; }
            .precio_anterior { color: red; }
            .actualizacion { font-size: 0.75em; color: #9E9E9E; }
        </style>
    </head>
    <body>
    """

    for nombre_publicacion, precio_nuevo, precio_anterior, enlace in resultados:
        nombre_publicacion_link = f'<a href="{enlace}" target="_blank" class="nombre">{nombre_publicacion}</a>'
        precio_nuevo_formateado = f"${precio_nuevo:,.0f}" if precio_nuevo else None
        precio_anterior_formateado = (
            f"${precio_anterior:,.0f}" if precio_anterior else None
        )
        if precio_anterior:
            html_content += f"""
            <div class="item">
                <div>{nombre_publicacion_link}</div>
                <div class="precio_actual">Precio actual: {precio_nuevo_formateado}</div>
                <div class="precio_anterior">Precio anterior: {precio_anterior_formateado}</div>
            </div>
            """
        else:
            html_content += f"""
            <div class="item">
                <div>{nombre_publicacion_link}</div>
                <div class="precio_actual">Precio actual: {precio_nuevo_formateado}</div>
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

    return html_content


def main():
    mostrar_publicacion_ficticia = True
    publicacion_ficticia = (
        simular_publicacion_ficticia() if mostrar_publicacion_ficticia else None
    )

    with open("links.txt", "r") as file:
        enlaces = [line.strip() for line in file]

    precios_guardados = {}
    resultados = []

    if publicacion_ficticia:
        nombre_publicacion, precio_actual, precio_anterior = publicacion_ficticia
        enlace_ficticio = "https://google.com"
        resultados.append(
            (nombre_publicacion, precio_actual, precio_anterior, enlace_ficticio)
        )

    for enlace in enlaces:
        nombre_publicacion, precio_nuevo = obtener_nombre_y_precio(enlace)
        if nombre_publicacion and precio_nuevo:
            nombre_publicacion = nombre_publicacion[:32] + "..."
            if enlace not in precios_guardados:
                precios_guardados[enlace] = {
                    "precio_actual": precio_nuevo,
                    "precio_anterior": None,
                }
                resultados.append((nombre_publicacion, precio_nuevo, None, enlace))
            elif precio_nuevo != precios_guardados[enlace]["precio_actual"]:
                precios_guardados[enlace]["precio_anterior"] = precios_guardados[
                    enlace
                ]["precio_actual"]
                precios_guardados[enlace]["precio_actual"] = precio_nuevo
                resultados.append(
                    (
                        nombre_publicacion,
                        precio_nuevo,
                        precios_guardados[enlace]["precio_anterior"],
                        enlace,
                    )
                )

    html_content = generar_html(resultados)
    with open("index.html", "w", encoding="utf-8") as html_file:
        html_file.write(html_content)


if __name__ == "__main__":
    main()
