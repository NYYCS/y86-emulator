<script setup lang="ts">
import YoFileExplorer from "./components/YoFileExplorer.vue";
import YoFilePreview from "./components/YoFilePreview.vue";
import YoProgramController from "./components/YoProgramController.vue";
import YoProgramState from "./components/YoProgramState.vue";
</script>

<template>
  <div class="main">
    <div class="title-bar">
      <h1 style="transform: translateX(-50%)">Y-86 Emulator</h1>
      <div class="program-controller">
        <YoProgramController />
      </div>
    </div>
    <div class="display">
      <div><YoFileExplorer /></div>
      <div><YoFilePreview /></div>
      <div><YoProgramState /></div>
    </div>
  </div>
</template>

<style scoped>
.main {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.display {
  display: flex;
  flex-direction: row;
  justify-content: center;
  gap: 1em;
}

.title-bar {
  display: flex;
  justify-content: center;
  align-items: center;
}

.program-controller {
  display: flex;
  flex: 1;
}
</style>
