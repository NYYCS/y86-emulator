<script setup lang="ts">
import { useYoFile } from "../composables/useYoFile";
import { useApi } from "../composables/useApi";

const axios = useApi();

const { file: currentFile, files } = useYoFile();

function uploadFile() {}
</script>

<template>
  <div class="file-explorer">
    <h2>FILES</h2>
    <div class="files">
      <div class="files-meta">
        <span class="add-file">{{ "DIRECTORY: yo_files/ +" }}</span>
      </div>
      <ul>
        <li
          :class="[currentFile?.filename == file.filename && 'active']"
          v-for="file in files"
          @click="currentFile = file"
        >
          {{ file.filename }}
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.file-explorer {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.files-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1em;
  font-size: 1rem;
}

.add-file {
  cursor: pointer;
}
.files {
  display: flex;
  height: 70vh;
  max-height: 70vh;
  flex-direction: column;
  border: 1px var(--accent-green) solid;
  padding: 0.5em 1em;
  overflow-y: scroll;
}
ul {
  display: flex;
  flex-direction: column;
  position: relative;
  flex: 1;
}
li {
  position: relative;
  cursor: pointer;
  font-size: 1rem;
}
li.active {
  color: var(--secondary-green);
  background: var(--accent-green);
}

li:not(.active):hover::before {
  content: ">";
  margin-right: 0.5em;
  font-weight: bold;
}
</style>
