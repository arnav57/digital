from typing import Optional
import logging
import cocotb
from cocotb.triggers import Edge


class ResetMonitor:
    """Passively tracks active-low reset assertion and deassertion."""

    def __init__(self, rstn_signal, name: str = None):
        self.rstn = rstn_signal
        self.name = "rstn_mon" if name is None else name

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)

        self._task: Optional[cocotb.Task] = None
        self._last_val: Optional[int] = None

    @property
    def is_asserted(self) -> bool:
        """Returns True only if reset is explicitly logic 0."""
        val = self.rstn.value
        return val.is_resolvable and int(val) == 0

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = cocotb.start_soon(self._run())

    def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.kill()
            self._task = None

    async def _run(self) -> None:
        # Check initial state at time zero if already resolvable
        init_val = self.rstn.value
        if init_val.is_resolvable:
            self._last_val = int(init_val)

        while True:
            await self.rstn.value_change
            curr = self.rstn.value

            # Ignore unresolvable states (X, Z)
            if not curr.is_resolvable:
                self.logger.warning("Reset line entered unresolvable state: %s", str(curr))
                self._last_val = None
                continue

            curr_val = int(curr)

            # Coming out of X/Z or uninitialized
            if self._last_val is None:
                self._last_val = curr_val
                continue

            # Only trigger on valid logic transitions between 0 and 1
            if curr_val != self._last_val:
                self._last_val = curr_val
                if curr_val == 0:
                    self.logger.info("Reset has asserted (active-low 0)")
                else:
                    self.logger.info("Reset has deasserted (1)")