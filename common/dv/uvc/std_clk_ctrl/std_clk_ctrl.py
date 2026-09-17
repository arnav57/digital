import cocotb, logging

from common.dv.uvc import ClockMonitor
from common.dv.uvc import ResetMonitor
from common.dv.uvc import BitMonitor

class ClockControl():

	def __init__(self, dut, name:str=None):
		self._dut  = dut
		self.name = "CLOCK-CONTROL" if name is None else name 

		# monitors
		self.mon_clk_out    = ClockMonitor(self.clock_out, "clk-out")
		self.mon_fr_clk_out = ClockMonitor(self.clock_out_fr, "fr-clk-out")
		self.mon_reset_in   = ResetMonitor(self.reset_in, "rstn-in")
		self.mon_reset_out  = ResetMonitor(self.reset_out, "rstn-out")
		self.mon_clk_en     = BitMonitor(self.clock_en, 'clk-en')

		# logger
		self.logger = logging.getLogger(self.name)
		self.logger.setLevel(logging.DEBUG)

	### DIRECT PIN ACCESS ###

	@property
	def clock_in(self):
		return self._dut.clk_i

	@property
	def reset_in(self):
		return self._dut.rstn_i

	@property
	def clock_div(self):
		return self._dut.clk_div_i
	
	@property
	def clock_en(self):
		return self._dut.clk_en_i

	@property
	def clock_out(self):
		return self._dut.clk_o

	@property
	def clock_out_fr(self):
		return self._dut.clk_fr_o

	@property
	def reset_out(self):
		return self._dut.rstn_o

	### INTERNAL STATE ###

	@property
	def in_reset(self) -> bool:
		return self.mon_reset_in.is_asserted

	@property
	def is_gated(self) -> bool:
		return self.mon_clk_en.is_low

	### ACTIVITY CONTROL ###

	def start(self):
		self.mon_clk_out.start()   
		self.mon_fr_clk_out.start()
		self.mon_reset_in.start()  
		self.mon_reset_out.start() 
		self.mon_clk_en.start()
		self.logger.info("started monitors")

	def stop(self):
		self.mon_clk_out.stop()   
		self.mon_fr_clk_out.stop()
		self.mon_reset_in.stop()  
		self.mon_reset_out.stop() 
		self.mon_clk_en.stop()  
		self.logger.info("stopped monitors")

	def initialize(self):
		self.clock_in.value  = 0
		self.reset_in.value  = 1
		self.clock_div.value = 0
		self.clock_en.value  = 0

	