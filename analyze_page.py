import requests
from bs4 import BeautifulSoup

url = 'https://moto.mercadolibre.com.ar/MLA-1468177137-honda-navi-110-scooters-0k-ahora-36912-arizona-motos-rc-_JM'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

print('Checking price elements...')
price_elements = soup.find_all('div', class_='ui-pdp-price__second-line')
print(f'Found {len(price_elements)} price elements')

for i, element in enumerate(price_elements):
    print(f'\nPrice element {i+1}:')
    print(element.prettify()[:500])

# Look for elements containing "1 pago"
payment_info = soup.find_all(string=lambda text: text and '1 pago' in text.lower())
print(f'\nFound {len(payment_info)} elements with "1 pago"')
for i, info in enumerate(payment_info):
    print(f'Payment info {i+1}: {info}')
    print(f'Parent: {info.parent.name}')
    # Try to find the closest price element
    closest_price = info.find_next('span', class_='andes-money-amount__fraction')
    if closest_price:
        print(f'Closest price: {closest_price.text}')

# Try to find all price elements
all_prices = soup.find_all('span', class_='andes-money-amount__fraction')
print(f'\nFound {len(all_prices)} price elements with class "andes-money-amount__fraction"')
for i, price in enumerate(all_prices):
    print(f'Price {i+1}: {price.text}')
    # Try to find payment info near this price
    payment_context = price.find_previous(string=lambda text: text and ('pago' in text.lower() or 'cuota' in text.lower()))
    if payment_context:
        print(f'  Context: {payment_context}')
