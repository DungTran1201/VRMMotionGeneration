/**
 * Frontend automated unit test runner (Node.js test).
 */

import assert from 'node:assert';
import { validateCanonicalMotion } from '../src/motion/schema_validator.js';

console.log('--- Running Frontend Unit Tests ---');

// Test 1: Validate good fixture structure
const validSample = {
  schema: 'CanonicalHumanoidMotion/v1',
  metadata: {
    source: 'fixture',
    fps: 30.0,
    duration: 1.0,
    num_frames: 2,
    coordinate_system: 'glTF_Y_UP_Z_BACK_X_RIGHT',
    units: 'meters',
    rotation_format: 'quaternion_xyzw'
  },
  frames: [
    {
      timestamp: 0.0,
      frame_index: 0,
      root: { position: [0, 1, 0], rotation: [0, 0, 0, 1] },
      bones: { hips: { rotation: [0, 0, 0, 1] } }
    },
    {
      timestamp: 0.5,
      frame_index: 1,
      root: { position: [0, 1, -0.5], rotation: [0, 0, 0, 1] },
      bones: { hips: { rotation: [0, 0, 0, 1] } }
    }
  ]
};

const res1 = validateCanonicalMotion(validSample);
assert.strictEqual(res1.valid, true, `Expected valid, got errors: ${res1.errors.join(', ')}`);
console.log('✓ Test 1 Passed: Valid motion document validated');

// Test 2: Reject invalid schema version
const invalidSchema = { ...validSample, schema: 'InvalidSchema/v9' };
const res2 = validateCanonicalMotion(invalidSchema);
assert.strictEqual(res2.valid, false);
assert.ok(res2.errors[0].includes('Unsupported schema'));
console.log('✓ Test 2 Passed: Invalid schema rejected');

// Test 3: Reject non-monotonic timestamps
const nonMonotonic = {
  ...validSample,
  frames: [
    { ...validSample.frames[0], timestamp: 1.0 },
    { ...validSample.frames[1], timestamp: 0.5 }
  ]
};
const res3 = validateCanonicalMotion(nonMonotonic);
assert.strictEqual(res3.valid, false);
assert.ok(res3.errors[0].includes('Non-monotonic timestamp'));
console.log('✓ Test 3 Passed: Non-monotonic timestamp rejected');

// Test 4: Reject non-unit quaternion
const nonUnitQuat = {
  ...validSample,
  frames: [
    {
      ...validSample.frames[0],
      root: { position: [0, 0, 0], rotation: [2.0, 0, 0, 0] }
    },
    validSample.frames[1]
  ]
};
const res4 = validateCanonicalMotion(nonUnitQuat);
assert.strictEqual(res4.valid, false);
assert.ok(res4.errors[0].includes('quaternion not normalized'));
console.log('✓ Test 4 Passed: Non-unit quaternion rejected');

console.log('--- All 4 Frontend Unit Tests Passed! ---');
