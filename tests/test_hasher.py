from src.dedupe.hasher import normalize, fuzzy_signature

def test_normalize_order_and_case():
    e = {"user_id":"U_1","device_id":"D_1","ip":"1.2.3.4","campaign_id":"CMP","amount":9.99}
    s1 = normalize(e)
    e2 = {"device_id":"d_1","user_id":"u_1","ip":"1.2.3.4","campaign_id":"cmp","amount":9.99}
    s2 = normalize(e2)
    assert s1 == s2

def test_signature_changes_when_field_changes():
    e = {"user_id":"u","device_id":"d","ip":"1.2.3.4","campaign_id":"c","amount":1.0}
    h1 = fuzzy_signature(e)
    e["amount"] = 2.0
    h2 = fuzzy_signature(e)
    assert h1 != h2
