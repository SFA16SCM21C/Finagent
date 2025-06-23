# src/test_advisor.py
def test_advice_import():
    """Test that the advisor module can be imported."""
    try:
        from advisor import get_advice
        assert True
    except ImportError:
        assert False