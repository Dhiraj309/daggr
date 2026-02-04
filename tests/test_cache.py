"""Tests for cache directory resolution."""

import os
from pathlib import Path
from unittest import mock


def test_get_hf_home_respects_env_var():
    """Test that get_hf_home respects the HF_HOME environment variable."""
    from daggr.state import get_hf_home

    custom_path = "/custom/hf/cache"

    # Mock the huggingface_hub.constants module
    mock_constants = mock.MagicMock()
    mock_constants.HF_HOME = custom_path

    with mock.patch.dict("sys.modules", {"huggingface_hub": mock.MagicMock()}):
        with mock.patch(
            "huggingface_hub.constants", mock_constants, create=True
        ) as patched:
            # Re-import to get fresh function that will use the mock
            import importlib

            from daggr import state

            importlib.reload(state)
            result = state.get_hf_home()
            assert result == Path(custom_path)

            # Reload again to restore normal state
            importlib.reload(state)


def test_get_daggr_cache_dir_uses_hf_home():
    """Test that get_daggr_cache_dir uses the HF home directory."""
    from daggr.state import get_daggr_cache_dir

    with mock.patch("daggr.state.get_hf_home") as mock_hf_home:
        mock_hf_home.return_value = Path("/mock/hf/home")
        # Need to create a temp dir for mkdir to work
        with mock.patch.object(Path, "mkdir"):
            result = get_daggr_cache_dir()
            assert result == Path("/mock/hf/home/daggr")


def test_get_hf_home_fallback_without_huggingface_hub():
    """Test fallback when huggingface_hub is not installed."""
    import importlib

    from daggr import state

    # Simulate ImportError by removing huggingface_hub from imports
    with mock.patch.dict("sys.modules", {"huggingface_hub": None}):
        # Test with HF_HOME set
        with mock.patch.dict(os.environ, {"HF_HOME": "/custom/path"}):
            # Need to reload to pick up the mock
            importlib.reload(state)
            result = state.get_hf_home()
            assert result == Path("/custom/path")

    # Reload to restore normal state
    importlib.reload(state)


def test_daggr_cache_is_under_hf_home():
    """Test that daggr cache is directly under HF_HOME/daggr."""
    from daggr.state import get_daggr_cache_dir, get_hf_home

    hf_home = get_hf_home()
    daggr_cache = get_daggr_cache_dir()

    # The daggr cache should be directly under HF_HOME
    assert daggr_cache == hf_home / "daggr"
    assert daggr_cache.parent == hf_home
