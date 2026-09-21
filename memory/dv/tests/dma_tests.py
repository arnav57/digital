"""cocotb tests for sdram_temp (the request stage) sitting in front of the SDRAM controller.

The Python `Patgen` below plays the role of the pattern generator.  Its handshake is:
present a request, then look at `sdram_ready_o` on each clock edge.  A value read right
after `await RisingEdge` is what the DUT sampled on that edge, so ready==1 there means
"the stage took my request on this edge".  Requests issued in the same step as the previous
acceptance go out back-to-back, one per cycle.
"""
import logging
import os
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

CLK_NS = 20   # 50 MHz, same as the Platform Designer clock
log = logging.getLogger("dma-tests")
log.setLevel(logging.DEBUG)


def merge_lanes(old: int, new: int, be: int) -> int:
    """Byte-lane merge, the same thing the SDRAM does on a partial write (be bit i = lane i)."""
    out = old
    for lane in range(4):
        if (be >> lane) & 1:
            mask = 0xFF << (8 * lane)
            out = (out & ~mask) | (new & mask)
    return out & 0xFFFFFFFF


class Patgen:
    def __init__(self, dut):
        self.dut = dut
        self.cycle = 0
        self.reads = []          # every returned read beat, in order (None if it contained X)
        self._idle()
        cocotb.start_soon(self._monitor())

    def _idle(self):
        self.dut.sdram_rd_en_i.value = 0
        self.dut.sdram_wr_en_i.value = 0

    async def _monitor(self):
        d = self.dut
        while True:
            await RisingEdge(d.clk_i)
            self.cycle += 1
            v = d.sdram_rd_valid_o.value
            if v.is_resolvable and v == 1:
                raw = d.sdram_rd_data_o.value
                self.reads.append(int(raw) if raw.is_resolvable else None)

    async def _issue(self, is_wr, addr, data, be):
        d = self.dut
        d.sdram_addr_i.value = addr
        d.sdram_byte_en_i.value = be
        d.sdram_wr_data_i.value = data
        d.sdram_wr_en_i.value = int(is_wr)
        d.sdram_rd_en_i.value = int(not is_wr)
        while True:
            await RisingEdge(d.clk_i)
            r = d.sdram_ready_o.value
            if r.is_resolvable and r == 1:            # taken on this edge
                break
        accepted_at = self.cycle
        self._idle()                                   # overridden if another request follows immediately
        return accepted_at

    async def write(self, addr, data, be=0xF):
        return await self._issue(True, addr, data, be)

    async def read(self, addr):
        return await self._issue(False, addr, 0, 0xF)

    async def gap(self, n):
        await ClockCycles(self.dut.clk_i, n)

    async def wait_reads(self, n, timeout=20000):
        for _ in range(timeout):
            if len(self.reads) >= n:
                return
            await RisingEdge(self.dut.clk_i)
        raise TimeoutError(f"only {len(self.reads)} of {n} read beats came back")


async def start(dut) -> Patgen:
    cocotb.start_soon(Clock(dut.clk_i, CLK_NS, unit="ns").start())
    bus = Patgen(dut)
    dut.rstn_i.value = 0
    await ClockCycles(dut.clk_i, 5)
    dut.rstn_i.value = 1          # note: no extra wait; sdram_ready_o holds us off until the controller is out of reset
    bus.cycle = 0                 # cycle 0 = reset release
    return bus


def fmt(x):
    return "X" if x is None else f"0x{x:08x}"


@cocotb.test()
async def test_write_then_read(dut):
    """16 writes, then 16 reads.  Watch WHEN each request is accepted."""
    bus = await start(dut)
    n = 16
    for i in range(n):
        at = await bus.write(i, 0xA5A50000 + i)
        log.info(f"write #{i:2d} accepted at cycle {at:5d}")
    for i in range(n):
        at = await bus.read(i)
        log.info(f"read  #{i:2d} accepted at cycle {at:5d}")
    await bus.wait_reads(n)
    for i in range(n):
        assert bus.reads[i] == 0xA5A50000 + i, f"word {i}: got {fmt(bus.reads[i])}"
    log.info("all 16 words matched")


@cocotb.test()
async def test_byte_enables(dut):
    """Partial-lane writes only change the enabled bytes (catches byte-enable polarity bugs)."""
    bus = await start(dut)
    await bus.write(0x40, 0x11223344, be=0b1111)
    await bus.write(0x40, 0xAABBCCDD, be=0b0101)    # lanes 0 and 2 only
    await bus.write(0x41, 0xFFFFFFFF, be=0b1111)
    await bus.write(0x41, 0x00000000, be=0b0011)    # clear the low two bytes
    await bus.read(0x40)
    await bus.read(0x41)
    await bus.wait_reads(2)
    assert bus.reads[0] == 0x11BB33DD, f"got {fmt(bus.reads[0])}, expected 0x11bb33dd"
    assert bus.reads[1] == 0xFFFF0000, f"got {fmt(bus.reads[1])}, expected 0xffff0000"


@cocotb.test()
async def test_throughput(dut):
    """Cycles per word for sequential vs row-hopping reads (numbers for the perf model)."""
    bus = await start(dut)
    for a in range(3):                                # get past the ~100 us power-up init first
        await bus.read(a)
    await bus.wait_reads(3)

    async def measure(name, n, stride):
        base = len(bus.reads)
        t0 = bus.cycle
        for i in range(n):
            await bus.read((i * stride) & 0x3FFFFF)
        await bus.wait_reads(base + n)
        cpw = (bus.cycle - t0) / n
        log.info(f"{name:26s}: {n} reads in {bus.cycle - t0} cycles = {cpw:.2f} cycles/word")
        return cpw

    seq = await measure("sequential (stride 1)", 256, 1)
    await measure("row-hopping (stride 256)", 256, 256)
    assert seq < 1.5, "sequential reads should stream at ~1 word/cycle; the request stage is stalling"


@cocotb.test()
async def test_random_vs_model(dut):
    """Random reads/writes/byte-enables/gaps over a few colliding addresses, checked against a Python model."""
    seed = int(os.environ.get("SEED", "1"))
    rng = random.Random(seed)
    log.info(f"seed = {seed}")
    bus = await start(dut)

    addrs = [0x000000, 0x000001, 0x0000FF, 0x000100, 0x100000, 0x100001, 0x3FFFFF, 0x2A5A5A]
    model, expected = {}, []

    for a in addrs:                                    # fill everything first so no read returns X
        v = rng.getrandbits(32)
        model[a] = v
        await bus.write(a, v)

    n_ops = 300
    for _ in range(n_ops):
        a = rng.choice(addrs)
        if rng.random() < 0.5:
            data, be = rng.getrandbits(32), rng.randrange(1, 16)
            model[a] = merge_lanes(model[a], data, be)
            await bus.write(a, data, be)
        else:
            expected.append(model[a])                  # in-order controller: value at issue time
            await bus.read(a)
        if rng.random() < 0.3:
            await bus.gap(rng.randrange(1, 6))

    await bus.wait_reads(len(expected))
    bad = [(i, e, g) for i, (e, g) in enumerate(zip(expected, bus.reads)) if e != g]
    for i, e, g in bad[:5]:
        log.error(f"read #{i}: expected {fmt(e)}, got {fmt(g)}")
    assert not bad, f"{len(bad)} of {len(expected)} reads mismatched (seed {seed})"
    log.info(f"{len(expected)} reads matched the model")