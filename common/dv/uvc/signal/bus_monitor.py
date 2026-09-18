import cocotb, logging

class BusMonitor():

	def __init__(self, bus_sig, name:str="bus_mon"):
		self.sig = bus_sig
		self.name = name
		
		# logger
		self.logger = logging.getLogger(self.name)
		self.logger.setLevel(logging.DEBUG)
		self._task: Optional[cocotb.Task] = None
	
	@property
	def value(self) -> int:
		return self.sig.value

	@property
	def value_is(self, val) -> bool:
		return self.value == val
	
	def start(self) -> None:
		if self._task is None or self._task.done():
			self._task = cocotb.start_soon(self._run())

	def stop(self) -> None:
		if self._task and not self._task.done():
			self._task.kill()
			self._task = None

	async def _run(self) -> None:
		while True:
			curr_val = self.value
			await self.sig.value_change
			new_val  = self.value

			if curr_val.is_resolvable and new_val.is_resolvable:
				self.logger.info(f"transition '{curr_val}' to '{new_val}'")

