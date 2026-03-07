#!/usr/bin/env bash
set -euo pipefail

# /private/tmp/clawneuro-m3-bench/bin/dcm2bids [succeeded]
/private/tmp/clawneuro-m3-bench/bin/dcm2bids -d sources/dcm_qa_nih-d302d6e241dda747b79ee1724ada3200179755a2/In -p ID01 -o run-output/bids_dataset -c code/dcm2bids_config.json --auto_extract_entities

# bids-validator [succeeded]
/private/tmp/clawneuro-m3-bench/bin/bids-validator-deno run-output/bids_dataset --format json
