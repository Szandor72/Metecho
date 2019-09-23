"""
These tests are TRULY AWFUL but we're expecting the code in sf_run_flow
to change substantially, and as it stands, it's full of implicit
external calls, so this would be mock-heavy anyway.
"""

from contextlib import ExitStack
from unittest.mock import MagicMock, patch

import pytest

from ..sf_run_flow import (
    capitalize,
    create_org_and_run_flow,
    delete_scratch_org,
    deploy_org_settings,
    get_access_token,
    get_devhub_api,
    get_login_url,
    get_org_details,
    get_org_result,
    jwt_session,
    mutate_scratch_org,
    refresh_access_token,
)

PATCH_ROOT = "metashare.api.sf_run_flow"


def test_capitalize():
    assert capitalize("fooBar") == "FooBar"


def test_jwt_session():
    with ExitStack() as stack:
        requests = stack.enter_context(patch(f"{PATCH_ROOT}.requests"))
        stack.enter_context(patch(f"{PATCH_ROOT}.pyjwt"))

        jwt_session(MagicMock(), MagicMock(), MagicMock(), url=None, is_sandbox=False)
        assert requests.post.called


def test_refresh_access_token():
    with ExitStack() as stack:
        stack.enter_context(patch(f"{PATCH_ROOT}.requests"))
        stack.enter_context(patch(f"{PATCH_ROOT}.pyjwt"))
        OrgConfig = stack.enter_context(patch(f"{PATCH_ROOT}.OrgConfig"))

        refresh_access_token(
            config=MagicMock(), org_name=MagicMock(), login_url="https://example.com"
        )

        assert OrgConfig.called


def test_get_devhub_api():
    with ExitStack() as stack:
        stack.enter_context(patch(f"{PATCH_ROOT}.jwt_session"))
        SimpleSalesforce = stack.enter_context(patch(f"{PATCH_ROOT}.SimpleSalesforce"))

        get_devhub_api(devhub_username="devhub_username")

        assert SimpleSalesforce.called


def test_get_org_details():
    with ExitStack() as stack:
        stack.enter_context(patch(f"{PATCH_ROOT}.os"))
        json = stack.enter_context(patch(f"{PATCH_ROOT}.json"))

        config, definition = get_org_details(
            cci=MagicMock(), org_name=MagicMock(), project_path=""
        )

        assert json.load.called


def test_get_org_result():
    result = get_org_result(
        email=MagicMock(),
        repo_owner=MagicMock(),
        repo_name=MagicMock(),
        repo_branch=MagicMock(),
        scratch_org_config=MagicMock(),
        scratch_org_definition={"edition": MagicMock()},
        cci=MagicMock(),
        devhub_api=MagicMock(),
    )

    assert result


def test_mutate_scratch_org():
    scratch_org_config = MagicMock()
    mutate_scratch_org(
        scratch_org_config=scratch_org_config,
        org_result={"LoginUrl": None, "ScratchOrg": None, "SignupUsername": None},
        email=MagicMock(),
    )

    assert scratch_org_config.config.update.called


def test_get_login_url():
    result = get_login_url({"SignupInstance": "test"})
    assert result == "https://test.salesforce.com"


def test_get_access_token():
    with patch(f"{PATCH_ROOT}.SalesforceOAuth2") as SalesforceOAuth2:
        get_access_token(
            login_url="https://example.com",
            org_result=MagicMock(),
            scratch_org_config=MagicMock(),
        )

        assert SalesforceOAuth2.called


