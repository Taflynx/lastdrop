#!/bin/bash
# Full pipeline: model -> threads -> print orientation -> Bambu 3MF files
set -e
cd "$(dirname "$0")"
python3 build.py
python3 finish_threads.py
python3 export_print.py
python3 make_bambu_3mf_2plates.py
python3 make_bambu_3mf_color.py
