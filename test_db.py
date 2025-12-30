import database as db
import pandas as pd
import os

# Init DB
db.init_db()

# Test Add
db.add_product("Test Batch Product", "BATCH-001", "Test", 100, 50, "Desc")

# Test Get by SKU
prod = db.get_product_by_sku("BATCH-001")
assert prod is not None
print(f"Product found: {prod[1]} (SKU: {prod[2]})")

# Test Update
success = db.update_product(prod[0], "Updated Name", "BATCH-001", "Test", 200, 100, "New Desc")
assert success is True

# Verify Update
prod_updated = db.get_product_by_sku("BATCH-001")
assert prod_updated[1] == "Updated Name"
assert prod_updated[4] == 200.0
print("Update verified.")

# Test Export Logic Simulation
df = db.get_all_products()
print(f"Total products: {len(df)}")
# Clean up
db.delete_product(prod[0])
print("Test product deleted.")
