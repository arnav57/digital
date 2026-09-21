from pathlib import Path
from itertools import chain

from pprint import pprint

from dataclasses import dataclass
from typing import List, Optional

### DIRECTORIES

RUN_SCRIPT_PATH    = Path(__file__).resolve()
ROOT_DIR           = (RUN_SCRIPT_PATH.parent / '..' / '..').resolve()
COMMON_DIR         = (ROOT_DIR / 'common').resolve()
COMMON_SCRIPTS_DIR = (COMMON_DIR / 'scripts').resolve()
COMPUTE_DIR        = (ROOT_DIR / 'compute').resolve()
MEMORY_DIR         = (ROOT_DIR / 'memory').resolve()

SIM_DIRECTORY_BASE = (ROOT_DIR / 'waves').resolve()

### COMMON HELPERS
DEFAULT_RTL_EXTENSIONS = ['*.sv', '*.v']
DEFAULT_TEST_EXTENSIONS = ['*.py']

def get_rtl_from(rtl_dir:Path):
    files = [file for ext in DEFAULT_RTL_EXTENSIONS for file in rtl_dir.glob(ext)]
    print(f"Found {len(files)} RTL Sources from '{str(rtl_dir)}'")
    for file in files:
        print(f"\t+ {file.name}")
    return files

def get_tests_from(test_dir:Path):
    files = [file for ext in DEFAULT_TEST_EXTENSIONS for file in test_dir.glob(ext)]
    print(f"Found {len(files)} testcases from '{str(test_dir)}'")
    for file in files:
        print(f"\t+ {file.name}")
    return files

        
    
    
