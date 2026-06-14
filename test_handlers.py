from app import InteractionState, handle_search, handle_get_outfit, handle_get_caption
from utils.data_loader import get_example_wardrobe

# Test that handlers return the correct number of values
state = InteractionState()

print("Testing search handler...")
result = handle_search("vintage graphic tee under $30", "Example wardrobe", state)
print(f"  Returns {len(result)} values: {[type(r).__name__ for r in result]}")
assert len(result) == 6, f"Expected 6 values, got {len(result)}"
print("  ✅ search handler returns correct format\n")

print("Testing outfit handler...")
result = handle_get_outfit(state)
print(f"  Returns {len(result)} values: {[type(r).__name__ for r in result]}")
assert len(result) == 7, f"Expected 7 values, got {len(result)}"
print("  ✅ outfit handler returns correct format\n")

print("Testing caption handler...")
result = handle_get_caption(state)
print(f"  Returns {len(result)} values: {[type(r).__name__ for r in result]}")
assert len(result) == 7, f"Expected 7 values, got {len(result)}"
print("  ✅ caption handler returns correct format\n")

print("✅ All handlers return correct number of values!")
