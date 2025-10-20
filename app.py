#uvicorn main:app --reload

from fastapi import FastAPI
from models import Product, KnapsackRequest
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    name: str
    weight: float
    value: float

class KnapsackRequest(BaseModel):
    capacity: float
    items: List[Item]

@app.post("/api/optimize/{method}")
def optimize_knapsack(method: str, req: KnapsackRequest):
    items = req.items
    capacity = req.capacity

    # Just a mock for now — you can replace this with your optimizer logic
    profit = sum(i.value for i in items if i.weight <= capacity / 2)
    used_capacity = sum(i.weight for i in items if i.weight <= capacity / 2)

    return {
        "method": method,
        "capacity": capacity,
        "usedCapacity": used_capacity,
        "profit": profit,
        "items": [i.dict() for i in items],
    }

# Sample products (images can be URLs or local paths)
products = [
    Product(id=1, name="Laptop", weight=3, value=25000, image="/src/assets/images/macbook.png"),
    Product(id=2, name="PS5 Console", weight=1, value=12000, image="/src/assets/images/gaming.png"),
    Product(id=3, name="Headphones", weight=2, value=5000, image="/src/assets/images/headphone.png")
]

@app.get("/api/products", response_model=List[Product])
def get_products():
    return products

# -------------------- Knapsack Algorithms --------------------
def knapsack_dp(capacity, items):
    n = len(items)
    dp = [[0]*(int(capacity)+1) for _ in range(n+1)]

    for i in range(1, n+1):
        for w in range(int(capacity)+1):
            if items[i-1].weight <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w-int(items[i-1].weight)] + items[i-1].value)
            else:
                dp[i][w] = dp[i-1][w]

    # Backtracking to find selected items
    w = int(capacity)
    selected = []
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected.append(items[i-1])
            w -= int(items[i-1].weight)

    return dp[n][int(capacity)], selected

def knapsack_fractional(capacity, items):
    items_sorted = sorted(items, key=lambda x: x.value/x.weight, reverse=True)
    remaining = capacity
    total_value = 0
    selected = []

    for item in items_sorted:
        if item.weight <= remaining:
            selected.append(item)
            total_value += item.value
            remaining -= item.weight
        else:
            fraction = remaining / item.weight
            total_value += item.value * fraction
            selected.append(Product(
                id=item.id,
                name=item.name + " (Fractional)",
                weight=remaining,
                value=item.value * fraction,
                image=item.image
            ))
            break

    return total_value, selected

def knapsack_backtrack(capacity, items):
    n = len(items)
    best_value = 0
    best_combo = []

    def helper(i, current_weight, current_value, combo):
        nonlocal best_value, best_combo
        if current_weight > capacity:
            return
        if i == n:
            if current_value > best_value:
                best_value = current_value
                best_combo = combo[:]
            return
        # include item
        helper(i+1, current_weight+items[i].weight, current_value+items[i].value, combo+[items[i]])
        # exclude item
        helper(i+1, current_weight, current_value, combo)

    helper(0, 0, 0, [])
    return best_value, best_combo

# -------------------- API Endpoints --------------------
@app.post("/api/optimize/dp")
def optimize_dp(req: KnapsackRequest):
    profit, selected = knapsack_dp(req.capacity, products)
    return {
        "method": "dp",
        "profit": profit,
        "usedCapacity": sum([item.weight for item in selected]),
        "capacity": req.capacity,
        "items": selected
    }

@app.post("/api/optimize/fractional")
def optimize_fractional(req: KnapsackRequest):
    profit, selected = knapsack_fractional(req.capacity, products)
    return {
        "method": "fractional",
        "profit": profit,
        "usedCapacity": sum([item.weight for item in selected]),
        "capacity": req.capacity,
        "items": selected
    }

@app.post("/api/optimize/backtrack")
def optimize_backtrack(req: KnapsackRequest):
    profit, selected = knapsack_backtrack(req.capacity, products)
    return {
        "method": "backtrack",
        "profit": profit,
        "usedCapacity": sum([item.weight for item in selected]),
        "capacity": req.capacity,
        "items": selected
    }
