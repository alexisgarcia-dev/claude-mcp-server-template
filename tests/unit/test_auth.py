"""Unit tests for StaticTokenVerifier auth setup in server.py."""



def test_static_token_verifier_demo_tokens_present():
    """server module must expose _demo_token_verifier with demo-readonly + demo-readwrite."""
    from src.server import _demo_token_verifier

    assert _demo_token_verifier is not None

    tokens = _demo_token_verifier.tokens
    assert "demo-readonly" in tokens
    assert "demo-readwrite" in tokens


def test_static_token_verifier_scopes_separation():
    """demo-readonly has read:pantry only, demo-readwrite has both scopes."""
    from src.server import _demo_token_verifier

    ro_scopes = _demo_token_verifier.tokens["demo-readonly"]["scopes"]
    rw_scopes = _demo_token_verifier.tokens["demo-readwrite"]["scopes"]

    assert "read:pantry" in ro_scopes
    assert "write:pantry" not in ro_scopes

    assert "read:pantry" in rw_scopes
    assert "write:pantry" in rw_scopes


def test_mcp_instance_has_auth_configured():
    """FastMCP instance must have auth=StaticTokenVerifier wired."""
    from src.server import mcp

    # FastMCP exposes auth via internal attribute (varies by version)
    auth = getattr(mcp, "auth", None) or getattr(mcp, "_auth", None)
    assert auth is not None, "mcp.auth not configured"
