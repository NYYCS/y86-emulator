<script setup lang="ts">
import { useYoFile } from "../composables/useYoFile";

const { file: currentFile, files, uploadYoFile } = useYoFile();

async function upload(event: Event) {
  const target = event.target as HTMLInputElement;
  const files = target.files;
  if (!files) return;
  uploadYoFile(files[0]);
}
</script>

<template>
  <div class="file-explorer">
    <h2>FILES</h2>
    <div class="files">
      <div class="files-meta">
        <span class="add-file">
          {{ "DIRECTORY: yo_files/" }}
          <label for="file-upload" class="add-file">
            {{ "ADD FILE +" }}
          </label>
          <input @change="upload" id="file-upload" type="file" />
        </span>
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
input[type="file"] {
  display: none;
}
.add-file {
  cursor: pointer;
}
</style>
