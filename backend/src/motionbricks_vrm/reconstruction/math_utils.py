"""Mathematical foundations and geometry utilities for MotionBricks-to-VRM integration.

Provides pure-Python/NumPy transformations for:
- Continuous 6D rotations (Zhou et al., CVPR 2019) to rotation matrices
- Rotation matrix to unit quaternion [x, y, z, w]
- Quaternion multiplication, conjugate, and rotation of 3D vectors
- Coordinate frame transformations (MotionBricks <-> Canonical glTF/VRM <-> MuJoCo)
- Forward kinematics and relative local transform recovery
"""

from __future__ import annotations

import math
from typing import List, Tuple, Union
import numpy as np


def normalize_quaternion(q: Union[List[float], np.ndarray]) -> np.ndarray:
    """Normalize a quaternion [x, y, z, w] to unit length.
    
    If the norm is near zero, returns the identity quaternion [0, 0, 0, 1].
    """
    q_arr = np.asarray(q, dtype=np.float64)
    norm = np.linalg.norm(q_arr)
    if norm < 1e-12:
        return np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float64)
    return q_arr / norm


def cont6d_to_matrix(c6d: Union[List[float], np.ndarray]) -> np.ndarray:
    """Convert continuous 6D rotation representation to a 3x3 rotation matrix.
    
    Uses Gram-Schmidt orthogonalization (Zhou et al., CVPR 2019).
    c6d shape: (..., 6) where [a1(3), a2(3)]
    Returns: (..., 3, 3) rotation matrix
    """
    arr = np.asarray(c6d, dtype=np.float64)
    orig_shape = arr.shape[:-1]
    flat = arr.reshape(-1, 6)

    x_raw = flat[:, 0:3]
    y_raw = flat[:, 3:6]

    x_norm = np.linalg.norm(x_raw, axis=-1, keepdims=True)
    x = x_raw / np.maximum(x_norm, 1e-12)

    dot = np.sum(x * y_raw, axis=-1, keepdims=True)
    y_proj = y_raw - dot * x
    y_norm = np.linalg.norm(y_proj, axis=-1, keepdims=True)
    y = y_proj / np.maximum(y_norm, 1e-12)

    z = np.cross(x, y)

    # Columns of rotation matrix: [x, y, z]
    rot_mat = np.stack([x, y, z], axis=-1)
    return rot_mat.reshape(orig_shape + (3, 3))


def matrix_to_quaternion_xyzw(matrix: Union[List[List[float]], np.ndarray]) -> np.ndarray:
    """Convert 3x3 rotation matrix to unit quaternion [x, y, z, w].
    
    Uses Shepperd's numerically stable algorithm.
    """
    m = np.asarray(matrix, dtype=np.float64)
    orig_shape = m.shape[:-2]
    flat_m = m.reshape(-1, 3, 3)
    num_mats = flat_m.shape[0]

    quats = np.zeros((num_mats, 4), dtype=np.float64)

    for i in range(num_mats):
        mat = flat_m[i]
        trace = mat[0, 0] + mat[1, 1] + mat[2, 2]

        if trace > 0.0:
            s = 0.5 / math.sqrt(trace + 1.0)
            w = 0.25 / s
            x = (mat[2, 1] - mat[1, 2]) * s
            y = (mat[0, 2] - mat[2, 0]) * s
            z = (mat[1, 0] - mat[0, 1]) * s
        elif mat[0, 0] > mat[1, 1] and mat[0, 0] > mat[2, 2]:
            s = 2.0 * math.sqrt(1.0 + mat[0, 0] - mat[1, 1] - mat[2, 2])
            w = (mat[2, 1] - mat[1, 2]) / s
            x = 0.25 * s
            y = (mat[0, 1] + mat[1, 0]) / s
            z = (mat[0, 2] + mat[2, 0]) / s
        elif mat[1, 1] > mat[2, 2]:
            s = 2.0 * math.sqrt(1.0 + mat[1, 1] - mat[0, 0] - mat[2, 2])
            w = (mat[0, 2] - mat[2, 0]) / s
            x = (mat[0, 1] + mat[1, 0]) / s
            y = 0.25 * s
            z = (mat[1, 2] + mat[2, 1]) / s
        else:
            s = 2.0 * math.sqrt(1.0 + mat[2, 2] - mat[0, 0] - mat[1, 1])
            w = (mat[1, 0] - mat[0, 1]) / s
            x = (mat[0, 2] + mat[2, 0]) / s
            y = (mat[1, 2] + mat[2, 1]) / s
            z = 0.25 * s

        q = np.array([x, y, z, w], dtype=np.float64)
        quats[i] = normalize_quaternion(q)

    return quats.reshape(orig_shape + (4,))


