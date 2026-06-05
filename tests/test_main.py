import pytest
from isda_pptgen import main

def test_main_help(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["isda-pptgen", "--help"])
    with pytest.raises(SystemExit):
        main.main()
    captured = capsys.readouterr()
    assert "ISDA PPT Generator" in captured.out
