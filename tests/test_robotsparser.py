import sys
import types

# Create a dummy protego module to avoid ImportError during import
sys.modules['protego'] = types.ModuleType('protego')
sys.modules['protego'].Protego = object

from robotsparser import robots_location


def test_robots_location():
    url = 'https://example.com/page'
    expected = 'https://example.com/robots.txt'
    assert robots_location(url) == expected
