import asyncio
import os

import pytest
import requests
from api_test_utils.apigee_api_apps import ApigeeApiDeveloperApps
from api_test_utils.apigee_api_products import ApigeeApiProducts

TEST_JWKS_URL = "https://raw.githubusercontent.com/NHSDigital/identity-service-jwks" \
    "/main/jwks/internal-dev/278af795-6884-42dd-a713-f2b03927abb5.json"
TEST_ENVIRONMENT = os.environ["APIGEE_ENVIRONMENT"]


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='module')
def apigee_root_url():
    return "https://api.service.nhs.uk" if TEST_ENVIRONMENT == "prod" \
        else f"https://{TEST_ENVIRONMENT}.api.service.nhs.uk"


@pytest.fixture(scope='module')
def apigee_organization():
    return "nhsd-prod" if TEST_ENVIRONMENT in ["int", "prod"] else "nhsd-nonprod"


@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def test_product(apigee_organization):
    api = ApigeeApiProducts(org_name=apigee_organization)
    await api.create_new_product()
    yield api
    await api.destroy_product()


@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def test_product_other_environment():
    api = ApigeeApiProducts(org_name="nhsd-nonprod")
    await api.create_new_product()
    yield api
    await api.destroy_product()


@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def test_app(apigee_organization, test_product):
    api = ApigeeApiDeveloperApps(org_name=apigee_organization)
    await api.create_new_app()
    yield api
    await api.destroy_app()


@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def test_app_no_product_subscriptions(apigee_organization):
    api = ApigeeApiDeveloperApps(org_name=apigee_organization)
    await api.create_new_app()
    yield api
    await api.destroy_app()


@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def test_app_no_jwks_url(apigee_organization, test_product):
    api = ApigeeApiDeveloperApps(org_name=apigee_organization)
    await api.create_new_app()
    yield api
    await api.destroy_app()


@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def test_app_other_environment(test_product_other_environment):
    api = ApigeeApiDeveloperApps(org_name="nhsd-nonprod")
    await api.create_new_app()
    yield api
    await api.destroy_app()


@pytest.fixture(scope='module', autouse=True)
@pytest.mark.asyncio
async def add_jwks_url_to_app(test_app: ApigeeApiDeveloperApps):
    await test_app.set_custom_attributes({
        "jwks-resource-url": TEST_JWKS_URL
    })


@pytest.fixture(scope='module', autouse=True)
@pytest.mark.asyncio
async def add_jwks_url_to_other_environment_app(test_app: ApigeeApiDeveloperApps):
    await test_app.set_custom_attributes({
        "jwks-resource-url": TEST_JWKS_URL
    })


@pytest.fixture(scope='module', autouse=True)
@pytest.mark.asyncio
async def add_product_to_app(test_product: ApigeeApiProducts, test_app: ApigeeApiDeveloperApps):
    await test_app.add_api_product([test_product.name])


@pytest.fixture(scope='module', autouse=True)
@pytest.mark.asyncio
async def add_product_to_no_jwks_url_app(test_product: ApigeeApiProducts, test_app_no_jwks_url: ApigeeApiDeveloperApps):
    await test_app_no_jwks_url.add_api_product([test_product.name])


@pytest.fixture(scope='module', autouse=True)
@pytest.mark.asyncio
async def add_product_to_other_environment_app(
        test_product_other_environment: ApigeeApiProducts,
        test_app_other_environment: ApigeeApiDeveloperApps
):
    await test_app_other_environment.add_api_product([test_product_other_environment.name])


@pytest.fixture(scope='module', autouse=True)
@pytest.mark.asyncio
async def set_product_environment(test_product: ApigeeApiProducts):
    await test_product.update_environments([TEST_ENVIRONMENT])


@pytest.fixture(scope='module', autouse=True)
@pytest.mark.asyncio
async def set_other_environment_product_environment(test_product_other_environment: ApigeeApiProducts):
    other_environment = "internal-dev" if TEST_ENVIRONMENT == "internal-qa" else "internal-qa"
    await test_product_other_environment.update_environments([other_environment])


@pytest.fixture(autouse=True)
@pytest.mark.asyncio
async def sleep_before_test():
    """ sleep for 200 millis before each test to avoid hitting the SpikeArrest policy """
    await asyncio.sleep(0.2)


@pytest.mark.asyncio
async def test_jwks_endpoint_valid_request(apigee_root_url, test_app: ApigeeApiDeveloperApps):
    client_id = test_app.client_id
    response = requests.get(f"{apigee_root_url}/key-locator/jwks?clientId={client_id}")
    assert ("keys" in response.json())


@pytest.mark.asyncio
async def test_jwks_endpoint_no_client_id(apigee_root_url):
    response = requests.get(f"{apigee_root_url}/key-locator/jwks")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_jwks_endpoint_empty_client_id(apigee_root_url):
    response = requests.get(f"{apigee_root_url}/key-locator/jwks?clientId=")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_jwks_endpoint_invalid_client_id(apigee_root_url):
    response = requests.get(f"{apigee_root_url}/key-locator/jwks?clientId=notAValidClientId")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_jwks_endpoint_no_product_subscriptions(
        apigee_root_url,
        test_app_no_product_subscriptions: ApigeeApiDeveloperApps
):
    client_id = test_app_no_product_subscriptions.client_id
    response = requests.get(f"{apigee_root_url}/key-locator/jwks?clientId={client_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_jwks_endpoint_no_jwks_url_for_app(
        apigee_root_url,
        test_app_no_jwks_url: ApigeeApiDeveloperApps
):
    client_id = test_app_no_jwks_url.client_id
    response = requests.get(f"{apigee_root_url}/key-locator/jwks?clientId={client_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_jwks_endpoint_app_not_for_this_environment(
        apigee_root_url,
        test_app_other_environment: ApigeeApiDeveloperApps
):
    client_id = test_app_other_environment.client_id
    response = requests.get(f"{apigee_root_url}/key-locator/jwks?clientId={client_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_jku_endpoint_valid_request(apigee_root_url, test_app: ApigeeApiDeveloperApps):
    client_id = test_app.client_id
    response = requests.get(f"{apigee_root_url}/key-locator/jku?clientId={client_id}")
    assert (response.text == TEST_JWKS_URL)


@pytest.mark.asyncio
async def test_jku_endpoint_no_client_id(apigee_root_url):
    response = requests.get(f"{apigee_root_url}/key-locator/jku")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_jku_endpoint_empty_client_id(apigee_root_url):
    response = requests.get(f"{apigee_root_url}/key-locator/jku?clientId=")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_jku_endpoint_invalid_client_id(apigee_root_url):
    response = requests.get(f"{apigee_root_url}/key-locator/jku?clientId=notAValidClientId")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_jku_endpoint_no_product_subscriptions(
        apigee_root_url,
        test_app_no_product_subscriptions: ApigeeApiDeveloperApps
):
    client_id = test_app_no_product_subscriptions.client_id
    response = requests.get(f"{apigee_root_url}/key-locator/jku?clientId={client_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_jku_endpoint_no_jwks_url_for_app(apigee_root_url, test_app_no_jwks_url: ApigeeApiDeveloperApps):
    client_id = test_app_no_jwks_url.client_id
    response = requests.get(f"{apigee_root_url}/key-locator/jku?clientId={client_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_jku_endpoint_app_not_for_this_environment(
        apigee_root_url,
        test_app_other_environment: ApigeeApiDeveloperApps
):
    client_id = test_app_other_environment.client_id
    response = requests.get(f"{apigee_root_url}/key-locator/jku?clientId={client_id}")
    assert response.status_code == 404
