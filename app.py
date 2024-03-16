import requests
from bs4 import BeautifulSoup
import time

# import ctypes
# from win10toast import ToastNotifier

color_reset = "\033[0m"
color_rojo = "\033[91m"
color_naranja = "\033[38;5;208m"
color_azul = "\033[94m"
color_celeste = "\033[96m"
color_amarillo = "\033[93m"
color_verde = "\033[92m"


# ctypes.windll.kernel32.SetConsoleTitleW("shop-publications")


# def parpadear_vetana():
#    try:
#        ctypes.windll.user32.FlashWindow(
#            ctypes.windll.kernel32.GetConsoleWindow(), True
#        )
#    except ImportError:
#        pass


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
        <title>Resultados de Precios</title>
        <style>
            body { font-family: Arial, sans-serif; }
            .item { margin-bottom: 20px; }
            .nombre { font-weight: bold; }
            .precio { color: green; }
        </style>
    </head>
    <body>
    """

    for index, resultado in enumerate(resultados, start=1):
        nombre_publicacion, precio_nuevo = resultado
        html_content += f"""
        <div class="item">
            <div class="nombre">Índice: {index} - {nombre_publicacion}</div>
            <div class="precio">Precio: {precio_nuevo}</div>
        </div>
        """

    html_content += """
    </body>
    </html>
    """

    return html_content


# def mostrar_notificacion(nombre, precio_nuevo, precio_anterior):
#    parpadear_vetana()
#    toaster = ToastNotifier()
#    toaster.show_toast(
#        nombre,
#        f"Precio nuevo: {precio_nuevo}\nPrecio anterior: {precio_anterior}",
#        duration=10,
#    )


# def simular_variacion_de_precio():
#    mostrar_notificacion("Producto de prueba", "$10.000", "$20.000")


def main():
    enlaces = [
        {
            "link": "https://www.mercadolibre.com.ar/gamepad-redragon-harrow-pro-wireless-g808pro-joystick-pc-ps3-color-negro/p/MLA27921678#polycard_client=bookmarks&wid=MLA1600354692&sid=bookmarks",
        },
        {
            "link": "https://moto.mercadolibre.com.ar/MLA-1626743114-zanella-ceccato-r150-cafe-racer-motozuni-_JM#polycard_client=bookmarks",
        },
        {
            "link": "https://www.mercadolibre.com.ar/casco-moto-ls2-integral-320-evo-negro-mate-doble-visor-tamano-del-casco-xl/p/MLA24045739#polycard_client=bookmarks&wid=MLA1437224074&sid=bookmarks",
        },
        {
            "link": "https://articulo.mercadolibre.com.ar/MLA-1395820361-campera-ls2-alba-hombre-mesh-verano-ventilada-moto-delta-_JM#polycard_client=bookmarks",
        },
        {
            "link": "https://articulo.mercadolibre.com.ar/MLA-1275154314-jardinero-de-jeans-hombre-con-roturas-_JM#polycard_client=bookmarks",
        },
        {
            "link": "https://www.mercadolibre.com.ar/montblanc-legend-edt-100ml-para-hombre/p/MLA5225009#polycard_client=bookmarks&wid=MLA1288452290&sid=bookmarks",
        },
        {
            "link": "https://www.mercadolibre.com.ar/set-armani-acqua-di-gio-edt-100-ml-deo-after-shave/p/MLA29269071#polycard_client=bookmarks&wid=MLA1675592798&sid=bookmarks",
        },
        # {
        #   "link": "",
        # },
    ]

    precios_guardados = {}

    #while True:
    resultados = []
    for enlace_info in enlaces:
        link = enlace_info["link"]
        resultado_obtencion = obtener_nombre_y_precio(link)

        if resultado_obtencion:
            nombre_publicacion, precio_nuevo = resultado_obtencion
            nombre_publicacion = nombre_publicacion[:32] + "..."
            if link not in precios_guardados:
                print(color_amarillo + f"• {nombre_publicacion}" + color_reset)
                print(color_celeste + f"   Precio: {precio_nuevo}" + color_reset)
                # print(f"     ")
                precios_guardados[link] = precio_nuevo
            elif precio_nuevo != precios_guardados[link]:
                print(color_amarillo + f"• {nombre_publicacion}")
                print(
                    color_azul
                    + f"  -Precio anterior: {precios_guardados[link]}"
                    + color_reset
                )
                print(
                    color_naranja
                    + f"  +Precio nuevo:    {precio_nuevo}"
                    + color_reset
                )
                print(f"-------------------------")
                # mostrar_notificacion(
                #    nombre_publicacion, precios_guardados[link], precio_nuevo
                # )
                precios_guardados[link] = precio_nuevo

    html_content = generar_html(resultados)
    with open("index.html", "w", encoding="utf-8") as html_file:
        html_file.write(html_content)

    #time.sleep(60 * 60)


if __name__ == "__main__":
    # simular_variacion_de_precio()
    main()
