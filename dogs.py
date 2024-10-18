import random

import pytest
import requests


class YaUploader:
    def __init__(self):
        # TODO: получение token по Client ID и Secret ID
        self.token = token

    def create_folder(self, path, token):
        url_create = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {token}'}
        response = requests.put(f'{url_create}?path={path}', headers = headers)

    def upload_photos_to_yd(self, token, path, url_file, name):
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {token}'}
        params = {"path": f'/{path}/{name}', 'url': url_file, "overwrite": "true"}
        resp = requests.post(url, headers=headers, params=params)


def get_sub_breeds(breed):
    res = requests.get(f'https://dog.ceo/api/breed/{breed}/list')
    return res.json().get('message', [])


def get_urls(breed, sub_breeds):
    url_images = []
    if sub_breeds:
        for sub_breed in sub_breeds:
            res = requests.get(f"https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random")
            sub_breed_urls = res.json().get('message')
            url_images.append(sub_breed_urls)
    else:
        url_images.append(requests.get(f"https://dog.ceo/api/breed/{breed}/images/random").json().get('message'))
    return url_images


def u(breed):
    sub_breeds = get_sub_breeds(breed)
    urls = get_urls(breed, sub_breeds)
    yandex_client = YaUploader()
    yandex_client.create_folder('test_folder', "AgAAAAAJtest_tokenxkUEdew")
    for url in urls:
        part_name = url.split('/')
        name = '_'.join([part_name[-2], part_name[-1]])
        yandex_client.upload_photos_to_yd("AgAAAAAJtest_tokenxkUEdew", "test_folder", url, name)


@pytest.mark.parametrize('breed', ['doberman', 'bulldog'])
def test_proverka_upload_dog(breed):
    u(breed)
    # проверка
    url_create = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth AgAAAAAJtest_tokenxkUEdew'}
    response = requests.get(f'{url_create}?path=/test_folder', headers=headers)
    import json
    if breed == 'doberman':
        file = 'doberman.json'
    elif breed == 'bulldog':
        file = 'bulldog.json'
    with open(file, 'r') as file:
        response = json.load(file)
    assert response.get('type') == "dir"
    assert response.get('name') == "test_folder"
    assert True
    items = response.get('_embedded').get('items')
    if get_sub_breeds(breed) == []:
        assert len(items) == 1
        for item in items:
            assert item.get('type') == 'file'
            assert item.get('name').startswith(breed)
    else:
        assert len(items) == len(get_sub_breeds(breed)), f"{items},{get_sub_breeds(breed)}"
        for item in items:
            assert item.get('type') == 'file'
            assert item.get('name').startswith(breed)
