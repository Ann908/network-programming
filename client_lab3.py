import json
import requests
from requests.auth import HTTPBasicAuth

Base_url = 'http://127.0.0.1:5000'

def input_prod():
    return {
        'cost': int(input('Cost: ')),
        'weight': int(input('Weight: ')),
        'color': input('Color: ').strip()
    }

def print_response(response):
    print(f'HTTP {response.status_code}')
    try:
        print(response.json())
    except ValueError:
        print(response.text)

def main():
    with requests.Session() as session:
        session.auth = HTTPBasicAuth('Nick', 'python')

        while True:
            print('\n1 - See all the products')
            print('2 - Find the product using ID')
            print('3 - Add product')
            print('4 - Update product')
            print('5 - Delete product')
            print('0 - Exit')
            choice = input('Input number of action: ').strip()

            if choice == '0':
                break

            try:
                if choice == '1':
                    response = session.get(f'{Base_url}/items', timeout=10)
                elif choice == '2':
                    product_id = int(input('ID of product: '))
                    response = session.get(f'{Base_url}/items/{product_id}', timeout=10)
                elif choice == '3':
                    response = session.post(f'{Base_url}/items', json=input_prod(), timeout=10)
                elif choice == '4':
                    product_id = int(input('ID product: '))
                    response = session.put(f'{Base_url}/items/{product_id}', json=input_prod(), timeout=10)
                elif choice == '5':
                    product_id = int(input('ID of product: '))
                    response = session.delete(f'{Base_url}/items/{product_id}', json=input_prod(), timeout=10)
                else:
                    print('Unknown command')
                    continue

                print_response(response)
            except ValueError:
                print('Cost, weight and ID must be integers')
            except requests.RequestException as error:
                print(f'Error HTTP-request: {error}')

if __name__ == '__main__':
    main()