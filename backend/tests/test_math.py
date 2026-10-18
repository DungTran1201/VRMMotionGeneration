"""Unit tests for geometry, math, coordinate conversions, and 6D rotations."""

import math
import numpy as np
import pytest

from motionbricks_vrm.reconstruction.math_utils import (
    canonical_pos_to_motionbricks,
    cont6d_to_matrix,
    euler_to_matrix,
    matrix_to_quaternion_xyzw,
    motionbricks_pos_to_canonical,
    motionbricks_quat_to_canonical,
    motionbricks_rot_to_canonical,
    normalize_quaternion,
    quaternion_conjugate,
    quaternion_multiply,
    quaternion_xyzw_to_matrix,
    rotate_vector,
)


def test_quaternion_normalization():
    q = np.array([3.0, 0.0, 4.0, 0.0])
    norm_q = normalize_quaternion(q)
    assert np.isclose(np.linalg.norm(norm_q), 1.0)
    assert np.allclose(norm_q, [0.6, 0.0, 0.8, 0.0])

    zero_q = normalize_quaternion([0.0, 0.0, 0.0, 0.0])
    assert np.allclose(zero_q, [0.0, 0.0, 0.0, 1.0])


def test_cont6d_to_matrix():
    # Identity orientation: x-axis = [1, 0, 0], y-axis = [0, 1, 0]
    c6d_ident = np.array([1.0, 0.0, 0.0, 0.0, 1.0, 0.0])
    mat_ident = cont6d_to_matrix(c6d_ident)
    assert np.allclose(mat_ident, np.eye(3), atol=1e-6)

    # 90 deg around Z: x-axis becomes [0, 1, 0], y-axis becomes [-1, 0, 0]
    c6d_z90 = np.array([0.0, 1.0, 0.0, -1.0, 0.0, 0.0])
    mat_z90 = cont6d_to_matrix(c6d_z90)
    expected_z90 = np.array([
        [0.0, -1.0, 0.0],
        [1.0,  0.0, 0.0],
        [0.0,  0.0, 1.0]
    ])
    assert np.allclose(mat_z90, expected_z90, atol=1e-6)


def test_matrix_quaternion_roundtrip():
    # Random orthogonal matrices via euler angles
    angles = [(0.1, 0.2, 0.3), (-0.5, 0.4, 0.8), (math.pi / 2, 0.0, -math.pi / 4)]
    for rx, ry, rz in angles:
        mat_orig = euler_to_matrix(rx, ry, rz)
        quat = matrix_to_quaternion_xyzw(mat_orig)
        assert np.isclose(np.linalg.norm(quat), 1.0)

        mat_rec = quaternion_xyzw_to_matrix(quat)
        assert np.allclose(mat_orig, mat_rec, atol=1e-5)


def test_quaternion_multiplication_and_conjugate():
    # Rotate 90 deg around X, then 90 deg around Y
    qx = np.array([math.sin(math.pi / 4), 0.0, 0.0, math.cos(math.pi / 4)])
    qy = np.array([0.0, math.sin(math.pi / 4), 0.0, math.cos(math.pi / 4)])

    q_combined = quaternion_multiply(qy, qx)
    assert np.isclose(np.linalg.norm(q_combined), 1.0)

    # Conjugate product q * q_inv = identity
    q_inv = quaternion_conjugate(q_combined)
    q_ident = quaternion_multiply(q_combined, q_inv)
    assert np.allclose(q_ident, [0.0, 0.0, 0.0, 1.0], atol=1e-6)


def test_coordinate_conversion_position():
    # In MotionBricks space: +Z is forward, +Y is up, +X is right
    # In Canonical space: -Z is forward, +Y is up, +X is right
    pos_motion = np.array([1.5, 2.0, 3.0])
    pos_can = motionbricks_pos_to_canonical(pos_motion)

    # Conversion is 180 deg around Y: x' = -x, y' = y, z' = -z
    assert np.allclose(pos_can, [-1.5, 2.0, -3.0], atol=1e-6)

    # Roundtrip check
    pos_back = canonical_pos_to_motionbricks(pos_can)
    assert np.allclose(pos_back, pos_motion, atol=1e-6)


def test_coordinate_conversion_rotation():
    # Identity rotation remains identity under conversion
    ident = np.eye(3)
    can_ident = motionbricks_rot_to_canonical(ident)
    assert np.allclose(can_ident, ident, atol=1e-6)

    # Forward direction vector (+Z in motion space) rotated to (-Z in canonical space)
    v_fwd_motion = np.array([0.0, 0.0, 1.0])
    v_fwd_can = motionbricks_pos_to_canonical(v_fwd_motion)
    assert np.allclose(v_fwd_can, [0.0, 0.0, -1.0], atol=1e-6)
