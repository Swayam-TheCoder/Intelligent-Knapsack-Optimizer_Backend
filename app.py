# uvicorn main:app --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

def knapsack_dp(capacity: float, items: List[Item]):
    n = len(items)
    dp = [[0] * (int(capacity) + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(int(capacity) + 1):
            if items[i - 1].weight <= w:
                dp[i][w] = max(
                    dp[i - 1][w],
                    dp[i - 1][w - int(items[i - 1].weight)] + items[i - 1].value,
                )
            else:
                dp[i][w] = dp[i - 1][w]

    # Backtracking to find selected items
    w = int(capacity)
    selected = []
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(items[i - 1])
            w -= int(items[i - 1].weight)

    selected.reverse()
    return dp[n][int(capacity)], selected


def knapsack_fractional(capacity: float, items: List[Item]):
    items_sorted = sorted(items, key=lambda x: x.value / x.weight, reverse=True)
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
            fractional_item = Item(
                name=item.name + " (Fractional)",
                weight=remaining,
                value=item.value * fraction,
            )
            selected.append(fractional_item)
            total_value += item.value * fraction
            break

    return total_value, selected

@app.post("/api/optimize/{method}")
def optimize(method: str, req: KnapsackRequest):

    if method.lower() == "dp":
        profit, selected = knapsack_dp(req.capacity, req.items)
    elif method.lower() == "fractional":
        profit, selected = knapsack_fractional(req.capacity, req.items)
    else:
        return {"error": "Invalid method. Use 'dp' or 'fractional'."}

    return {
        "method": method,
        "capacity": req.capacity,
        "usedCapacity": sum(item.weight for item in selected),
        "profit": profit,
        "items": [item.dict() for item in selected],
    }
