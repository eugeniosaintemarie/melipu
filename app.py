import requests
from bs4 import BeautifulSoup
import datetime

color_reset = "\033[0m"
color_rojo = "\033[91m"
color_naranja = "\033[38;5;208m"
color_azul = "\033[94m"
color_celeste = "\033[96m"
color_amarillo = "\033[93m"
color_verde = "\033[92m"


def obtener_nombre_y_precio(link):
    response = requests.get(link)

    if response.status_code != 200:
        print(color_rojo + f"No se pudo acceder al link {link}" + color_reset)
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    class_id_nombre = "ui-pdp-title"
    nombre_element = soup.find(class_=class_id_nombre)

    precio_container = soup.find("div", class_="ui-pdp-price__second-line")
    if precio_container:
        class_id_precio = "andes-money-amount__fraction"
        precio_element = precio_container.find("span", class_=class_id_precio)
    else:
        precio_element = None

    if precio_element:
        precio_actual = precio_element.get_text().strip()
        nombre_publicacion = (
            nombre_element.get_text().strip()
            if nombre_element
            else color_rojo
            + f"Nombre de publicacion no encontrado {link}"
            + color_reset
        )
        return nombre_publicacion, precio_actual
    else:
        print(
            color_rojo
            + f"Precio de publicacion no encontrado {nombre_publicacion}"
            + color_reset
        )
        return None


def generar_html(resultados):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Publicaciones-Precios</title>
        <link rel="icon" type="image/svg+xml" href="https://http2.mlstatic.com/frontend-assets/ml-web-navigation/ui-navigation/5.21.22/mercadolibre/favicon.svg">
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Roboto', Arial, sans-serif; }
            .item { margin-bottom: 20px; }
            .nombre { font-weight: bold; }
            .precio { color: green; }
            .precio_anterior { color: red; }
            .actualizacion { font-size: 0.8em; text-align: center; }
            .actualizacion-small { font-size: 0.6em; text-align: center; }
        </style>
    </head>
    <body>
    """

    for index, resultado in enumerate(resultados, start=1):
        nombre_publicacion, precio_nuevo, precio_anterior = resultado
        if precio_anterior:
            html_content += f"""
            <div class="item">
                <div class="nombre">{nombre_publicacion}</div>
                <div class="precio">Precio actual: ${precio_nuevo}</div>
                <div class="precio_anterior">Precio anterior: ${precio_anterior}</div>
            </div>
            """
        else:
            html_content += f"""
            <div class="item">
                <div class="nombre">{nombre_publicacion}</div>
                <div class="precio">Precio actual: ${precio_nuevo}</div>
            </div>
            """

    actualizacion = datetime.datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).strftime("%Y-%m-%d %H:%M:%S")
    html_content += f"""
    <div class="actualizacion-small">
        <br/><br/><br/>Última actualización:{actualizacion}
    </div>
    </body>
    </html>
    """

    return html_content


def main():
    with open("links.txt", "r") as file:
        enlaces = [line.strip() for line in file]

    precios_guardados = {}
    resultados = []

    for enlace in enlaces:
        resultado_obtencion = obtener_nombre_y_precio(enlace)
        if resultado_obtencion:
            nombre_publicacion, precio_nuevo = resultado_obtencion
            nombre_publicacion = nombre_publicacion[:32] + "..."
            if enlace not in precios_guardados:
                precios_guardados[enlace] = {
                    "precio_actual": precio_nuevo,
                    "precio_anterior": None,
                }
                resultados.append((nombre_publicacion, precio_nuevo, None))
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
                    )
                )

    html_content = generar_html(resultados)
    with open("index.html", "w", encoding="utf-8") as html_file:
        html_file.write(html_content)


if __name__ == "__main__":
    main()
