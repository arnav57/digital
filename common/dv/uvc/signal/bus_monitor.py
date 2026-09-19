import logging
from typing import Optional

import cocotb
from cocotb.triggers import ReadOnly


class BusMonitor():
	"""Logs *settled* transitions of one signal.

	The signal is sampled after ReadOnly, i.e. once per time step after every
	delta cycle has finished.  Values that only exist in the middle of a time
	step (combinational glitches, half-updated buses) are never seen, and
	several deltas' worth of changes collapse into one logged transition.

	Subclasses override _format() to change how a value is printed.
	"""

	def __init__(self, bus_sig, name: str = "bus_mon"):
		self.sig = bus_sig
		self.name = name

		# logger
		self.logger = logging.getLogger(self.name)
		self.logger.setLevel(logging.DEBUG)
		self._task: Optional[cocotb.Task] = None

	@property
	def value(self):
		"""LIVE value of the signal (a LogicArray/Logic).  Not cached.

		Only trust it at a settled point: after `await ReadOnly()`, or when
		sampled right after a clock edge (values from the previous cycle).
		"""
		return self.sig.value

	def value_is(self, val) -> bool:
		# was a @property, but a property can't take an argument
		return self.value == val

	def _format(self, value) -> str:
		return str(value)

	def start(self) -> None:
		if self._task is None or self._task.done():
			self._task = cocotb.start_soon(self._run())

	def stop(self) -> None:
		if self._task is not None and not self._task.done():
			self._task.cancel()      # Task.kill() is deprecated since cocotb 2.0
		self._task = None

	async def _run(self) -> None:
		prev = self.value
		while True:
			await self.sig.value_change
			await ReadOnly()         # let all delta cycles of this time step settle
			new = self.value

			if new != prev and prev.is_resolvable and new.is_resolvable:
				self.logger.info(f"transition '{self._format(prev)}' to '{self._format(new)}'")
			prev = new