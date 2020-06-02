import pytest
import string
import random
import os


@pytest.fixture
def file_content_generator():
    def generator(lenght=1024 * 1024):
        content = "".join(random.choice(string.ascii_letters) for i in range(lenght))
        return content.encode()

    return generator


@pytest.fixture
def filename_generator():
    def generator():
        return "".join(random.choice(string.ascii_letters) for i in range(25)) + ".txt"

    return generator


@pytest.fixture
def filename(filename_generator):
    return filename_generator()


@pytest.fixture
def file_content(file_content_generator):
    return file_content_generator()


@pytest.fixture
def file_generator(file_content, config, filename):
    def generator(name=None, content=file_content):
        if name is None:
            name = filename

        storage_dir = config.get("storage_dir", "/app/data")

        with open(os.path.join(storage_dir, name), "wb") as f:
            f.write(file_content)

        return name, file_content

    return generator


@pytest.fixture
def file(file_generator):
    return file_generator()


@pytest.fixture
def get_file_content(config):
    def generator(filename):
        storage_dir = config.get("storage_dir", "/app/data")
        with open(os.path.join(storage_dir, filename), "rb") as f:
            return f.read()

    return generator
