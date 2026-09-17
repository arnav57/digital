import cocotb
from cocotb.logging import SimLog
from cocotb.triggers import Edge, Event
from typing import Optional
import logging


class BitMonitor:
	"""Passively tracks transitions and state on any 1-bit signal."""

	def __init__(self, signal, name: str = "bit_mon"):
		self.sig = signal
		self.name = name
		# logger
		self.logger = logging.getLogger(self.name)
		self.logger.setLevel(logging.DEBUG)
		self._task: Optional[cocotb.Task] = None

		# Event for test synchronization
		self.changed: Event = Event()

	@property
	def is_high(self) -> bool:
		"""Returns True if the signal is logic 1."""
		return self.sig.value == 1

	@property
	def is_low(self) -> bool:
		"""Returns True if the signal is logic 0."""
		return self.sig.value == 0

	def start(self) -> None:
		if self._task is None or self._task.done():
			self._task = cocotb.start_soon(self._run())

	def stop(self) -> None:
		if self._task and not self._task.done():
			self._task.kill()
			self._task = None

	async def _run(self) -> None:
		while True:
			await Edge(self.sig)
			# Wake up anyone waiting on a change
			self.changed.set()
			self.changed.clear()

			if self.is_high:
				self.logger.info("Transition -> HIGH (1)")
			elif self.is_low:
				self.logger.info("Transition -> LOW (0)")
			else:
				self.logger.warning("Transition -> UNKNOWN/X/Z (%s)", self.sig.value)

	async def wait_for_value(self, val: int) -> None:
		"""Helper to block until the signal matches the requested bit state."""
		target_str = str(val)
		while self.sig.value.binstr != target_str:
			await Edge(self.sig)