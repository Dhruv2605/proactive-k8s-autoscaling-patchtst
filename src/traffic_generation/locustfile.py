from locust import HttpUser, task, between
import random

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)  # Simulate human think time

    @task(10)
    def index(self):
        self.client.get("/")

    @task(5)
    def view_product(self):
        # A few valid product IDs from Online Boutique
        products = ["0PUK6V6EV0", "1YMWWN1N4O", "2ZYFJ3GM2N", "66VCHSJNUP", "6E92ZMYYFZ"]
        item_id = random.choice(products)
        self.client.get(f"/product/{item_id}")

    @task(3)
    def view_cart(self):
        self.client.get("/cart")

    @task(1)
    def checkout(self):
        self.client.post("/cart/checkout", json={
            "email": "test@example.com",
            "street_address": "123 Test St",
            "zip_code": "94043",
            "city": "Mountain View",
            "state": "CA",
            "country": "United States",
            "credit_card_number": "4444444444444444",
            "credit_card_expiration_month": 1,
            "credit_card_expiration_year": 2026,
            "credit_card_cvv": 123
        })