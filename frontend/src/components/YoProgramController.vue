<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useYoFile } from "../composables/useYoFile";
import { useCpu } from "../composables/useCpu";

const { history, halting, cycle } = useCpu();
const { file } = useYoFile();

const progress = computed(() => {
  if (history.value.length == 0) return 0;
  if (!halting.value) return 0;
  return Math.ceil((cycle.value / (history.value.length - 1)) * 100);
});

const interval = ref<number>(0);
const paused = ref(true);

watch(
  () => paused.value,
  () => {
    if (paused.value) clearInterval(interval.value);
    else
      interval.value = setInterval(() => {
        if (cycle.value !== history.value.length - 1) cycle.value++;
      }, 200);
  }
);

watch(
  () => file.value,
  () => (paused.value = true),
  { deep: true }
);

watch(
  () => cycle.value,
  () => {
    if (cycle.value === history.value.length - 1) paused.value = true;
  }
);
</script>

<template>
  <div class="yo-program-controller">
    <div class="progress-bar">
      <span> {{ halting ? `${progress}%` : "?%" }}</span>
      [
      <progress
        style="transform: translateX(-1px) translateY(-1px)"
        max="100"
        :value="progress"
      />
      ]
    </div>
    <div class="button-group">
      <button
        @click="
          cycle > 0 && cycle--;
          paused = true;
        "
      >
        {{ "<" }}
      </button>
      <button style="width: 4rem" @click="paused = !paused">
        {{ paused ? "PLAY" : "PAUSE" }}
      </button>
      <button
        @click="
          history.length > cycle && cycle++;
          paused = true;
        "
      >
        {{ ">" }}
      </button>
      <button
        @click="
          cycle = 0;
          paused = true;
        "
      >
        RESET
      </button>
    </div>
  </div>
</template>

<style scoped>
.yo-program-controller {
  display: flex;
  transform: translateX(80%);
  align-items: center;
  justify-content: center;
  width: 20vw;
}
.progress-bar {
  display: flex;
  align-items: center;
  position: absolute;
  transform: translateX(-300px);
}

progress {
  width: 256px;
  height: 4px;
  border: 0;
  background: black;
}

::-webkit-progress-bar {
  appearance: none;
  background: black;
}

::-webkit-progress-value {
  background: var(--accent-green);
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 1em;
  width: 100%;
}

.button-group button {
  background: none;
}
</style>
