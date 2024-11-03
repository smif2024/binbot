import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
import json

class BinanceFees:
    def __init__(self):
        # Replace these with your actual API key and secret
        self.api_key = "mykey"
        self.api_secret = "mysecret"
        self.base_url = "https://api.binance.com"
        self.trading_pairs = ["BTCUSDT", "ETHBTC", "ETHUSDT"]

    def _generate_signature(self, params):
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def get_market_fees(self):
        try:
            endpoint = "/sapi/v1/asset/tradeFee"  # Updated endpoint
            timestamp = int(time.time() * 1000)
            params = {
                'timestamp': timestamp
            }
            
            # Generate signature
            signature = self._generate_signature(params)
            params['signature'] = signature

            # Prepare headers
            headers = {
                'X-MBX-APIKEY': self.api_key
            }

            # Make API request
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=headers
            )
            
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            print(f"Response Content: {response.text}")

            if response.status_code == 200:
                data = response.json()
                print("\nCurrent Trading Fees:")
                for pair in data:
                    if pair['symbol'] in self.trading_pairs:
                        print(f"\n{pair['symbol']}:")
                        maker_fee = float(pair['makerCommission']) * 100.0
                        taker_fee = float(pair['takerCommission']) * 100.0
                        print(f"Maker Fee: {maker_fee}%")
                        print(f"Taker Fee: {taker_fee}%")
            else:
                print(f"Error Response: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Response content: {response.text}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

def main():
    fees = BinanceFees()
    while True:
        print("\nFetching current trading fees...")
        fees.get_market_fees()
        print("\nWaiting 30 seconds before next update...")
        time.sleep(30)

if __name__ == "__main__":
    main()