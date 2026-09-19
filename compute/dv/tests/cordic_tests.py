import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random, math, logging

from common.dv.uvc import ClockMonitor, ResetMonitor
from compute.dv.uvc import CORDIC

@cocotb.test()
async def cordic_base_test(dut):

	# TESTCASE SETUP
	cordic  = CORDIC(dut, "cordic")
	clk = Clock(dut.clk_i, 10, unit="ns")
	clk_mon = ClockMonitor(dut.clk_i, "cordic-clk")
	rst_mon = ResetMonitor(dut.rstn_i, "cordic-rstn")

	logger = logging.getLogger("cordic-base-test")
	logger.setLevel(logging.DEBUG)

	cordic.start()
	clk_mon.start()
	rst_mon.start()
	cocotb.start_soon(clk.start())

	# # choose a random input on z [-90 to 90 deg]
	# z_value = random.randint(-16384, 16384)
	z_value = random.randrange(65536)
	z_degrees = z_value * (360.0 / 65536.0)

	actual_sin = math.sin(math.radians(z_degrees))
	actual_cos = math.cos(math.radians(z_degrees))

	K = 1.64676 # CORDIC gain
	scaled_sin = K * actual_sin
	scaled_cos = K * actual_cos
	
	logger.info(f"chose value: '{z_value}' = '{z_degrees} deg'")
	logger.info(f"Actual sin: '{actual_sin}'")
	logger.info(f"Actual cos: '{actual_cos}'")
	logger.info(f"Expecting sin: '{scaled_sin}'")
	logger.info(f"Expecting cos: '{scaled_cos}'")

	# SEQUENCE

	dut.rstn_i.value = 0
	dut.en_i.value   = 0
	dut.x_i.value = 32768
	dut.y_i.value = 0
	dut.z_i.value = z_value

	await Timer(30, unit="ns")
	await RisingEdge(dut.clk_i)

	dut.rstn_i.value = 1
	dut.en_i.value   = 1

	await RisingEdge(dut.clk_i)
	dut.en_i.value = 0


	result = await cordic.get_result()
	err_sin = scaled_sin - result.y
	err_cos = scaled_cos - result.x
	ang_err = result.z_deg

	deg_per_lsb = 360.0 / 65536.0
	ang_err_lsb = ang_err / (deg_per_lsb)

	logger.info(f"Error (sin) = {err_sin}")
	logger.info(f"Error (cos) = {err_cos}")
	logger.info(f"Error (deg) = {ang_err} ({ang_err_lsb} LSb)")

	await RisingEdge(dut.clk_i)
	await RisingEdge(dut.clk_i)
	await RisingEdge(dut.clk_i)