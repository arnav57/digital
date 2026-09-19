from common.dv.uvc import BusMonitor


class CordicVectorMonitor(BusMonitor):
	"""Signed fixed-point vector (default Q3.15 in an 18 bit bus)."""

	def __init__(self, sig, name: str = "cordic-vec", fractional_bits: int = 15):
		super().__init__(sig, name)
		self.fractional_bits = fractional_bits

	def to_decimal(self, value) -> float:
		# bus width comes from the value itself, no hard-coded 18
		return value.to_signed() / (2 ** self.fractional_bits)

	@property
	def decimal_value(self) -> float:
		return self.to_decimal(self.value)

	def _format(self, value) -> str:
		return str(self.to_decimal(value))


class CordicAngleMonitor(BusMonitor):
	"""Signed BAR angle (2**width == 360 degrees)."""

	def __init__(self, sig, name: str = "cordic-ang"):
		super().__init__(sig, name)

	def to_degrees(self, value) -> float:
		return value.to_signed() * 360.0 / (2 ** len(value))

	@property
	def angle_value(self) -> float:
		return self.to_degrees(self.value)

	def _format(self, value) -> str:
		return str(self.to_degrees(value))