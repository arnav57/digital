# arnav57/digital

> A Minimal RTL Design Library with standard components, bigger projects, and some verification "IP"

## Environment Setup

This setup uses cocotb-2.1 to simulate alongside questa. You will need to do the following to setup the repository. Note that these instructions are for windows users. Linux users should be able to follow through a venv (hint: create a venv)

1. Install Miniconda
1. git clone this repo
1. Follow installation instructions for cocotb from: https://docs.cocotb.org/en/stable/install.html
1. `cd digital && pip install -e . `

## Running Simulations

After following the setup steps above you can run a simulation by invoking the `run.py` script inside digital/common/scripts/


**Example Run Command:**
```
cd digital;
cls & python common\scripts\run.py -tb compute -test cordic_tests;
```

- `-tb <block-level-folder>` accepts the name of a block-level folder in this repo that has unit tests (compute, memory, ...)
- `-test <testcase>` accepts the name of any file inside `<block-level-folder>/dv/tests/`

More things may be added. As always documentation will lag behind :)