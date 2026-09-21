import os
import sys
from pathlib import Path
from cocotb_tools.runner import get_runner
import argparse
from datetime import datetime

from sources import get_sources_for
from dirs import SIM_DIRECTORY_BASE, ROOT_DIR

parser = argparse.ArgumentParser(
    description = "Main simulation build script for this repository"
)

TB_CHOICES = ['compute', 'memory']
parser.add_argument("-tb", "--tb", type=str, required=True, choices=TB_CHOICES, help="Block level testbench to run")
parser.add_argument("-test", "--test", type=str, required=True, help="Testcase to run from chosen block level testbench" )

def create_get_build_dir(time):
    sim_folder = (SIM_DIRECTORY_BASE / time).resolve()
    sim_folder.mkdir(parents=True, exist_ok=True)
    return sim_folder

def find_test_file(filename: str):
    # Find all dv/tests directories
    # Searches directly for matching paths matching the pattern anywhere in the tree
    found_files = list(ROOT_DIR.glob(f"*/dv/tests/**/{filename}.py"))

    if len(found_files) == 0:
        raise RuntimeError(f"\n\nCould not find test file with the name: '{filename}.py' in the repo")
    elif len(found_files) > 1:
        raise RuntimeError(f"\n\nFound multiple test files with the same name:\n{found_files}\n Please fix this collision")

    print(f"Found test file: '{str(found_files[0])}'")
    return found_files[0]

def get_run_command():
    python_exe  = sys.executable
    python_args = sys.argv
    return f"{python_exe} " + " ".join(python_args)

def create_run_marker(dir:Path):
    with open(str(dir / 'run_command'), 'w') as f:
        f.write(get_run_command())

def main():
    args = parser.parse_args()
    args = vars(args)

    now = datetime.now().strftime("%B%d_%H%M%S")
    tb_top = args['tb']

    print(
        f"Building tb = {tb_top}, "
        f"current timestamp is: {now}"
    )

    sources, top   = get_sources_for(tb_top)
    build_dir = create_get_build_dir(now)

    # search for the test name
    test_file_name = args['test']
    test_file_path = find_test_file(test_file_name)
    sys.path.append(str(test_file_path.parent))

    print(f"\n\n=== RUNNING TEST ===\n\n")

    ## create marker
    create_run_marker(build_dir)

    ## BUILD THE RUNNER
    sim = "questa"
    runner = get_runner(sim)
    runner.build(
        sources = sources,
        hdl_toplevel = top,
        build_dir = build_dir,
        timescale = ("1ns", "1ps"),
        waves = True
    )
    runner.test(
        hdl_toplevel = top,
        test_module = test_file_name,
        waves = True
    )



if __name__ == "__main__":
    main()