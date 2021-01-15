from flask import Flask, request, jsonify
from utils import read_news

app = Flask(__name__)


@app.route('/getnews/<news_agency_name>')
def get_news(news_agency_name):
    _from = request.args.get('from') or 0
    _limit = request.args.get('limit') or 10
    return jsonify(read_news(_from,_limit))