class TestDeployOrgSettings:
    def test_org_preference_settings(self):
        with ExitStack() as stack:
            stack.enter_context(patch(f"{PATCH_ROOT}.temporary_dir"))
            stack.enter_context(patch(f"{PATCH_ROOT}.os"))
            stack.enter_context(patch(f"{PATCH_ROOT}.open"))
            stack.enter_context(patch(f"{PATCH_ROOT}.refresh_access_token"))
            stack.enter_context(patch(f"{PATCH_ROOT}.TaskConfig"))
            Deploy = stack.enter_context(patch(f"{PATCH_ROOT}.Deploy"))

            section_setting = MagicMock()
            settings = MagicMock()
            scratch_org_definition = MagicMock()

            section_setting.items.return_value = [(MagicMock(), MagicMock())]
            settings.items.return_value = [("orgPreferenceSettings", section_setting)]
            scratch_org_definition.get.return_value = settings

            deploy_org_settings(
                cci=MagicMock(),
                login_url="https://example.com",
                org_config=MagicMock(),
                org_name=MagicMock(),
                scratch_org_config=MagicMock(),
                scratch_org_definition=scratch_org_definition,
            )
            assert Deploy.called

    def test_other_settings(self):
        with ExitStack() as stack:
            stack.enter_context(patch(f"{PATCH_ROOT}.temporary_dir"))
            stack.enter_context(patch(f"{PATCH_ROOT}.os"))
            stack.enter_context(patch(f"{PATCH_ROOT}.open"))
            stack.enter_context(patch(f"{PATCH_ROOT}.refresh_access_token"))
            stack.enter_context(patch(f"{PATCH_ROOT}.TaskConfig"))
            Deploy = stack.enter_context(patch(f"{PATCH_ROOT}.Deploy"))

            section_setting = MagicMock()
            settings = MagicMock()
            scratch_org_definition = MagicMock()

            section_setting.items.return_value = [(MagicMock(), MagicMock())]
            settings.items.return_value = [("something else", section_setting)]
            scratch_org_definition.get.return_value = settings

            deploy_org_settings(
                cci=MagicMock(),
                login_url="https://example.com",
                org_config=MagicMock(),
                org_name=MagicMock(),
                scratch_org_config=MagicMock(),
                scratch_org_definition=scratch_org_definition,
            )
            assert Deploy.called

    def test_no_settings(self):
        with ExitStack() as stack:
            stack.enter_context(patch(f"{PATCH_ROOT}.temporary_dir"))
            stack.enter_context(patch(f"{PATCH_ROOT}.os"))
            stack.enter_context(patch(f"{PATCH_ROOT}.open"))
            stack.enter_context(patch(f"{PATCH_ROOT}.refresh_access_token"))
            stack.enter_context(patch(f"{PATCH_ROOT}.TaskConfig"))
            Deploy = stack.enter_context(patch(f"{PATCH_ROOT}.Deploy"))

            section_setting = MagicMock()
            settings = MagicMock()
            scratch_org_definition = MagicMock()

            section_setting.items.return_value = [(MagicMock(), MagicMock())]
            settings.items.return_value = [("orgPreferenceSettings", section_setting)]
            scratch_org_definition.get.return_value = None

            deploy_org_settings(
                cci=MagicMock(),
                login_url="https://example.com",
                org_config=MagicMock(),
                org_name=MagicMock(),
                scratch_org_config=MagicMock(),
                scratch_org_definition=scratch_org_definition,
            )
            assert not Deploy.called


def test_create_org_and_run_flow():
    with ExitStack() as stack:
        stack.enter_context(patch(f"{PATCH_ROOT}.os"))
        stack.enter_context(patch(f"{PATCH_ROOT}.BaseCumulusCI"))
        stack.enter_context(patch(f"{PATCH_ROOT}.get_devhub_api"))
        get_org_details = stack.enter_context(patch(f"{PATCH_ROOT}.get_org_details"))
        get_org_details.return_value = (MagicMock(), MagicMock())
        stack.enter_context(patch(f"{PATCH_ROOT}.get_org_result"))
        stack.enter_context(patch(f"{PATCH_ROOT}.mutate_scratch_org"))
        stack.enter_context(patch(f"{PATCH_ROOT}.get_login_url"))
        stack.enter_context(patch(f"{PATCH_ROOT}.get_access_token"))
        stack.enter_context(patch(f"{PATCH_ROOT}.deploy_org_settings"))
        stack.enter_context(patch(f"{PATCH_ROOT}.cd"))

        create_org_and_run_flow(
            repo_owner=MagicMock(),
            repo_name=MagicMock(),
            repo_branch=MagicMock(),
            user=MagicMock(),
            flow_name=MagicMock(),
            project_path=MagicMock(),
        )


@pytest.mark.django_db
def test_delete_scratch_org(scratch_org_factory):
    scratch_org = scratch_org_factory(config={"org_id": "some-id"})
    with ExitStack() as stack:
        stack.enter_context(patch(f"{PATCH_ROOT}.os"))
        devhub_api = MagicMock()
        get_devhub_api = stack.enter_context(patch(f"{PATCH_ROOT}.get_devhub_api"))
        get_devhub_api.return_value = devhub_api
        devhub_api.query.return_value = {"records": [{"Id": "some-id"}]}

        delete_scratch_org(scratch_org)

        assert devhub_api.ActiveScratchOrg.delete.called