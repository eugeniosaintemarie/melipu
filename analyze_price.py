import requests
from bs4 import BeautifulSoup

url = 'https://www.mercadolibre.com.ar/consola-xbox-series-s-512gb-digital-blanco/p/MLA16650345?offer_type=BEST_PRICE'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

print('Analyzing MercadoLibre price structure...')

# Find all price elements
price_elements = soup.find_all('div', class_='ui-pdp-price__second-line')
print('Found', len(price_elements), 'price elements')

# Print all price elements with their text content
for i, elem in enumerate(price_elements):
    print(f'\nPrice element {i+1}:')
    print(elem.text.strip())
    
    # Look for the price fraction
    price_fraction = elem.find('span', class_='andes-money-amount__fraction')
    if price_fraction:
        print('Price fraction:', price_fraction.text.strip())

# Look for price subtitle elements that might contain '1 pago' text
subtitle_elements = soup.find_all('p', class_='ui-pdp-price__part ui-pdp-price__subtitle')
print('\nSubtitle elements:')
for elem in subtitle_elements:
    print(elem.text.strip())

# Look for all money amount elements
money_elements = soup.find_all('span', class_='andes-money-amount__fraction')
print('\nAll money amount elements:')
for i, elem in enumerate(money_elements):
    print(f'{i+1}. {elem.text.strip()}')
    
    # Try to find parent elements with price information
    parent = elem.find_parent('div', class_='ui-pdp-price')
    if parent:
        subtitle = parent.find('p', class_='ui-pdp-price__part ui-pdp-price__subtitle')
        if subtitle:
            print('   Subtitle:', subtitle.text.strip())

# Look for elements with '1 pago' text
pago_elements = soup.find_all(string=lambda text: text and '1 pago' in text.lower())
print('\nElements with "1 pago" text:')
for elem in pago_elements:
    print(elem.strip())
    parent = elem.parent
    print('Parent:', parent)
    
    # Try to find the closest price element
    price_container = parent.find_parent('div', class_='ui-pdp-price')
    if price_container:
        price = price_container.find('span', class_='andes-money-amount__fraction')
        if price:
            print('Associated price:', price.text.strip())

# Look for elements with 'cuotas' text (installments)
cuotas_elements = soup.find_all(string=lambda text: text and 'cuota' in text.lower())
print('\nElements with "cuotas" text:')
for elem in cuotas_elements:
    print(elem.strip())
    parent = elem.parent
    price_container = parent.find_parent('div', class_='ui-pdp-price')
    if price_container:
        price = price_container.find('span', class_='andes-money-amount__fraction')
        if price:
            print('Associated price:', price.text.strip())