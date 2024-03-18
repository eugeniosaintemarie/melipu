import requests
from bs4 import BeautifulSoup
import datetime
import pytz


def simular_publicacion_ficticia():
    return "Prueba", 100000, 200000


def obtener_nombre_y_precio(link):
    response = requests.get(link)

    if response.status_code != 200:
        print(f"No se pudo acceder al link {link}")
        return None, None

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
            else f"Nombre de publicacion no encontrado {link}"
        )
        return nombre_publicacion, precio_actual
    else:
        print(f"Precio de publicacion no encontrado {nombre_publicacion}")
        return None, None


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
        precio_nuevo_formateado = (
            "{:,.0f}".format(float(precio_nuevo.replace(",", "."))).replace(",", ".")
            if isinstance(precio_nuevo, str)
            else "No disponible"
        )
        precio_anterior_formateado = (
            "{:,.0f}".format(float(precio_anterior.replace(",", "."))).replace(",", ".")
            if isinstance(precio_anterior, str)
            else "No disponible"
        )
        if precio_anterior:
            html_content += f"""
            <div class="item">
                <div>{nombre_publicacion_link}</div>
                <div class="precio_actual">> {precio_nuevo_formateado}</div>
                <div class="precio_anterior">< {precio_anterior_formateado}</div>
            </div>
            """
        else:
            html_content += f"""
            <div class="item">
                <div>{nombre_publicacion_link}</div>
                <div class="precio_actual">> {precio_nuevo_formateado}</div>
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
