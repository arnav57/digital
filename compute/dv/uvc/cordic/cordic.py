import logging
from dataclasses import dataclass
from typing import Optional

import cocotb
from cocotb.queue import Queue
from cocotb.triggers import RisingEdge

from .cordic_monitor import CordicAngleMonitor, CordicVectorMonitor


@dataclass(frozen=True)
class CordicResult:
	"""One coherent output sample (x, y, z all from the same cycle)."""
	x: float        # Q3.15 -> float (still includes the CORDIC gain)
	y: float
	z_deg: float    # residual angle error in degrees
	z_lsb: int      # residual angle error in BAR LSBs


class CORDIC():

	def __init__(self, dut, name: str = "cordic"):
		self._dut = dut
		self.name = name

		# logger
		self.logger = logging.getLogger(self.name)
		self.logger.setLevel(logging.DEBUG)

		# output monitors (logging / debug only)
		self.x_out_mon = CordicVectorMonitor(self._dut.x_o, "x_out")
		self.y_out_mon = CordicVectorMonitor(self._dut.y_o, "y_out")
		self.z_out_mon = CordicAngleMonitor(self._dut.z_o, "angle_error_out")

		# coherent results, one per cycle that valid_o is high
		self._results: Queue = Queue()
		self._task: Optional[cocotb.Task] = None

	###### TASK CONTROL ######

	def start(self):
		self.logger.info("Starting task")
		self.x_out_mon.start()
		self.y_out_mon.start()
		self.z_out_mon.start()
		if self._task is None or self._task.done():
			self._task = cocotb.start_soon(self._run())

	def stop(self):
		self.x_out_mon.stop()
		self.y_out_mon.stop()
		self.z_out_mon.stop()
		if self._task is not None and not self._task.done():
			self._task.cancel()
		self._task = None
		self.logger.info("Stopped task")

	###### RESULTS ######

	async def get_result(self) -> CordicResult:
		"""Wait for the next valid output sample."""
		return await self._results.get()

	async def _run(self) -> None:
		dut = self._dut
		while True:
			await RisingEdge(dut.clk_i)
			# Values read right after a clock edge are the settled values of the
			# previous cycle, so valid/x/y/z are consistent with each other even
			# though x/y come out of combinational logic (cordic_transform).
			if dut.valid_o.value != 1:
				continue
			x, y, z = dut.x_o.value, dut.y_o.value, dut.z_o.value
			if not (x.is_resolvable and y.is_resolvable and z.is_resolvable):
				self.logger.warning(f"valid_o is high but outputs have X/Z: x={x} y={y} z={z}")
				continue
			self._results.put_nowait(CordicResult(
				x=self.x_out_mon.to_decimal(x),
				y=self.y_out_mon.to_decimal(y),
				z_deg=self.z_out_mon.to_degrees(z),
				z_lsb=z.to_signed(),
			))