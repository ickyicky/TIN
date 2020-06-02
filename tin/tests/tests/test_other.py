def test_exception(client):
    result = client.post("produce-exception")
    assert result.status_code == 500
