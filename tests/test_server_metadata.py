from macinput.server import get_server_metadata
from macinput.settings import ServerSettings


def test_server_metadata_contains_prompt_and_resources():
    metadata = get_server_metadata(ServerSettings())
    assert metadata["name"] == "macinput"
    assert "ui_action_protocol" == metadata["prompt"]
    assert "macinput://best-practices" in metadata["resources"]
