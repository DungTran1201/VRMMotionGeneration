<script setup lang="ts">
defineProps<{
  status: "active" | "ready" | "offline" | "error" | "warning";
  label?: string;
}>();
</script>

<template>
  <span :class="['status-badge', `status-${status}`]" role="status">
    <span class="dot"></span>
    <span class="text">{{ label || status }}</span>
  </span>
</template>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid transparent;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-active,
.status-ready {
  background: rgba(16, 185, 129, 0.12);
  color: var(--accent-success);
  border-color: rgba(16, 185, 129, 0.3);
}
.status-active .dot,
.status-ready .dot {
  background: var(--accent-success);
  box-shadow: 0 0 8px var(--accent-success);
}

.status-offline {
  background: rgba(107, 114, 128, 0.15);
  color: var(--text-muted);
  border-color: rgba(107, 114, 128, 0.3);
}
.status-offline .dot {
  background: var(--text-muted);
}

.status-warning {
  background: rgba(245, 158, 11, 0.12);
  color: var(--accent-warning);
  border-color: rgba(245, 158, 11, 0.3);
}
.status-warning .dot {
  background: var(--accent-warning);
}

.status-error {
  background: rgba(239, 68, 68, 0.12);
  color: var(--accent-danger);
  border-color: rgba(239, 68, 68, 0.3);
}
.status-error .dot {
  background: var(--accent-danger);
  box-shadow: 0 0 8px var(--accent-danger);
}
</style>
