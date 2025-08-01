import requests
import json
import time
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Ваш ключ от Coinmarketcap (получите бесплатно на pro.coinmarketcap.com)
CMC_API_KEY = "04530b24-633d-48d4-8c4c-75739deaf5d4"

# Список отслеживаемых криптовалют
CRYPTOS = [
    'BTC', 'ETH', 'BNB', 'APT', 'SUI', 'DYDX', '1INCH',
    'OP', 'ARB', 'APE', 'LDO', 'SEI', 'STRK', 'OLAS'
]

def get_price(currency):
    """Получаем цену: сначала Binance, потом Coinmarketcap"""
    # Пробуем Binance
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={currency}USDT"
        response = requests.get(url)
        if response.status_code == 200:
            return {
                'price': float(response.json()['price']),
                'source': 'Binance'
            }
    except:
        pass
    
    # Если нет на Binance, пробуем Coinmarketcap
    try:
        url = "https://pro-api.coinmarketcap.com/v4/dex/spot-pairs/latest"
        headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
        params = {'symbol': f"{currency}/USDT", 'limit': 1}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                return {
                    'price': float(data['data'][0]['price']),
                    'source': 'Coinmarketcap'
                }
    except:
        pass
    
    return {'price': None, 'source': 'Не найдено'}

def update_prices():
    """Обновляем все цены"""
    print(f"{time.ctime()} - Обновление цен...")
    app.current_prices = {currency: get_price(currency) for currency in CRYPTOS}

# Настраиваем автообновление
scheduler = BackgroundScheduler()
scheduler.add_job(update_prices, 'interval', minutes=2)
scheduler.start()

# Главная страница
@app.route('/')
def dashboard():
    return render_template('index.html', prices=app.current_prices)

if __name__ == '__main__':
    app.current_prices = {}
    update_prices()  # Первое обновление
    app.run(host='0.0.0.0', port=5000)
