"""Unit tests for motion mathematics, quaternion continuity, and forward kinematics."""

import numpy as np
import pytest

from ardy_vrm_demo.motion_adapter.core_skeleton import (
    REST_JOINTS_CORE,
    compute_offsets,
    forward_kinematics,
)
from ardy_vrm_demo.motion_adapter.vrm_retargeter import (
    ensure_quaternion_continuity,
    matrix_to_quaternion_xyzw,
)


def test_identity_matrix_to_quaternion():
    """Identity 3x3 rotation matrix must map to [0, 0, 0, 1]."""
    eye = np.eye(3)[np.newaxis, np.newaxis, ...]  # (1, 1, 3, 3)
    quat = matrix_to_quaternion_xyzw(eye)[0, 0]
    expected = np.array([0.0, 0.0, 0.0, 1.0])
    np.testing.assert_allclose(quat, expected, atol=1e-6)
    assert np.isclose(np.linalg.norm(quat), 1.0)


def test_quaternion_normalization():
    """All converted quaternions must strictly have unit Euclidean norm."""
    # Generate random orthogonal rotation matrices using QR decomposition
    np.random.seed(42)
    random_matrices = []
    for _ in range(10):
        H = np.random.randn(3, 3)
        Q, R = np.linalg.qr(H)
        d = np.diagonal(R)
        ph = d / np.abs(d)
        Q = Q * ph
        if np.linalg.det(Q) < 0:
            Q[:, 0] = -Q[:, 0]
        random_matrices.append(Q)

    mats = np.array(random_matrices)[:, np.newaxis, ...]  # (10, 1, 3, 3)
    quats = matrix_to_quaternion_xyzw(mats)
    norms = np.linalg.norm(quats, axis=-1)
    np.testing.assert_allclose(norms, 1.0, atol=1e-6)


def test_quaternion_continuity_flip():
    """Continuity check must flip opposite-sign quaternions representing identical rotations."""
    # q and -q represent the exact same rotation, but flipping causes slerp discontinuity
    q1 = np.array([0.0, 0.0, 0.0, 1.0])
    q2 = np.array([0.0, 0.0, 0.0, -1.0])
    raw = np.array([[q1], [q2]])  # (T=2, J=1, 4)

    continuous = ensure_quaternion_continuity(raw)
    dot = np.sum(continuous[0, 0] * continuous[1, 0])
    assert dot > 0.9999, f"Dot product should be positive after continuity pass: {dot}"


def test_rest_pose_forward_kinematics():
    """Forward kinematics with identity rotations and zero root translation must reproduce rest-pose offsets."""
    T, J = 1, 27
    identity_rot = np.tile(np.eye(3), (T, J, 1, 1))
    zero_root = np.zeros((T, 3))

    fk_pos, _ = forward_kinematics(identity_rot, zero_root)
    # Joints should match canonical REST_JOINTS_CORE within floating-point tolerance
    np.testing.assert_allclose(fk_pos[0], REST_JOINTS_CORE, atol=1e-5)
