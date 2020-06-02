from multiprocessing.pool import ThreadPool


def test_concurrency_locking(client, filename):
    pool = ThreadPool(processes=10)
    client.authorize()

    def test_procedure():
        result = client.post(f"file/{filename}", b"a" * 1024)
        return result.status_code

    results = [pool.apply_async(test_procedure) for i in range(10)]
    collected = [r.get() for r in results]
    assert any((r == 423 for r in collected))


def test_concurrency_allowd(client, filename):
    pool = ThreadPool(processes=10)
    client.authorize()

    result = client.get(f"file/{filename}")
    status_code = result.status_code

    def test_procedure():
        result = client.get(f"file/{filename}")
        return result.status_code

    results = [pool.apply_async(test_procedure) for i in range(10)]
    collected = [r.get() for r in results]
    assert all((r == status_code for r in collected)), collected
