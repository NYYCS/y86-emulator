<script setup lang="ts">
import { ref, computed, watchEffect } from "vue";
import { useCpu } from "../composables/useCpu";
import { useYoFile } from "../composables/useYoFile";

const { file, files, context } = useYoFile();
const { state } = useCpu();

const lineNumber = computed(() =>
  state.value ? context.value[state.value.PC] : 0
);

const el = computed<HTMLElement | undefined | null>(() => {
  if (!file.value) return undefined;
  return document.getElementById(`line-${lineNumber.value}`);
});

const source = ref<HTMLElement>();

watchEffect(() => {
  if (el.value) source.value!.scrollTop = el.value?.offsetTop - 250;
});
</script>

<template>
  <div class="file-preview">
    <h2>{{ `source code for ${file?.filename}` }}</h2>
    <div class="source-wrapper">
      <div ref="source" class="source">
        <template v-if="file">
          <p
            v-for="(text, i) in file.content.split('\n')"
            :id="`line-${i}`"
            :class="[i === context[state ? state.PC : 0] && 'active']"
          >
            {{ text }}
          </p>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.file-preview {
  display: flex;
  flex-direction: column;
  position: relative;
}
.source-wrapper {
  width: 50vw;
  max-width: 50vw;
  height: 70vh;
  max-height: 70vh;
  border: 1px var(--accent-green) solid;
  padding: 0.5em 1em;
  overflow: hidden;
}
.source {
  height: 100%;
  overflow: scroll;
}

.source p {
  display: flex;
  white-space: pre;
  margin: 0;
  font-size: 1rem;
  font-family: "glass_tty_vt220medium";
}

.active {
  color: var(--secondary-green);
  background: var(--accent-green);
}
</style>
