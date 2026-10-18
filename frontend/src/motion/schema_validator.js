/**
 * In-browser Schema Validator for CanonicalHumanoidMotion/v1.
 */

export const REQUIRED_HUMANOID_BONES = [
  'hips',
  'spine',
  'leftUpperLeg',
  'leftLowerLeg',
  'leftFoot',
  'rightUpperLeg',
  'rightLowerLeg',
  'rightFoot'
];

export const ALL_STANDARD_BONES = [
  'hips',
  'spine',
  'chest',
  'upperChest',
  'neck',
  'head',
  'leftShoulder',
  'leftUpperArm',
  'leftLowerArm',
  'leftHand',
  'rightShoulder',
  'rightUpperArm',
  'rightLowerArm',
  'rightHand',
  'leftUpperLeg',
  'leftLowerLeg',
  'leftFoot',
  'leftToes',
  'rightUpperLeg',
  'rightLowerLeg',
  'rightFoot',
  'rightToes'
];

export function validateCanonicalMotion(data) {
  const errors = [];

  if (!data || typeof data !== 'object') {
    return { valid: false, errors: ['Root motion document must be an object'] };
  }

  if (data.schema !== 'CanonicalHumanoidMotion/v1') {
    errors.push(`Unsupported schema '${data.schema}'. Expected 'CanonicalHumanoidMotion/v1'`);
  }

  const meta = data.metadata;
  if (!meta || typeof meta !== 'object') {
    errors.push('Missing required metadata object');
  } else {
    if (typeof meta.fps !== 'number' || meta.fps <= 0) {
      errors.push(`Invalid metadata.fps: ${meta.fps}`);
    }
    if (typeof meta.num_frames !== 'number' || meta.num_frames <= 0) {
      errors.push(`Invalid metadata.num_frames: ${meta.num_frames}`);
    }
  }

  const frames = data.frames;
  if (!Array.isArray(frames) || frames.length === 0) {
    errors.push('Frames must be a non-empty array');
    return { valid: false, errors };
  }

  if (meta && meta.num_frames && frames.length !== meta.num_frames) {
    errors.push(`Frame count mismatch: metadata specifies ${meta.num_frames}, frames list has ${frames.length}`);
  }

  // Validate frame 0 and sample check
  let prevTimestamp = -1e-9;
  for (let i = 0; i < frames.length; i++) {
    const frame = frames[i];
    if (typeof frame.timestamp !== 'number' || Number.isNaN(frame.timestamp)) {
      errors.push(`Frame ${i} has invalid timestamp`);
      break;
    }
    if (frame.timestamp < prevTimestamp) {
      errors.push(`Non-monotonic timestamp at frame ${i}: ${frame.timestamp} < ${prevTimestamp}`);
      break;
    }
    prevTimestamp = frame.timestamp;

    if (!frame.root || !Array.isArray(frame.root.position) || !Array.isArray(frame.root.rotation)) {
      errors.push(`Frame ${i} missing root position or rotation`);
      break;
    }

    // Verify quaternion length
    const q = frame.root.rotation;
    if (q.length !== 4) {
      errors.push(`Frame ${i} root rotation has length ${q.length}, expected 4`);
      break;
    }
    const qNorm = Math.sqrt(q[0]*q[0] + q[1]*q[1] + q[2]*q[2] + q[3]*q[3]);
    if (Math.abs(qNorm - 1.0) > 0.05) {
      errors.push(`Frame ${i} root quaternion not normalized: norm=${qNorm.toFixed(4)}`);
      break;
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}
