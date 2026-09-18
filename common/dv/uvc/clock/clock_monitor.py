from typing import Optional
import logging
import cocotb
from cocotb.triggers import Edge, First, Timer


class ClockMonitor:

    def __init__(self, clk_signal, name: str = "clk_mon", timeout_ns: float = 100.0):
        self.clk = clk_signal
        self.name = name
        self.timeout_ns = timeout_ns
        self._task: Optional[cocotb.Task] = None

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)

        self.active = False
        self._last_val: Optional[int] = None

    def start(self):
        if not self._task or self._task.done():
            self._task = cocotb.start_soon(self._run())

    def stop(self):
        if self._task:
            self._task.kill()
            self._task = None

    async def _run(self):
        while True:
            edge_trigger = self.clk.value_change
            timeout = Timer(self.timeout_ns, unit="ns")

            first_event = await First(edge_trigger, timeout)

            if first_event is edge_trigger:
                # is_resolvable is True only if there are no X, Z, U, etc.
                val = self.clk.value
                if val.is_resolvable:
                    curr_val = int(val)
                    # Only treat as a true clock toggle if transitioning 0 <-> 1
                    if self._last_val is not None and curr_val != self._last_val:
                        if not self.active:
                            self.active = True
                            self.logger.info("Clock started toggling")
                    self._last_val = curr_val
                else:
                    # In X or Z
                    self._last_val = None
            else:
                # Timer expired without an edge
                if self.active:
                    self.active = False
                    self.logger.info("Clock stopped toggling")