import json
import pytest


def test_file_get(client, file_generator):
    client.authorize()
    name, content = file_generator()

    result = client.get(f"file/{name}")
    assert result.status_code == 200
    assert result.content == content
    assert int(result.headers["Content-Length"]) == len(content)


def test_file_get_not_existing(client, filename_generator, get_file_content):
    client.authorize()
    while True:
        filename = filename_generator()
        try:
            get_file_content(filename)
        except FileNotFoundError:
            break

    result = client.get(f"file/{filename}")
    assert result.status_code == 404


def test_file_get_range(client, file_generator):
    client.authorize()
    name, content = file_generator()

    downloaded_content = b""
    portion = 128 * 1024
    range_from = 0
    range_to = portion - 1

    while True:
        result = client.get(
            f"file/{name}", headers={"Range": f"bytes={range_from}-{range_to}"}
        )
        assert result.status_code == 206
        assert int(result.headers["Content-Length"]) == len(result.content)
        assert (
            result.headers["Content-Range"]
            == f"bytes {range_from}-{range_to}/{len(content)}"
        )
        assert content[range_from : range_to + 1] == result.content
        downloaded_content += result.content
        range_from = range_to + 1
        if range_from == len(content):
            break
        range_to = range_to + portion
        if range_to >= len(content):
            range_to = len(content) - 1

    assert content == downloaded_content


def test_file_get_invalid_range(client, file_generator):
    client.authorize()
    name, content = file_generator()

    range_from = 1024
    range_to = 1

    result = client.get(
        f"file/{name}", headers={"Range": f"bytes={range_from}-{range_to}"}
    )
    assert result.status_code == 400

    result = client.get(f"file/{name}", headers={"Range": "bytes=any-12"})
    assert result.status_code == 400


def test_file_post(client, file_content, filename, get_file_content):
    client.authorize()

    result = client.post(f"file/{filename}", file_content)
    assert result.status_code == 200

    assert get_file_content(filename) == file_content


def test_file_post_to_not_existing_folder(
    client, file_content, filename, get_file_content
):
    client.authorize()

    result = client.post(f"file/notexistingbyanychance/{filename}", file_content)
    assert result.status_code == 404


def test_file_post_to_invalid_folder(client, file_content, filename, get_file_content):
    client.authorize()

    result = client.post(f"file//{filename}", file_content)
    assert result.status_code == 400


@pytest.mark.parametrize(
    "scale_factor", [1, 0.5, 0.25, 2, 4],
)
def test_file_override(
    client, scale_factor, file_generator, file_content_generator, get_file_content
):
    client.authorize()
    name, content = file_generator()
    file_content = file_content_generator(int(len(content) * scale_factor))

    result = client.post(f"file/{name}", file_content)
    assert result.status_code == 200
    assert get_file_content(name) == file_content


@pytest.mark.parametrize(
    "file_size", [1024, 1024 * 1024,],  # 1Kb  # 1Mb
)
def test_file_post_range(
    client, file_size, file_content_generator, filename, get_file_content
):
    client.authorize()
    file_content = file_content_generator(file_size)

    portion = int(file_size / 10)
    range_from = 0
    range_to = portion - 1

    while True:
        result = client.post(
            f"file/{filename}",
            file_content[range_from : range_to + 1],
            headers={"Content-Range": f"bytes {range_from}-{range_to}/{file_size}"},
        )
        assert result.status_code == 200

        range_from = range_to + 1
        if range_from >= file_size:
            break

        range_to += portion
        if range_to >= file_size:
            range_to = file_size - 1

    assert get_file_content(filename) == file_content


@pytest.mark.parametrize(
    "range_,range_from,range_to,file_size",
    [
        ("bytes 1024-1/1040", 1, 1025, 1040),
        ("bytes 1-1024/1040", 1, 1000, 1040),
        ("bytes 0-1024/800", 1, 800, 800),
        ("bytes 0-511/800", 1, 560, 800),
    ],
)
def test_file_post_range_invalid_range(
    client, range_, range_from, range_to, file_size, file_content_generator, filename
):
    client.authorize()
    file_content = file_content_generator(file_size)

    result = client.post(
        f"file/{filename}",
        file_content[range_from:range_to],
        headers={"Content-Range": range_},
    )
    assert result.status_code == 400


def test_file_delete(client, file_generator, get_file_content):
    client.authorize()
    name, content = file_generator()

    result = client.delete(f"file/{name}")
    assert result.status_code == 200

    result = client.get(f"file/{name}")
    assert result.status_code == 404

    try:
        get_file_content(name)
        raise AssertionError()
    except FileNotFoundError:
        pass


def test_file_delete_not_existing(client, filename_generator, get_file_content):
    client.authorize()
    while True:
        filename = filename_generator()
        try:
            get_file_content(filename)
        except FileNotFoundError:
            break

    result = client.delete(f"file/{filename}")
    assert result.status_code == 404


def test_file_delete_invalid_request(client, folder_generator):
    client.authorize()
    name = folder_generator()

    result = client.delete(f"file/{name}")
    assert result.status_code == 400
