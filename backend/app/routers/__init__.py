"""
API路由
"""
from app.routers import auth, users, products, agents, orders, inventory, customers, performance

__all__ = ["auth", "users", "products", "agents", "orders", "inventory", "customers", "performance"]