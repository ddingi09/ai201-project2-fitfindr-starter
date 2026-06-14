from agent import _parse_query

# Test parsing
test_cases = [
    "looking for a vintage graphic tee under $30",
    "vintage graphic tee under $30, size M",
    "designer ballgown size XXS under $5",
    "blue jeans, $50 max, large",
    "floral dress under $40 size small",
]

for query in test_cases:
    parsed = _parse_query(query)
    print(f"Query: {query}")
    print(f"  → description: {parsed['description']}")
    print(f"  → size: {parsed['size']}")
    print(f"  → max_price: {parsed['max_price']}")
    print()
