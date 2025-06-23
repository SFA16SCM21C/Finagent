def test_advice_import():
    print("Running test_advice_import")
    try:
        from advisor import get_advice
        assert True
    except ImportError:
        assert False
        
def test_advice_content():
    from advisor import get_advice
    advice = get_advice()
    assert len(advice) > 0
    assert "financial plan" in advice.lower()