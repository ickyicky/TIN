import os


def test_get_dir(client, folder_generator):
    client.authorize()
    name = folder_generator()
    result = client.get(f"dir/{name}")
    assert result.status_code == 200
    assert result.json() == []


def test_get_dir_info(client, folder_generator, folder_name, file_generator, filename):
    client.authorize()
    name = folder_generator()
    file_generator(os.path.join(name, filename))
    folder_generator(os.path.join(name, folder_name))

    result = client.get(f"dir/{name}?info=True")
    assert result.status_code == 200

    data = result.json()
    mapped = {f["name"]: f["type"] for f in data}

    assert mapped[filename] == "file"
    assert mapped[folder_name] == "directory"


def test_create_dir_recursively(client, folder_name):
    path = "/".join(folder_name for i in range(4))
    sub_path = "/".join(folder_name for i in range(3))

    client.authorize()

    result = client.post(f"dir/{path}")
    assert result.status_code == 200
    result = client.get(f"dir/{sub_path}")
    assert result.status_code == 200
    assert result.json() == [folder_name]


def test_delete_dir(client, folder_generator):
    folder_name = folder_generator()
    client.authorize()

    result = client.delete(f"dir/{folder_name}")
    assert result.status_code == 200

    result = client.get(f"dir/{folder_name}")
    assert result.status_code == 404


def test_remove_dir_recursively(client, folder_name):
    path = "/".join(folder_name for i in range(4))
    client.authorize()
    result = client.post(f"dir/{path}")
    assert result.status_code == 200

    result = client.delete(f"dir/{folder_name}")
    assert result.status_code == 400

    result = client.delete(f"dir/{folder_name}?recursive=True")
    assert result.status_code == 200

    result = client.get(f"dir/{path}")
    assert result.status_code == 404
