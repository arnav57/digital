import math

# ============================================================
# EASY-TO-CHANGE CORDIC CONSTANTS
# ============================================================

NUM_STAGES = 14
ANGLE_WIDTH = 16
VECTOR_WIDTH = 18

# 1 sign + 2 integer/magnitude bits + 15 fractional bits
FRAC_BITS = 15

INPUT_ANGLE_DEG = 30.0

INITIAL_X = 1.0 / 1.64676
INITIAL_Y = 0.0


# ============================================================
# BAR / FIXED-POINT HELPERS
# ============================================================

def deg_to_bar(deg, width=ANGLE_WIDTH):
    full_scale = 1 << width
    return round((deg / 360.0) * full_scale) % full_scale


def bar_to_deg(bar, width=ANGLE_WIDTH):
    full_scale = 1 << width
    return (bar / full_scale) * 360.0


def signed_bar(bar, width=ANGLE_WIDTH):
    sign_bit = 1 << (width - 1)
    if bar & sign_bit:
        return bar - (1 << width)
    return bar


def fixed_to_int(value, frac_bits=FRAC_BITS):
    return round(value * (1 << frac_bits))


def int_to_fixed(value, frac_bits=FRAC_BITS):
    return value / (1 << frac_bits)


def arithmetic_shift_right(value, shift):
    # Matches signed arithmetic >>> behavior.
    return value // (1 << shift)


# ============================================================
# ARCTAN LUT
# ============================================================

theta_lut = []

for i in range(NUM_STAGES):
    theta_rad = math.atan(2.0 ** (-i))
    theta_deg = math.degrees(theta_rad)
    theta_bar = deg_to_bar(theta_deg)
    theta_lut.append(theta_bar)


# ============================================================
# CORDIC
# ============================================================

def cordic(angle_deg):
    # Initial desired rotation angle in signed BAR
    z = signed_bar(deg_to_bar(angle_deg))

    # Initial vector in fixed point
    x = fixed_to_int(INITIAL_X)
    y = fixed_to_int(INITIAL_Y)

    print()
    print("CORDIC iterations")
    print("-" * 90)
    print(
        f"{'i':>2} | {'direction':>9} | {'theta (deg)':>12} | "
        f"{'z (deg)':>12} | {'x':>12} | {'y':>12}"
    )
    print("-" * 90)

    for i in range(NUM_STAGES):

        # Direction is determined by the sign of z
        if z < 0:
            direction = -1
        else:
            direction = +1

        theta = signed_bar(theta_lut[i])

        # Equivalent to your SV:
        # y_i >>> i
        # x_i >>> i
        y_shifted = arithmetic_shift_right(y, i)
        x_shifted = arithmetic_shift_right(x, i)

        # Your CORDIC equations
        x_next = x - direction * y_shifted
        y_next = y + direction * x_shifted
        z_next = z - direction * theta

        z_display = bar_to_deg(z & ((1 << ANGLE_WIDTH) - 1))
        if z_display >= 180.0:
            z_display -= 360.0

        print(
            f"{i:2d} | {direction:+9d} | "
            f"{bar_to_deg(theta_lut[i]):12.6f} | "
            f"{z_display:12.6f} | "
            f"{int_to_fixed(x):12.8f} | "
            f"{int_to_fixed(y):12.8f}"
        )

        x, y, z = x_next, y_next, z_next

    return int_to_fixed(x), int_to_fixed(y), z


# ============================================================
# TEST
# ============================================================

x_out, y_out, z_out = cordic(INPUT_ANGLE_DEG)

GAIN = 1.646760258

expected_cos = math.cos(math.radians(INPUT_ANGLE_DEG))
expected_sin = math.sin(math.radians(INPUT_ANGLE_DEG))

print()
print("=" * 60)
print("RESULT")
print("=" * 60)

print(f"Input angle           : {INPUT_ANGLE_DEG:.6f} degrees")
print(f"CORDIC x              : {x_out:.10f}")
print(f"CORDIC y              : {y_out:.10f}")
print(f"Expected cos          : {expected_cos:.10f}")
print(f"Expected sin          : {expected_sin:.10f}")
print()
print("With x0 = 1, y0 = 0, CORDIC gain is present:")
print(f"Expected gain-scaled x: {expected_cos * GAIN:.10f}")
print(f"Expected gain-scaled y: {expected_sin * GAIN:.10f}")
print()
print("Errors:")
print(
    f"x error: "
    f"{x_out - expected_cos * GAIN:+.10e}"
)
print(
    f"y error: "
    f"{y_out - expected_sin * GAIN:+.10e}"
)
