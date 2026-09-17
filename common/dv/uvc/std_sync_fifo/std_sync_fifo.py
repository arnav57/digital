import cocotb, logging
from typing import Optional
from cocotb.triggers import Edge

from common.dv.uvc import ClockMonitor
from common.dv.uvc    import ResetMonitor
from common.dv.uvc import BitMonitor

class SyncFIFO():

	def __init__(self, dut, name:str="sync_fifo"):
		self._dut = dut
		self.name = name

		# monitors
		self.mon_acc_read  = BitMonitor(self._dut.actually_read, "fifo-read")
		self.mon_acc_write = BitMonitor(self._dut.actually_write, "fifo-write")
		self.mon_empty     = BitMonitor(self._dut.empty_o, "fifo-empty")
		self.mon_full      = BitMonitor(self._dut.full_o, "fifo-full")

		# logger
		self.logger = logging.getLogger(self.name)
		self.logger.setLevel(logging.DEBUG)

		# task and state
		self._task: Optional[cocotb.Task] = None
		self._fifo = []
	
	@property
	def size(self) -> int:
		return len(self._fifo)
	
	###### TASK CONTROL ######
	
	def start(self):
		self.logger.info("Starting monitors")
		self.mon_acc_read.start()  
		self.mon_acc_write.start() 
		self.mon_empty.start()     
		self.mon_full.start()      
		if self._task is None or self._task.done():
			self._task = cocotb.start_soon(self._run())
	
	def stop(self):
		self.mon_acc_read.stop()  
		self.mon_acc_write.stop() 
		self.mon_empty.stop()     
		self.mon_full.stop()      
		if self._task and not self._task.done():
			self._task.kill()
			self._task = None
		self.logger.info("Stopped monitors")

	async def _run(self) -> None:
		while True:
			# check if we read
			if (self.mon_acc_read.is_high):
				await Edge(self._dut.clk_i)
				await self.reading_from_fifo()
			# check if we write
			if (self.mon_acc_write.is_high):
				await self.write_to_fifo()
				await Edge(self._dut.clk_i)
			
	
	async def reading_from_fifo(self):
		expected_value = self._fifo.pop(0)
		actual_value   = self._dut.rd_data_o.value
		self.logger.info(f"fifo recieved a valid read of '{actual_value}', fifo size is now {self.size}")
		assert expected_value == actual_value, f"FIFO Read Value: '{actual_value}' does not match the expected value of '{expected_value}' !\n\n"
	
	async def write_to_fifo(self):
		wr_value = self._dut.wr_data_i.value
		self._fifo.append(wr_value)
		self.logger.info(f"fifo recieved a valid write with '{wr_value}', fifo size is now {self.size}")
	


