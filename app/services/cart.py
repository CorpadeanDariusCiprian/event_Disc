from flask import session

CART_SESSION_KEY = "cart_items"

def add_to_cart(event):
    cart = session.get(CART_SESSION_KEY, [])
    cart.append(event)
    session[CART_SESSION_KEY] = cart
    session.modified = True

def get_cart():
    return session.get(CART_SESSION_KEY, [])

def clear_cart():
    session.pop(CART_SESSION_KEY, None)
    session.modified = True