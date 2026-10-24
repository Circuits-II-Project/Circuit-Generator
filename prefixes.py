import math
import re

#----------------------------------------------------------------------------------
# ENGINEERING PREFIXES
#----------------------------------------------------------------------------------

# Multiplier for each prefix (same prefixes as ENGINEERING_PREFIXES in input_validation.py)
# Prefixes are case-sensitive: m = milli, M = mega. Micro is written as u.
PREFIXES = {
    "T": 1e12,
    "G": 1e9,
    "M": 1e6,
    "k": 1e3,
    "": 1,
    "m": 1e-3,
    "u": 1e-6,
    "n": 1e-9,
    "p": 1e-12,
}

# Power of 10 (multiple of 3) for each prefix, used when printing results
EXPONENT_TO_PREFIX = {
    12: "T",
    9: "G",
    6: "M",
    3: "k",
    0: "",
    -3: "m",
    -6: "u",
    -9: "n",
    -12: "p",
}

# A number, an optional prefix and an optional unit. Examples: "4.7k", "10 mH", "5F", "2e3"
VALUE_PATTERN = re.compile(
    r"^\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*([pnumkMGT]?)\s*([A-Za-z]*)\s*$"
)

# Function for converting a value with prefix into its decimal equivalent
# Example: "4.7k" --> 4700.0
def from_prefix(text):
    match = VALUE_PATTERN.match(text)

    if match is None:
        raise ValueError(f"Invalid value: {text!r}")

    # The unit is accepted so the user can type it, but it does not change the value
    number, prefix, _unit = match.groups()

    return float(number) * PREFIXES[prefix]

# Function for rounding a value and giving it the correct prefix
# Example: 0.000047 with unit "F" --> "47.00 uF"
def to_prefix(value, unit="", decimals=2):
    if value == 0:
        return f"{0:.{decimals}f} {unit}"

    # Find the power of 10 that is a multiple of 3 (engineering notation)
    exponent = math.floor(math.log10(abs(value)) / 3) * 3

    # Stay inside the supported prefixes (p to T)
    exponent = max(-12, min(12, exponent))

    scaled = round(value / 10**exponent, decimals)

    # Rounding can turn 999.999 into 1000.00, so move up to the next prefix
    if abs(scaled) >= 1000 and exponent < 12:
        exponent += 3
        scaled = round(value / 10**exponent, decimals)

    return f"{scaled:.{decimals}f} {EXPONENT_TO_PREFIX[exponent]}{unit}"
