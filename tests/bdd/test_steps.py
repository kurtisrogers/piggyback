"""BDD step definitions for Playwright end-to-end scenarios."""

from __future__ import annotations

import json

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.conftest import DEMO_PASSWORD, DEMO_USERNAME

pytestmark = pytest.mark.django_db(transaction=True)

scenarios("home.feature")
scenarios("catalog.feature")
scenarios("auth.feature")


@pytest.fixture
def site_url(live_server):
    return live_server.url


@pytest.fixture
def api_response():
    return {}


@given("the piggyback sample catalog is loaded")
def catalog_loaded(loaded_catalog):
    """Catalog JSON fixtures loaded via the loaded_catalog fixture."""


@given("I am signed in as the demo user")
def signed_in_demo_user(page, site_url, demo_user):
    page.goto(f"{site_url}/admin/login/")
    page.fill('input[name="username"]', DEMO_USERNAME)
    page.fill('input[name="password"]', DEMO_PASSWORD)
    page.click('input[type="submit"]')
    page.wait_for_url("**/")


@when(parsers.parse('I visit "{path}"'))
def visit_path(page, site_url, path):
    page.goto(f"{site_url}{path}")


@when(parsers.parse('I request "{path}"'))
def request_path(page, site_url, path, api_response):
    page.goto(site_url + "/")
    result = page.evaluate(
        """async (path) => {
            const response = await fetch(path, {credentials: 'include'});
            const text = await response.text();
            return {status: response.status, body: text};
        }""",
        path,
    )
    api_response["status"] = result["status"]
    api_response["body"] = result["body"]


@then(parsers.parse('I should see "{text}"'))
def should_see_text(page, text):
    locator = page.get_by_text(text, exact=False).first
    assert locator.is_visible(), f'Expected to see "{text}" on the page'


@then("I should see a card template")
def should_see_template(page):
    assert page.locator(".pb-template-card").count() >= 1


@then(parsers.parse("the API response status should be {status:d}"))
def api_status(api_response, status):
    assert api_response.get("status") == status


@then("the API response should include templates")
def api_has_templates(api_response):
    data = json.loads(api_response["body"])
    items = data.get("results", data)
    assert len(items) >= 1


@then(parsers.parse('the API response should include "{text}"'))
def api_includes_text(api_response, text):
    assert text in api_response["body"]
