from flask import Flask, request, jsonify
from utils import read_news, read_news_of_on_news_agency
from flask_cors import CORS
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/get_news/')
def get_news():
    _from = request.args.get('from') or 0
    _limit = request.args.get('limit') or 10
    return jsonify(read_news(_from, _limit))


@app.route('/get_news_of_news_agency/<news_agency_name>')
def get_news_of_certain_news_agency(news_agency_name):
    _from = request.args.get('from') or 0
    _limit = request.args.get('limit') or 10
    return jsonify(read_news_of_on_news_agency(news_agency_name, _from, _limit))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
