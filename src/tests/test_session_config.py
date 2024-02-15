from bot.session_config import SessionConfig

def test_session_config():
    SessionConfig.set_node("pve")
    assert SessionConfig.get_node() == "pve"