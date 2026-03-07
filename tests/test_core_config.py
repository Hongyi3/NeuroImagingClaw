from __future__ import annotations

import json

from clawneuro.core import load_config
from clawneuro.skills.bids_auditor import BidsAuditorConfig


def test_load_config_supports_yaml_json_and_toml(tmp_path, fixtures_root):
    config_data = {
        "bids_root": str(fixtures_root / "bids" / "minimal"),
        "output_root": str(tmp_path / "out"),
        "execute": False,
    }

    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text(
        "bids_root: {0}\noutput_root: {1}\nexecute: false\n".format(
            config_data["bids_root"], config_data["output_root"]
        ),
        encoding="utf-8",
    )
    json_path = tmp_path / "config.json"
    json_path.write_text(json.dumps(config_data), encoding="utf-8")
    toml_path = tmp_path / "config.toml"
    toml_path.write_text(
        'bids_root = "{0}"\noutput_root = "{1}"\nexecute = false\n'.format(
            config_data["bids_root"], config_data["output_root"]
        ),
        encoding="utf-8",
    )

    for path in (yaml_path, json_path, toml_path):
        config = load_config(path, BidsAuditorConfig)
        assert config.bids_root == fixtures_root / "bids" / "minimal"
        assert config.execute is False
