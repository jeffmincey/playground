"""The example configurations must follow the rule grammar in docs/07."""

import pytest

yaml = pytest.importorskip("yaml")

from check_config import CONFIG_DIR, check

BAD = """
module: { address: 1, peers: [0] }
inputs: { IN7: { mode: DISABLED } }
aux:
  AUX1:
    rating_a: "2"
    on_host_loss: OFF
    rule:
      condition: "IN9 is_on OR M1.OUT4 is_on OR IN7 is_on OR VBAT > hysteresis(12, 13) for 500 OR IGN is_on"
"""


def test_committed_configurations_are_clean():
    files = sorted(CONFIG_DIR.glob("*.yaml"))
    assert files
    for path in files:
        assert check(yaml.safe_load(path.read_text())) == [], path.name


def test_each_kind_of_mistake_is_reported():
    errors = "\n".join(check(yaml.safe_load(BAD)))
    for fragment in ("rating_a = '2'", "on_host_loss = False", "5 terms",
                     "cannot parse 'IN9 is_on'", "M1.OUT4 is not from a configured peer",
                     "IN7 reads a DISABLED input"):
        assert fragment in errors, fragment
