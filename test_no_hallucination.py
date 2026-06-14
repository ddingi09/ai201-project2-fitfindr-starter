from tools import create_fit_card

# Test 1: Item with no price, no platform, no outfit
print("Test 1 - Minimal info:")
item1 = {"name": "vintage graphic tee"}
caption1 = create_fit_card("", item1)
print(f"Caption: {caption1}")
print(f"Contains 'Depop' or specific platform: {'depop' in caption1.lower() or 'thrift' in caption1.lower()}")
print()

# Test 2: Item with price but no platform
print("Test 2 - With price, no platform:")
item2 = {"name": "vintage graphic tee", "price": 12.50, "title": "Retro Band Tee"}
caption2 = create_fit_card("", item2)
print(f"Caption: {caption2}")
print(f"Contains '$': {'$' in caption2}")
print(f"Contains specific platform: {'depop' in caption2.lower()}")
print()

# Test 3: Item with platform and price
print("Test 3 - With platform and price:")
item3 = {"name": "vintage graphic tee", "price": 15.00, "platform": "Depop", "title": "Rock Band Tee"}
caption3 = create_fit_card("", item3)
print(f"Caption: {caption3}")
print(f"Contains 'Depop': {'Depop' in caption3}")
print(f"Contains price: {'$' in caption3 or '15' in caption3}")
