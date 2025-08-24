import sys
from io import StringIO
from unittest.mock import patch

import pytest

from bookspine.cli import main


def test_app_help():
    with patch.object(sys, "argv", ["bookspine", "--help"]), patch("sys.stdout", new=StringIO()) as fake_out:
        with pytest.raises(SystemExit) as e:
            main()
        assert e.type is SystemExit
        assert e.value.code == 0
        assert "usage: bookspine [-h]" in fake_out.getvalue()
