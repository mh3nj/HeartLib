import json
import time
from datetime import datetime, timedelta
import requests
from pywebpush import webpush, WebPushException

class DueDateNotifier:
    def __init__(self, crud, subscriptions_file='push_subscriptions.json'):
        self.crud = crud
        self.subscriptions_file = subscriptions_file
        self.vapid_private_key = "YOUR_PRIVATE_KEY"  # Generate once
        self.vapid_claims = {
            "sub": "mailto:library@heartlib.org"
        }
    
    def load_subscriptions(self):
        try:
            with open(self.subscriptions_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def check_and_notify(self):
        """Run daily: find loans due in 3 days or overdue, send notifications"""
        subscriptions = self.load_subscriptions()
        if not subscriptions:
            return
        
        now = datetime.now().timestamp()
        three_days_later = (datetime.now() + timedelta(days=3)).timestamp()
        
        # Get loans due in next 3 days (not yet overdue)
        conn = self.crud.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.*, p.name as patron_name, p.id as patron_id, b.title
            FROM loans l
            JOIN patrons p ON l.patron_id = p.id
            JOIN books b ON l.book_id = b.id
            WHERE l.return_time IS NULL
            AND l.due_time BETWEEN ? AND ?
        ''', (now, three_days_later))
        upcoming = cursor.fetchall()
        
        # Get overdue loans
        cursor.execute('''
            SELECT l.*, p.name as patron_name, p.id as patron_id, b.title
            FROM loans l
            JOIN patrons p ON l.patron_id = p.id
            JOIN books b ON l.book_id = b.id
            WHERE l.return_time IS NULL AND l.due_time < ?
        ''', (now,))
        overdue = cursor.fetchall()
        
        for sub in subscriptions:
            endpoint = sub.get('endpoint')
            if not endpoint:
                continue
            # For simplicity, send aggregated message
            if upcoming:
                self.send_notification(sub, "📚 Books Due Soon", 
                                       f"You have {len(upcoming)} book(s) due in the next 3 days.")
            if overdue:
                self.send_notification(sub, "⚠️ Overdue Books", 
                                       f"You have {len(overdue)} overdue book(s). Please return them.")
    
    def send_notification(self, subscription, title, body):
        try:
            webpush(
                subscription_info=subscription,
                data=json.dumps({'title': title, 'body': body}),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims
            )
        except WebPushException as e:
            print(f"Push failed: {e}")
