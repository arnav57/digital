import cocotb, logging

class CORDIC():

    def __init__(self, dut, name:str = "cordic"):
        self._dut = dut
        self.name = name

		# logger
		self.logger = logging.getLogger(self.name)
		self.logger.setLevel(logging.DEBUG)
    