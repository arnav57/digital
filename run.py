from pathlib import Path
from cocotb_tools.runner import get_runner
import sys

def test_cordic_pipe():
    sim = "questa"
    proj_root = Path('C:/Users/arnav/Documents/deepseek/projects/capstone/').resolve()
    rtl_root  = (proj_root / 'compute' / 'rtl').resolve()
    tests_dir   = (proj_root / 'compute' / 'dv' / 'tests').resolve()

    sources = [
        rtl_root / "cordic_stage.sv",
        rtl_root / "cordic_pipe.sv",
    ]

    sys.path.append(str(tests_dir))

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="cordic_pipe",
        build_dir=proj_root / "sim_build",
        waves = True
    )

    runner.test(
        hdl_toplevel="cordic_pipe",
        test_module='cordic_tests',
        waves = True
    )

if __name__ == "__main__":
    test_cordic_pipe()