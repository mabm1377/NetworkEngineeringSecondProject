from flask import Flask, request, jsonify
from utils import read_news, read_news_of_on_news_agency, search, visit_news
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


@app.route("/search")
def search_in_news():
    query = request.args.get("query")
    return jsonify(search(query))


@app.route("/visit/")
def visit():
    news_id = request.args.get("news_id")
    if news_id is None:
        return jsonify({"error": "news id is None"}), 400
    return visit_news(news_id)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
