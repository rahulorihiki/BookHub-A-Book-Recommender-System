from flask import Flask, jsonify, request
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 
# Only allow a specific origin
# CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:5000"}})


# Load your books data from JSON file once at the start
with open('books.json', 'r') as file:
    books = json.load(file) 

@app.route('/api/books', methods=['GET'])
def get_books():
    # Retrieve query parameter for search, if provided
    query = request.args.get('search', '')  # Default is empty string if not provided
    if query:
        # Filter books based on query
        filtered_books = [book for book in books if query.lower() in book.lower()]
        return jsonify(filtered_books[:5])
    else:
        # Return all books if no query is provided
        return jsonify(books)

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=7000)