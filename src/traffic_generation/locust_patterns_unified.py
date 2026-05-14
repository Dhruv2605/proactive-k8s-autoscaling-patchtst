import math
from locust import HttpUser, task, between, LoadTestShape

# --- USER BEHAVIOR ---
class WebsiteUser(HttpUser):
    wait_time = between(1, 5)
    
    @task(10)
    def index(self): self.client.get("/")
    @task(5)
    def view_item(self): self.client.get("/product/0PUK6V6EV0")
    @task(2)
    def add_cart(self): self.client.get("/cart")
    @task(1)
    def checkout(self): self.client.post("/cart/checkout", json={"email": "test@example.com"})

# --- UNIFIED LOAD PATTERN ---
class UnifiedThesisLoad(LoadTestShape):
    """
    Cycles through Sine, Spike, and Step patterns automatically.
    Total Cycle: 8 Hours (28,800 seconds)
    """

    def tick(self):
        run_time = self.get_run_time()
        cycle_time = run_time % 28800 # 8 Hour Cycles

        # 0-3h: SINE WAVE (Standard Day/Night)
        if cycle_time < 10800:
            base = 200
            amplitude = 150
            period = 1800 # 30 min oscillations
            users = base + amplitude * math.sin(2 * math.pi * run_time / period)
            return (round(users), 10)

        # 3-5h: SPIKE STRESS (Flash Sales)
        elif cycle_time < 18000:
            spike_cycle = run_time % 600 # 10 min spikes
            if spike_cycle < 480: # 8 min quiet
                return (50, 5)
            else: # 2 min BOOM
                return (1200, 100)

        # 5-7h: STEP LOAD (Steady Growth)
        elif cycle_time < 25200:
            step_run_time = cycle_time - 18000
            step = int(step_run_time / 600) # Add 100 users every 10 mins
            users = 100 + (step * 100)
            return (min(users, 3000), 10)

        # 7-8h: RANDOM BURSTS (Unpredictable)
        else:
            burst_cycle = run_time % 300 # 5 min mini-cycles
            if burst_cycle < 200:
                return (200, 10)
            else:
                return (1500, 150)

        return (50, 5)
