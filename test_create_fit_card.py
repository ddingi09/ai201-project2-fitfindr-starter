#from tools import search_listings
from tools import suggest_outfit
#from utils.data_loader import get_example_wardrobe
#from utils.data_loader import get_empty_wardrobe
from tools import create_fit_card
from test_suggest_outfit import test_suggest_wardrobe_empty
from test_suggest_outfit import test_suggest_working

def test_fit_working():
    outfit = test_suggest_working()
    item = {"name" : "vintage graphic tee", "size" : None, "max_price" : 50}
    out = create_fit_card(outfit, item)
    print(out)
    assert len(out) > 0

def test_fit_outfit_empty():
    #results = search_listings("vintage graphic tee", size=None, max_price=50)
    item = {"name" : "vintage graphic tee", "size" : None, "max_price" : 50}
    out = create_fit_card("", item)
    print(out)
    #assert isInstance(out, str)
    assert len(out) > 0
print("Working:")
test_fit_working()
print("\nNot Working:\n")
test_fit_outfit_empty()