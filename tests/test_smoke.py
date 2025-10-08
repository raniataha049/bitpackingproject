def test_import_cli():
    import cli.bitpacking_cli as mod
    assert hasattr(mod, "cli")
