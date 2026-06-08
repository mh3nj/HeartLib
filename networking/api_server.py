# heartlib/networking/api_server.py
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import threading
import json
import os
from datetime import datetime

class HeartLibAPI:
    def __init__(self, crud, host='0.0.0.0', port=8766):
        self.crud = crud
        self.host = host
        self.port = port
        self.app = Flask(__name__, static_folder='../pwa', template_folder='../pwa')
        CORS(self.app)
        self.setup_routes()
    
    def setup_routes(self):
        # Serve PWA HTML
        @self.app.route('/')
        def index():
            return send_from_directory('../pwa', 'index.html')
        
        @self.app.route('/manifest.json')
        def manifest():
            return send_from_directory('../pwa', 'manifest.json')
        
        @self.app.route('/sw.js')
        def service_worker():
            return send_from_directory('../pwa', 'sw.js')
        
        # API endpoints
        @self.app.route('/api/books', methods=['GET'])
        def get_books():
            books = self.crud.get_all_books()
            return jsonify(books)
        
        @self.app.route('/api/search', methods=['GET'])
        def search():
            query = request.args.get('q', '')
            books = self.crud.search_books(query)
            return jsonify(books)
        
        @self.app.route('/api/books/<book_id>', methods=['GET'])
        def get_book(book_id):
            book = self.crud.get_book_by_id(book_id)
            return jsonify(book) if book else ('Not found', 404)
        
        @self.app.route('/api/patrons/<barcode>', methods=['GET'])
        def get_patron(barcode):
            patron = self.crud.get_patron_by_barcode(barcode)
            return jsonify(patron) if patron else ('Not found', 404)
        
        @self.app.route('/api/patron/<patron_id>/loans', methods=['GET'])
        def get_patron_loans(patron_id):
            loans = self.crud.get_active_loans_for_patron(patron_id)
            return jsonify(loans)
        
        @self.app.route('/api/checkout', methods=['POST'])
        def checkout():
            data = request.json
            success = self.crud.checkout_book(
                data['book_id'], 
                data['patron_id'], 
                data.get('due_days', 14)
            )
            return jsonify({'success': success})
        
        @self.app.route('/api/return', methods=['POST'])
        def return_book():
            data = request.json
            success = self.crud.return_book(data['loan_id'])
            return jsonify({'success': success})
        
        @self.app.route('/api/renew', methods=['POST'])
        def renew():
            data = request.json
            # Extend due date by 14 days
            success = self.crud.renew_loan(data['loan_id'], data.get('extra_days', 14))
            return jsonify({'success': success})
        
        @self.app.route('/api/hold', methods=['POST'])
        def place_hold():
            data = request.json
            # For now, just add to a holds table (to be implemented)
            return jsonify({'success': True})
        
        @self.app.route('/api/stats', methods=['GET'])
        def stats():
            stats = self.crud.get_stats()
            return jsonify(stats)
        
        @self.app.route('/api/verify_staff_pin', methods=['POST'])
        def verify_pin():
            data = request.json
            # Simple PIN check (change in settings)
            correct_pin = self.crud.get_setting('staff_pin', '1234')
            return jsonify({'valid': data['pin'] == correct_pin})
    
    def start(self):
        """Start the API server"""
        self.app.run(host=self.host, port=self.port, debug=False, threaded=True)
    
    def start_background(self):
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        print(f"🌐 HeartLib PWA available at http://{self.host}:{self.port}")

    # Store subscriptions in a simple file (or database)
    SUBSCRIPTIONS_FILE = 'push_subscriptions.json'

    def save_subscription(subscription):
        try:
            with open(SUBSCRIPTIONS_FILE, 'r') as f:
                subs = json.load(f)
        except:
            subs = []
        subs.append(subscription)
        with open(SUBSCRIPTIONS_FILE, 'w') as f:
            json.dump(subs, f)

    @app.route('/api/subscribe', methods=['POST'])
    def subscribe():
        subscription = request.json
        save_subscription(subscription)
        return jsonify({'status': 'ok'})