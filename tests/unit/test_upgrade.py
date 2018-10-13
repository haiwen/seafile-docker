import glob
from os.path import abspath, basename, exists, dirname, join

import pytest
from mock import patch

from upgrade import is_minor_upgrade, collect_upgrade_scripts

@pytest.mark.parametrize("v1, v2, result", [
    ('6.3.0', '6.3.0', False),
    ('6.3.0', '6.3.1', True),
    ('6.3.0', '6.4.0', False),
    ('6.3.1', '6.4.0', False),
    ('6.4.0', '6.3.0', False),
])
def test_minor_upgrade(v1, v2, result):
    assert is_minor_upgrade(v1, v2) == result


def test_collect_upgrade_scripts():
    files = [
        'upgrade_4.4_5.0.sh',
        'upgrade_5.0_5.1.sh',
        'upgrade_5.1_6.0.sh',
        'upgrade_6.0_6.1.sh',
    ]
    def fake_glob(pattern):
        return [join(dirname(pattern), f) for f in files]
    def _basename(files):
        return [basename(f) for f in files]
    with patch.object(glob, 'glob', fake_glob):
        assert _basename(collect_upgrade_scripts('5.0.1', '6.1.0')) == files[1:]
