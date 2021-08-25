from flask import Flask, jsonify
from cyb import get_cyb_market_data
# from gol import get_gol_market_data, GGOL_SUPPLY
from config import GCYB_SUPPLY


app = Flask(__name__)


@app.route('/coins/cyb', methods=['GET'])
def cyb_data():
    global MARKET_DATA
    try:
        print('in try')
        market_data = get_cyb_market_data()['market_data']
        MARKET_DATA = market_data
    except Exception:
        print('in exept')
        market_data = MARKET_DATA.copy()
    return jsonify({
        "name": "cyber",
        "symbol": "gcyb",
        "image": {
            "small": "https://cyber.page/blue-circle.a8fa89beb0.png"
        },
        "market_data": market_data,
        "supply": GCYB_SUPPLY
    })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
