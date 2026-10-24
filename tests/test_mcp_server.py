"""Verifica que el servidor MCP carga y expone las 3 tools."""


def test_mcp_server_imports():
    import mcp_server.server as srv
    assert hasattr(srv, "get_public_keys")
    assert hasattr(srv, "verify_example")
    assert hasattr(srv, "verify_artifact")


def test_mcp_fastmcp_importable():
    """Regresion: si el SDK 'mcp' vuelve a estar shadoweado, este test falla."""
    from mcp.server.fastmcp import FastMCP  # noqa: F401
    assert True