def quaternion_xyzw_to_matrix(q: Union[List[float], np.ndarray]) -> np.ndarray:
    """Convert unit quaternion [x, y, z, w] to 3x3 rotation matrix."""
    q_norm = normalize_quaternion(q)
    x, y, z, w = q_norm

    xx = x * x
    yy = y * y
    zz = z * z
    xy = x * y
    xz = x * z
    yz = y * z
    wx = w * x
    wy = w * y
    wz = w * z

    return np.array([
        [1.0 - 2.0 * (yy + zz), 2.0 * (xy - wz), 2.0 * (xz + wy)],
        [2.0 * (xy + wz), 1.0 - 2.0 * (xx + zz), 2.0 * (yz - wx)],
        [2.0 * (xz - wy), 2.0 * (yz + wx), 1.0 - 2.0 * (xx + yy)]
    ], dtype=np.float64)


def quaternion_multiply(q1: Union[List[float], np.ndarray], q2: Union[List[float], np.ndarray]) -> np.ndarray:
    """Hamilton product of two quaternions q1 and q2 in [x, y, z, w] format.
    
    Computes q = q1 * q2, representing rotation q2 followed by rotation q1.
    """
    x1, y1, z1, w1 = np.asarray(q1, dtype=np.float64)
    x2, y2, z2, w2 = np.asarray(q2, dtype=np.float64)

    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
    z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2

    return normalize_quaternion([x, y, z, w])


def quaternion_conjugate(q: Union[List[float], np.ndarray]) -> np.ndarray:
    """Inverse/conjugate of a unit quaternion [x, y, z, w]."""
    x, y, z, w = np.asarray(q, dtype=np.float64)
    return np.array([-x, -y, -z, w], dtype=np.float64)


def rotate_vector(q: Union[List[float], np.ndarray], v: Union[List[float], np.ndarray]) -> np.ndarray:
    """Rotate a 3D vector v by quaternion q [x, y, z, w]."""
    mat = quaternion_xyzw_to_matrix(q)
    return mat @ np.asarray(v, dtype=np.float64)


# Coordinate System Transformations
# MotionBricks Space: +X Right, +Y Up, +Z Forward (Right-handed)
# Canonical glTF/VRM Space: +X Right, +Y Up, -Z Forward (Right-handed)
#
# Transformation: 180 degrees around Y-axis (facing direction flip from +Z to -Z).
R_Y_180 = np.array([
    [-1.0,  0.0,  0.0],
    [ 0.0,  1.0,  0.0],
    [ 0.0,  0.0, -1.0]
], dtype=np.float64)

Q_Y_180 = np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float64)  # [x, y, z, w] for 180 deg around Y


def motionbricks_pos_to_canonical(pos: Union[List[float], np.ndarray]) -> np.ndarray:
    """Convert 3D position from MotionBricks space (+Z forward) to Canonical space (-Z forward)."""
    p = np.asarray(pos, dtype=np.float64)
    return R_Y_180 @ p


def canonical_pos_to_motionbricks(pos: Union[List[float], np.ndarray]) -> np.ndarray:
    """Convert 3D position from Canonical space to MotionBricks space."""
    p = np.asarray(pos, dtype=np.float64)
    return R_Y_180 @ p  # Involutive (R_Y_180^T = R_Y_180)


def motionbricks_rot_to_canonical(rot_mat: np.ndarray) -> np.ndarray:
    """Convert 3x3 rotation matrix from MotionBricks space to Canonical space.
    
    R_canonical = R_Y_180 * R_motion * R_Y_180^T
    """
    return R_Y_180 @ rot_mat @ R_Y_180.T


def motionbricks_quat_to_canonical(q_xyzw: Union[List[float], np.ndarray]) -> np.ndarray:
    """Convert quaternion from MotionBricks space to Canonical space."""
    mat = quaternion_xyzw_to_matrix(q_xyzw)
    mat_can = motionbricks_rot_to_canonical(mat)
    return matrix_to_quaternion_xyzw(mat_can)


def euler_to_matrix(roll_x: float, pitch_y: float, yaw_z: float) -> np.ndarray:
    """Construct rotation matrix from XYZ Euler angles in radians."""
    cx, sx = math.cos(roll_x), math.sin(roll_x)
    cy, sy = math.cos(pitch_y), math.sin(pitch_y)
    cz, sz = math.cos(yaw_z), math.sin(yaw_z)

    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]], dtype=np.float64)
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=np.float64)
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]], dtype=np.float64)

    return rz @ ry @ rx
