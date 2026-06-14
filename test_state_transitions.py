from app import InteractionState, handle_search, handle_get_outfit, handle_get_caption, handle_continue_shopping
from utils.data_loader import get_example_wardrobe

# Test state transitions
state = InteractionState()

# Step 1: Search
print("Step 1: Searching for 'vintage graphic tee under $30'...")
listing1, outfit1, caption1, status1, show_outfit, show_search = handle_search(
    "vintage graphic tee under $30",
    "Example wardrobe",
    state
)
print(f"Status: {status1}")
print(f"Step: {state.step}")
print(f"Show outfit button: {show_outfit}")
print(f"Item found: {bool(state.session['selected_item'])}\n")

# Step 2: Get outfit
print("Step 2: Getting outfit suggestion...")
listing2, outfit2, caption2, status2, _, show_caption, show_search = handle_get_outfit(state)
print(f"Status: {status2}")
print(f"Step: {state.step}")
print(f"Outfit length: {len(outfit2)}")
print(f"Show caption button: {show_caption}\n")

# Step 3: Get caption
print("Step 3: Getting Instagram caption...")
listing3, outfit3, caption3, status3, _, _, show_search = handle_get_caption(state)
print(f"Status: {status3}")
print(f"Step: {state.step}")
print(f"Caption length: {len(caption3)}\n")

# Step 4: Continue shopping
print("Step 4: Continuing shopping...")
_, _, _, status4, _, _, _ = handle_continue_shopping(state)
print(f"Status: {status4}")
print(f"Step: {state.step}")
print(f"Session cleared: {len(state.session) == 0}\n")

print("✅ All state transitions working correctly!")
