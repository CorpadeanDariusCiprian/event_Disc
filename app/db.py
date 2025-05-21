from tinydb import TinyDB, Query
from datetime import datetime


db = TinyDB('tinydb.json')  # This file will store your data


transactions_table = db.table('client_transactions')


def save_transaction(session_id, user_ip, search_params, cart_items, payment_status):
    """
    Save transaction data into TinyDB.
    """
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)

    transaction = {
        'session_id': session_id,
        'user_ip': user_ip,
        'search_params': search_params,
        'cart_items': cart_items,
        'total_amount': total_amount,
        'payment_status': payment_status,
        'purchase_datetime': datetime.utcnow().isoformat()
    }

    transactions_table.insert(transaction)