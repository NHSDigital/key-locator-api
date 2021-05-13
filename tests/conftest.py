import asyncio
import os

import pytest
from api_test_utils.apigee_api_apps import ApigeeApiDeveloperApps
from api_test_utils.apigee_api_products import ApigeeApiProducts

JWKS_URL = "https://raw.githubusercontent.com/NHSDigital/identity-service-jwks" \
           "/main/jwks/internal-dev/278af795-6884-42dd-a713-f2b03927abb5.json"
ENVIRONMENT = os.environ["APIGEE_ENVIRONMENT"]
BASE_PATH = os.environ["SERVICE_BASE_PATH"]


# Common fixtures

@pytest.fixture(scope='module')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def sleep_before_test():
    """ sleep for 200 millis before each test to avoid hitting the SpikeArrest policy """
    await asyncio.sleep(0.2)


@pytest.fixture(scope='module')
def apigee_root_url():
    return "https://api.service.nhs.uk" if ENVIRONMENT == "prod" else f"https://{ENVIRONMENT}.api.service.nhs.uk"


@pytest.fixture(scope='module')
def service_root_url(apigee_root_url):
    return f"{apigee_root_url}/{BASE_PATH}"


@pytest.fixture(scope='module')
def apigee_organization():
    return "nhsd-prod" if ENVIRONMENT in ["int", "prod"] else "nhsd-nonprod"


@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def test_product(apigee_organization):
    api = ApigeeApiProducts(org_name=apigee_organization)
    api.environments = [ENVIRONMENT]
    await api.create_new_product()
    yield api
    await api.destroy_product()


# App with valid configuration

@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def test_app_valid_config(apigee_organization, test_product):
    api = ApigeeApiDeveloperApps(
        org_name=apigee_organization,
        developer_email=f"apm-testing-{ENVIRONMENT}@nhs.net"
    )
    await api.create_new_app()
    yield api
    await api.destroy_app()


@pytest.fixture(scope='module', autouse=True)
@pytest.mark.asyncio
async def add_jwks_url_to_app(test_app_valid_config):
    await test_app_valid_config.set_custom_attributes({
        "jwks-resource-url": JWKS_URL
    })


@pytest.fixture(scope='module', autouse=True)
@pytest.mark.asyncio
async def add_product_to_app(test_product: ApigeeApiProducts, test_app_valid_config):
    await test_app_valid_config.add_api_product([test_product.name])


# App with no JWKS URL configured

@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def test_app_no_jwks_url(apigee_organization, test_product):
    api = ApigeeApiDeveloperApps(
        org_name=apigee_organization,
        developer_email=f"apm-testing-{ENVIRONMENT}@nhs.net"
    )
    await api.create_new_app()
    yield api
    await api.destroy_app()


@pytest.fixture(scope='module', autouse=True)
@pytest.mark.asyncio
async def add_product_to_no_jwks_url_app(
        test_product: ApigeeApiProducts,
        test_app_no_jwks_url: ApigeeApiDeveloperApps
):
    await test_app_no_jwks_url.add_api_product([test_product.name])


# App with no API product subscriptions

@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def test_app_no_product_subscriptions(apigee_organization):
    api = ApigeeApiDeveloperApps(
        org_name=apigee_organization,
        developer_email=f"apm-testing-{ENVIRONMENT}@nhs.net"
    )
    await api.create_new_app()
    yield api
    await api.destroy_app()


@pytest.fixture(scope='module', autouse=True)
@pytest.mark.asyncio
async def add_jwks_url_to_no_products_app(test_app_no_product_subscriptions: ApigeeApiDeveloperApps):
    await test_app_no_product_subscriptions.set_custom_attributes({
        "jwks-resource-url": JWKS_URL
    })


# App subscribed to an API product for a different environment

@pytest.fixture(scope='module')
def other_environment():
    return "internal-qa" if ENVIRONMENT == "internal-dev" else "internal-dev"


@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def test_product_other_environment(other_environment):
    api = ApigeeApiProducts(org_name="nhsd-nonprod")
    api.environments = [other_environment]
    await api.create_new_product()
    yield api
    await api.destroy_product()


@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def test_app_other_environment(test_product_other_environment, other_environment):
    api = ApigeeApiDeveloperApps(
        org_name="nhsd-nonprod",
        developer_email=f"apm-testing-{other_environment}@nhs.net"
    )
    await api.create_new_app()
    yield api
    await api.destroy_app()


@pytest.fixture(scope='module', autouse=True)
@pytest.mark.asyncio
async def add_jwks_url_to_other_environment_app(test_app_other_environment: ApigeeApiDeveloperApps):
    await test_app_other_environment.set_custom_attributes({
        "jwks-resource-url": JWKS_URL
    })


@pytest.fixture(scope='module', autouse=True)
@pytest.mark.asyncio
async def add_product_to_other_environment_app(
        test_product_other_environment: ApigeeApiProducts,
        test_app_other_environment: ApigeeApiDeveloperApps
):
    await test_app_other_environment.add_api_product([test_product_other_environment.name])
