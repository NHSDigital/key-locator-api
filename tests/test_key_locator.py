import pytest
import requests
from api_test_utils.apigee_api_apps import ApigeeApiDeveloperApps

import conftest


@pytest.mark.asyncio
async def test_jwks_endpoint_valid_request(service_root_url, test_app_valid_config: ApigeeApiDeveloperApps):
    client_id = test_app_valid_config.client_id
    response = requests.get(f"{service_root_url}/jwks?clientId={client_id}")
    assert response.status_code == 200
    assert ("keys" in response.json())


@pytest.mark.asyncio
async def test_jku_endpoint_valid_request(service_root_url, test_app_valid_config: ApigeeApiDeveloperApps):
    client_id = test_app_valid_config.client_id
    response = requests.get(f"{service_root_url}/jku?clientId={client_id}")
    assert response.status_code == 200
    assert (response.text == conftest.JWKS_URL)


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["jku", "jwks"])
async def test_no_client_id(service_root_url, endpoint):
    response = requests.get(f"{service_root_url}/{endpoint}")
    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["jku", "jwks"])
async def test_empty_client_id(service_root_url, endpoint):
    response = requests.get(f"{service_root_url}/{endpoint}?clientId=")
    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["jku", "jwks"])
async def test_invalid_client_id(service_root_url, endpoint):
    response = requests.get(f"{service_root_url}/{endpoint}?clientId=notAValidClientId")
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["jku", "jwks"])
async def test_no_jwks_url_for_app(
        service_root_url,
        endpoint,
        test_app_no_jwks_url: ApigeeApiDeveloperApps
):
    client_id = test_app_no_jwks_url.client_id
    response = requests.get(f"{service_root_url}/{endpoint}?clientId={client_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["jku", "jwks"])
async def test_no_product_subscriptions(
        service_root_url,
        endpoint,
        test_app_no_product_subscriptions: ApigeeApiDeveloperApps
):
    client_id = test_app_no_product_subscriptions.client_id
    response = requests.get(f"{service_root_url}/{endpoint}?clientId={client_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["jku", "jwks"])
async def test_app_not_for_this_environment(
        service_root_url,
        endpoint,
        test_app_other_environment: ApigeeApiDeveloperApps
):
    client_id = test_app_other_environment.client_id
    response = requests.get(f"{service_root_url}/{endpoint}?clientId={client_id}")
    assert response.status_code == 404
