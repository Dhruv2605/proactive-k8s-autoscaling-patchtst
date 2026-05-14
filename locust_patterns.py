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

# --- LOAD PATTERNS ---
class ThesisLoadShape(LoadTestShape):
    """
    Runs FOREVER until you press Ctrl+C.
    """
    
    # OPTIONS: "sine_wave", "step_load", "spike_stress"
    CURRENT_PATTERN = "spike_stress" 

    def tick(self):
        run_time = self.get_run_time()
        
        # --- REMOVED TIME LIMIT CHECK HERE ---
        # The test will now run until you manually stop it.

        # PATTERN 1: SINE WAVE (Infinite Day/Night cycles)
        if self.CURRENT_PATTERN == "sine_wave":
            base = 200
            amplitude = 150
            period = 1800 # 30 mins
            # math.sin works for infinite run_time values
            users = base + amplitude * math.sin(2 * math.pi * run_time / period)
            return (round(users), 10)

        # PATTERN 2: SPIKE STRESS (Infinite Flash Sales)
        # Quiet for 8 mins, HUGE spike for 2 mins, repeat forever.
        elif self.CURRENT_PATTERN == "spike_stress":
            cycle_time = run_time % 600 # 5 min cycles (Modulo works forever)
            if cycle_time < 480: # First 3 mins normal
                return (50, 5)
            else: # Last 2 mins BOOM
                return (1000, 100)

        # PATTERN 3: STEP LOAD (Infinite Growth)
        # Adds 100 users every 10 minutes.
        elif self.CURRENT_PATTERN == "step_load":
            step = int(run_time / 600)
            users = 50 + (step * 100)
            
            # SAFETY CAP: Stop growing at 5000 users to prevent crash
            if users > 5000: 
                users = 5000
                
            return (users, 10)

        return (50, 5) # Default safety