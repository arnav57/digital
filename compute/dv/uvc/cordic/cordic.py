import cocotb, logging
from common.dv.uvc import BusMonitor

from cocotb.triggers import RisingEdge
from .cordic_monitor import CordicAngleMonitor, CordicVectorMonitor

class CORDIC():

	def __init__(self, dut, name:str = "cordic"):
		self._dut = dut
		self.name = name

		# logger
		self.logger = logging.getLogger(self.name)
		self.logger.setLevel(logging.DEBUG)

		# output monitors
		self.x_out_mon = CordicVectorMonitor(self._dut.x_o, "x_out")
		self.y_out_mon = CordicVectorMonitor(self._dut.y_o, "y_out")
		self.z_out_mon = CordicAngleMonitor(self._dut.z_o, "angle_error_out")
		# task and state
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
		if self._task and not self._task.done():
			self._task.kill()
			self._task = None
		self.logger.info("Stopped task")

	async def _run(self) -> None:
		while True:
			x_out = self._dut.x_o.value
			y_out = self._dut.y_o.value
			z_out = self._dut.z_o.value

			await RisingEdge(self._dut.clk_i)



		
		