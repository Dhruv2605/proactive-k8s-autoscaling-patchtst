"""
Locust traffic generator for Weaveworks Sock Shop.
Simulates realistic e-commerce browsing: catalogue, cart, orders.
Uses the same sine_wave and spike_stress patterns as Online Boutique.
"""
from locust import HttpUser, task, between, LoadTestShape
import math, time, random

class SockShopUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def browse_catalogue(self):
        self.client.get("/catalogue", name="/catalogue")

    @task(3)
    def view_item(self):
        self.client.get("/catalogue/3395a43e-2d88-40de-b95f-e00e1502085b", name="/catalogue/item")

    @task(2)
    def view_cart(self):
        self.client.get("/cart", name="/cart")

    @task(1)
    def home_page(self):
        self.client.get("/", name="/")

    @task(1)
    def login(self):
        self.client.get("/login", name="/login")


class SineWaveShape(LoadTestShape):
    """Smooth sinusoidal traffic: 50-500 users, 10-min period."""
    min_users = 50
    max_users = 500
    period = 600  # seconds

    def tick(self):
        run_time = self.get_run_time()
        if run_time > 7200:  # 2 hours max
            return None
        amplitude = (self.max_users - self.min_users) / 2
        users = int(self.min_users + amplitude + amplitude * math.sin(2 * math.pi * run_time / self.period))
        return (users, max(10, users // 10))
