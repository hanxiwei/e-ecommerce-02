from locust import HttpUser, task, between
import random

class EcommerceUser(HttpUser):
    wait_time = between(1, 2)
    
    @task(3)
    def search_products(self):
        """Simulate searching/getting products list"""
        self.client.get("/api/v1/products/")
        
    @task(1)
    def create_order(self):
        """Simulate creating an order"""
        user_id = random.randint(1, 1000)
        status = "pending"
        total = round(random.uniform(10.0, 500.0), 2)
        shipping_address = f"Address {random.randint(1, 1000)}"
        
        # In the current implementation, create_order expects query parameters
        self.client.post(f"/api/v1/orders/?user_id={user_id}&status={status}&total={total}&shipping_address={shipping_address}")
