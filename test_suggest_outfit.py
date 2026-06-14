from tools import search_listings
from tools import suggest_outfit
from utils.data_loader import get_example_wardrobe
from utils.data_loader import get_empty_wardrobe

def test_suggest_working():
    #results = search_listings("vintage graphic tee", size=None, max_price=50)
    i = {"desc" : "vintage graphic tee", "size" : None, "max_price" : 50}
    out = suggest_outfit(i, get_example_wardrobe())
    return out
    #assert isInstance(out, str)
    assert len(out) > 0

def test_suggest_wardrobe_empty():
    #results = search_listings("vintage graphic tee", size=None, max_price=50)
    i = {"desc" : "vintage graphic tee", "size" : None, "max_price" : 50}
    out = suggest_outfit(i, get_empty_wardrobe())
    return out
    #assert isInstance(out, str)
    assert len(out) > 0

test_suggest_wardrobe_empty()
test_suggest_working()