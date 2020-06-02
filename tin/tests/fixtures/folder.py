import pytest
import string
import random
import os


@pytest.fixture
def folder_name_generator():
    def generator():
        name = "".join(random.choice(string.ascii_letters) for i in range(30))
        return name

    return generator


@pytest.fixture
def folder_name(folder_name_generator):
    name = folder_name_generator()
    return name


@pytest.fixture
def folder_generator(config, folder_name):
    def generator(name=None):
        if name is None:
            name = folder_name
        storage_dir = config.get("storage_dir", "/app/data")
        dir_path = os.path.join(storage_dir, name)
        os.mkdir(dir_path)
        return name

    return generator
