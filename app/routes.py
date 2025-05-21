import os
from dotenv import load_dotenv
from flask import Blueprint, render_template, request, redirect, url_for
from urllib.parse import urlencode

from app.db import save_transaction
from app.services import ticketmaster_api, cart, eventbrite_scraper
import stripe
from flask import jsonify, request

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

main = Blueprint('main', __name__)

@main.route("/", methods=["POST"])
def index():
    # Extract input from POST form data (or JSON if you want)
    category = request.form.get("category", "")
    date = request.form.get("date", "")
    address = request.form.get("address", "")
    keyword = request.form.get("keyword", "")

    # Process inputs immediately (call search functions)
    events_ticketmaster = ticketmaster_api.search_events(keyword, category, date, address, limit=5)
    events_eventbrite = eventbrite_scraper.search_events(keyword, category, date, address, limit=5)

    # Return results directly, render template with data
    return render_template(
        "results.html",
        events_ticketmaster=events_ticketmaster,
        events_eventbrite=events_eventbrite,
        keyword=keyword,
        stripe_public_key=os.getenv("STRIPE_PUBLIC_KEY")
    )


@main.route("/results", methods=["GET"])
def results():
    keyword = request.args.get("keyword", "")
    category = request.args.get("category", "")
    date = request.args.get("date", "")
    address = request.args.get("address", "")

    events_ticketmaster = []
    events_eventbrite = []

    if keyword:
        events_ticketmaster = ticketmaster_api.search_events(keyword, category, date, address, limit=5)
        events_eventbrite = eventbrite_scraper.search_events(keyword, category, date, address, limit=5)

    return render_template(
        "results.html",
        events_ticketmaster=events_ticketmaster,
        events_eventbrite=events_eventbrite,
        keyword=keyword,
        stripe_public_key=os.getenv("STRIPE_PUBLIC_KEY")
    )

@main.route("/add_to_cart", methods=["POST"])
def add_to_cart_route():
    event = {
        "name": request.form.get("name"),
        "date": request.form.get("date"),
        "time": request.form.get("time"),
        "venue": request.form.get("venue"),
        "url": request.form.get("url")
    }
    cart.add_to_cart(event)
    return redirect(url_for("main.cart_view"))

@main.route("/cart", methods=["GET"])
def cart_view():
    items = cart.get_cart()
    return render_template("cart.html", cart_items=items)

@main.route("/clear_cart", methods=["GET"])
def clear_cart_route():
    cart.clear_cart()
    return redirect(url_for("main.cart_view"))

@main.route("/create_checkout_session", methods=["POST"])
def create_checkout_session():
    data = request.get_json()
    line_items = []

    for item in data.get("items", []):
        line_items.append({
            "price_data": {
                "currency": "usd",
                "unit_amount": int(item["price"] * 100),  # Stripe expects amount in cents
                "product_data": {
                    "name": item["name"]
                },
            },
            "quantity": item["quantity"],
        })

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=url_for("main.index", _external=True) + "?success=true",
            cancel_url=url_for("main.index", _external=True) + "?canceled=true"
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/payment_success")
def payment_success():
    session_id = request.args.get("session_id")
    if not session_id:
        return "Session ID missing", 400

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            # Example: get user IP from request
            user_ip = request.remote_addr or "unknown"

            # Get the search parameters and cart from session or somewhere you store them (adjust as needed)
            # For example, maybe from query parameters or cookies (this depends on your app's logic)
            search_params = {
                "keyword": request.args.get("keyword"),
                "category": request.args.get("category"),
                "date": request.args.get("date"),
                "address": request.args.get("address")
            }
            # Assuming you pass cart items in the URL or session, replace this as per your app logic
            cart_items = []  # Replace with actual cart data retrieval

            # Save transaction to TinyDB
            save_transaction(session_id, user_ip, search_params, cart_items, session.payment_status)

            return render_template("thank_you.html")
        else:
            return redirect(url_for("main.payment_cancel"))
    except Exception as e:
        return f"Failed to verify payment: {str(e)}", 500

@main.route("/payment_cancel")
def payment_cancel():
    return render_template("payment_failed.html")

@main.route("/dummy_payment_success")
def dummy_payment_success():
    # Simulated data
    session_id = "dummy_session_123"
    user_ip = request.remote_addr or "127.0.0.1"
    search_params = {"keyword": "Coldplay", "category": "music", "date": "2025-05-21", "address": "NYC"}
    cart_items = [
        {"name": "Coldplay Ticket", "price": 100.00, "quantity": 2}
    ]
    payment_status = "paid"

    save_transaction(session_id, user_ip, search_params, cart_items, payment_status)
    return render_template("thank_you.html")

