<script setup lang="ts">
defineProps<{
  type: "loading" | "empty" | "error" | "not-available";
  title: string;
  description: string;
  actionLabel?: string;
}>();

const emit = defineEmits<{
  (e: "action"): void;
}>();
</script>

<template>
  <div :class="['state-view', `state-${type}`]">
    <div class="state-icon">
      <span v-if="type === 'loading'" class="spinner"></span>
      <span v-else-if="type === 'empty'">📂</span>
      <span v-else-if="type === 'error'">⚠️</span>
      <span v-else-if="type === 'not-available'">🚫</span>
    </div>
    <h3 class="state-title">{{ title }}</h3>
    <p class="state-description">{{ description }}</p>
    <button
      v-if="actionLabel"
      id="state-view-action-btn"
      class="state-action-btn"
      @click="emit('action')"
    >
      {{ actionLabel }}
    </button>
  </div>
</template>

<style scoped>
.state-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
  background: var(--bg-card);
  border: 1px dashed var(--border-subtle);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(8px);
}

.state-icon {
  font-size: 2.5rem;
  margin-bottom: 16px;
}

.spinner {
  display: inline-block;
  width: 36px;
  height: 36px;
  border: 3px solid var(--border-subtle);
  border-top-color: var(--accent-cyan);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.state-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.state-description {
  font-size: 0.95rem;
  color: var(--text-secondary);
  max-width: 480px;
  margin-bottom: 20px;
}

.state-action-btn {
  padding: 8px 18px;
  background: var(--accent-cyan);
  color: #000;
  font-weight: 600;
  font-size: 0.875rem;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.state-action-btn:hover {
  background: #22d3ee;
  box-shadow: 0 0 12px var(--accent-cyan-glow);
}
</style>
