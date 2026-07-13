from gazebo_mcp import server as srv


def test_tools_registered():
    assert callable(srv.gazebo_doctor)
    assert callable(srv.gazebo_spawn)
    assert "mock" in srv.gazebo_mode()
