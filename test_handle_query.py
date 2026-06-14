from app import handle_query

# Test 1: Empty query
print("Test 1 - Empty query:")
result = handle_query("", "Example wardrobe")
print(f"Result: {result[0]}\n")

# Test 2: Valid query with example wardrobe
print("Test 2 - Valid query with example wardrobe:")
result = handle_query("vintage graphic tee under $30", "Example wardrobe")
print(f"Listing:\n{result[0][:100]}...\n")
print(f"Outfit suggestion provided: {len(result[1]) > 0}")
print(f"Fit card provided: {len(result[2]) > 0}\n")

# Test 3: Valid query with empty wardrobe
print("Test 3 - Valid query with empty wardrobe:")
result = handle_query("blue jeans under $40", "Empty wardrobe (new user)")
print(f"Listing:\n{result[0][:100]}...\n")
print(f"Outfit suggestion provided: {len(result[1]) > 0}")
print(f"Fit card provided: {len(result[2]) > 0}\n")

# Test 4: No-results query
print("Test 4 - No-results query:")
result = handle_query("designer ballgown size XXS under $5", "Example wardrobe")
print(f"Error message: {result[0]}\n")
print(f"Outfit suggestion empty: {len(result[1]) == 0}")
print(f"Fit card empty: {len(result[2]) == 0}")
