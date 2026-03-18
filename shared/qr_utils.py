"""
QR code utility functions.

Calculates optimal QR version and box size based on data length.
"""

from __future__ import annotations

import qrcode.constants

# Maximum data capacity per version (1–16) for each error correction level.
# Rows keyed by the qrcode library's constant values:
#   ERROR_CORRECT_M=0, ERROR_CORRECT_L=1, ERROR_CORRECT_H=2, ERROR_CORRECT_Q=3
_MAX_CAPACITY = {
    qrcode.constants.ERROR_CORRECT_L: [
        41,
        77,
        127,
        187,
        255,
        322,
        370,
        461,
        552,
        652,
        772,
        883,
        1022,
        1101,
        1250,
        1408,
    ],
    qrcode.constants.ERROR_CORRECT_M: [
        34,
        63,
        101,
        149,
        202,
        255,
        293,
        365,
        432,
        513,
        604,
        691,
        796,
        871,
        991,
        1082,
    ],
    qrcode.constants.ERROR_CORRECT_Q: [
        27,
        48,
        77,
        111,
        144,
        178,
        206,
        258,
        308,
        370,
        438,
        506,
        586,
        644,
        718,
        808,
    ],
    qrcode.constants.ERROR_CORRECT_H: [
        17,
        34,
        58,
        82,
        106,
        139,
        154,
        202,
        235,
        288,
        331,
        374,
        427,
        468,
        530,
        602,
    ],
}


def suggest_qr_version(
    data: str,
    error_correction: int = qrcode.constants.ERROR_CORRECT_L,
) -> int:
    """Return the minimum QR version that can accommodate the data length."""
    capacities = _MAX_CAPACITY.get(
        error_correction, _MAX_CAPACITY[qrcode.constants.ERROR_CORRECT_L]
    )
    for version_idx, cap in enumerate(capacities):
        if len(data) <= cap:
            return version_idx + 1
    return len(capacities)


def suggest_box_size(data: str) -> int:
    """Return a recommended box size based on data length."""
    return max(len(data) // 50, 10)
