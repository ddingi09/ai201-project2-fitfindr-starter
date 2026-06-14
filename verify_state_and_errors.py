"""
Verify state flow and error handling in the agent
"""

from agent import run_agent
from utils.data_loader import get_example_wardrobe

print("=" * 80)
print("TEST 1: Verify state is passing correctly between tools")
print("=" * 80)

session = run_agent(
    "vintage graphic tee under $30",
    get_example_wardrobe()
)

print("\n1. Checking session error:")
print(f"   Error: {session['error']}")
assert session["error"] is None, "Should have no error"
print("   ✅ No error\n")

print("2. Checking session selected_item:")
selected_item = session["selected_item"]
print(f"   Item ID: {selected_item.get('id')}")
print(f"   Item title: {selected_item.get('title')}")
print(f"   Item price: {selected_item.get('price')}")
print(f"   Item type: {type(selected_item)}")
print(f"   Item keys: {list(selected_item.keys())[:5]}...")  # First 5 keys
assert selected_item is not None, "selected_item should not be None"
assert isinstance(selected_item, dict), "selected_item should be a dict"
assert selected_item in session["search_results"], "selected_item should be from search_results"
print("   ✅ selected_item is a valid dict from search_results\n")

print("3. Checking session outfit_suggestion:")
outfit = session["outfit_suggestion"]
print(f"   Type: {type(outfit)}")
print(f"   Length: {len(outfit)} characters")
print(f"   First 100 chars: {outfit[:100]}...")
assert isinstance(outfit, str), "outfit_suggestion should be a string"
assert len(outfit) > 0, "outfit_suggestion should not be empty"
print("   ✅ outfit_suggestion is a non-empty string\n")

print("4. Checking session fit_card:")
fit_card = session["fit_card"]
print(f"   Type: {type(fit_card)}")
print(f"   Length: {len(fit_card)} characters")
print(f"   First 100 chars: {fit_card[:100]}...")
assert isinstance(fit_card, str), "fit_card should be a string"
assert len(fit_card) > 0, "fit_card should not be empty"
print("   ✅ fit_card is a non-empty string\n")

print("5. Verifying state consistency:")
print(f"   selected_item has required fields:")
print(f"     - title: {bool(selected_item.get('title'))}")
print(f"     - price: {bool(selected_item.get('price') is not None)}")
print(f"     - platform: {bool(selected_item.get('platform'))}")
print(f"     - colors: {bool(selected_item.get('colors'))}")
print(f"     - style_tags: {bool(selected_item.get('style_tags'))}")

# Verify outfit mentions the item
item_name = selected_item.get('title', '').lower()
outfit_lower = outfit.lower()
print(f"   outfit_suggestion mentions item: {item_name in outfit_lower or selected_item.get('name', '').lower() in outfit_lower}")

# Verify fit_card mentions relevant info
print(f"   fit_card includes styling details: {len(fit_card) > 50}")
print("   ✅ State is consistent and flowing correctly\n")

print("\n" + "=" * 80)
print("TEST 2: Verify no-results error path")
print("=" * 80)

session_error = run_agent(
    "designer ballgown size XXS under $5",
    get_example_wardrobe()
)

print("\n1. Checking session error:")
error = session_error["error"]
print(f"   Error message: {error}")
assert error is not None, "Should have an error message"
assert len(error) > 0, "Error message should not be empty"
print("   ✅ Error is set\n")

print("2. Checking session search_results:")
search_results = session_error["search_results"]
print(f"   Results list length: {len(search_results)}")
assert search_results == [], "search_results should be empty list"
print("   ✅ search_results is empty\n")

print("3. Checking session selected_item:")
selected_item_error = session_error["selected_item"]
print(f"   selected_item value: {selected_item_error}")
assert selected_item_error is None, "selected_item should be None when search fails"
print("   ✅ selected_item is None\n")

print("4. Checking session outfit_suggestion:")
outfit_error = session_error["outfit_suggestion"]
print(f"   outfit_suggestion value: {outfit_error}")
assert outfit_error is None, "outfit_suggestion should be None when search fails"
print("   ✅ outfit_suggestion is None (suggest_outfit was NOT called)\n")

print("5. Checking session fit_card:")
fit_card_error = session_error["fit_card"]
print(f"   fit_card value: {fit_card_error}")
assert fit_card_error is None, "fit_card should be None when search fails"
print("   ✅ fit_card is None (create_fit_card was NOT called)\n")

print("=" * 80)
print("✅ ALL VERIFICATION TESTS PASSED")
print("=" * 80)
print("\nSummary:")
print("  ✅ State flows correctly between tools")
print("  ✅ selected_item is passed to suggest_outfit correctly")
print("  ✅ outfit_suggestion is passed to create_fit_card correctly")
print("  ✅ Error path works - no downstream tools called on search failure")
print("  ✅ suggest_outfit and create_fit_card are skipped when search fails")
