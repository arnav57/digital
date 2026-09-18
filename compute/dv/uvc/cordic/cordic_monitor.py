from common.dv.uvc import BusMonitor
import math

class CordicVectorMonitor(BusMonitor):

	def __init__(self, sig, name:str = "cordic-vec"):
		super().__init__(sig, name)
	
	def _to_decimal(self, raw_value: int, fractional_bits: int = 15, total_bits: int = 18) -> float:
		# Handle two's complement signed integer if a fixed bit-width is specified
		raw_value = int(raw_value)
		if total_bits is not None:
			sign_bit = 1 << (total_bits - 1)
			if raw_value & sign_bit:
				raw_value -= (1 << total_bits)
				
		# Convert Q-format to decimal
		return raw_value / (2 ** fractional_bits)
	
	@property
	def decimal_value(self) -> float:
		return self._to_decimal(self.sig.value)

	
	async def _run(self) -> None:
		while True:
			curr_val = self.value
			await self.sig.value_change
			new_val  = self.value

			if curr_val.is_resolvable and new_val.is_resolvable:
				self.logger.info(f"transition '{self._to_decimal(curr_val)}' to '{self._to_decimal(new_val)}'")

class CordicAngleMonitor(BusMonitor):

	def __init__(self, sig, name:str = "cordic-ang"):
		super().__init__(sig, name)
	
	def _to_degrees(self, raw_value: int, num_bits: int = 16) -> float:
		raw_value = int(raw_value)

		sign_bit = 1 << (num_bits - 1)
		if raw_value & sign_bit:
			raw_value -= 1 << num_bits

		return raw_value * 360.0 / (2 ** num_bits)
	
	@property
	def angle_value(self) -> float:
		return self._to_degrees(self.sig.value)

	async def _run(self) -> None:
		while True:
			curr_val = self.value
			await self.sig.value_change
			new_val  = self.value

			if curr_val.is_resolvable and new_val.is_resolvable:
				self.logger.info(f"transition '{self._to_degrees(curr_val)}' to '{self._to_degrees(new_val)}'")

