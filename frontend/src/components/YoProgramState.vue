<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useCpu } from "../composables/useCpu";

const { state, cycle } = useCpu();

const STAT_CODE = {
  1: "AOK",
  2: "HLT",
  3: "ADR",
  4: "INS",
};

const memoryOffset = ref(0);
const memorySize = computed(() => Object.keys(state.value?.MEM ?? {}).length);
const memory = computed(() => {
  if (!state.value) return { 0: 0, 8: 0, 16: 0, 24: 0 };
  const mem = Object.entries(state.value.MEM).reduce((prev, next, index) => {
    if (!(memoryOffset.value <= index && memoryOffset.value + 4 > index))
      return prev;
    const [addr, value] = next;
    prev[Number(addr)] = value;
    return prev;
  }, {} as Record<number, number>);

  const diff = 4 - memorySize.value;
  if (diff != 0) {
    const lastAddr = Number(Object.keys(mem).at(-1));
    for (let i = 0; i < diff + 1; i++) {
      mem[lastAddr + i * 8] = 0;
    }
  }

  return mem;
});

function cycleMemory() {
  if (memorySize.value - memoryOffset.value <= 4) memoryOffset.value = 0;
  else memoryOffset.value++;
}

function hexify(value: number) {
  return (
    "0x" + BigInt.asUintN(64, BigInt(value)).toString(16).padStart(16, "0")
  );
}
</script>

<template>
  <div class="program-state">
    <div class="wrapper">
      <div class="block">
        <h2 style="font-size: 1rem !important">PROGRAM STATE</h2>
        <div class="stat-wrapper">
          <div class="stat-panel">
            <ul>
              <li>
                <span class="stat-label">RAX</span
                ><span class="stat-value" :key="state?.REG.rax"
                  >{{ hexify(state ? state.REG.rax : 0) }}
                </span>
              </li>
              <li>
                <span class="stat-label">RCX</span
                ><span class="stat-value" :key="state?.REG.rcx"
                  >{{ hexify(state ? state.REG.rcx : 0) }}
                </span>
              </li>
              <li>
                <span class="stat-label">RBX</span
                ><span class="stat-value" :key="state?.REG.rbx"
                  >{{ hexify(state ? state.REG.rbx : 0) }}
                </span>
              </li>
              <li>
                <span class="stat-label">RDX</span
                ><span class="stat-value" :key="state?.REG.rdx"
                  >{{ hexify(state ? state.REG.rdx : 0) }}
                </span>
              </li>
              <li>
                <span class="stat-label">RSP</span
                ><span class="stat-value"
                  >{{ hexify(state ? state.REG.rdx : 0) }}
                </span>
              </li>
              <li>
                <span class="stat-label">RBP</span
                ><span class="stat-value" :key="state?.REG.rbp"
                  >{{ hexify(state ? state.REG.rbp : 0) }}
                </span>
              </li>
              <li>
                <span class="stat-label">RSI</span
                ><span class="stat-value" :key="state?.REG.rsi"
                  >{{ hexify(state ? state.REG.rsi : 0) }}
                </span>
              </li>
              <li>
                <span class="stat-label">RDI</span
                ><span class="stat-value" :key="state?.REG.rdi"
                  >{{ hexify(state ? state.REG.rdi : 0) }}
                </span>
              </li>
              <li>
                <span class="stat-label">R8</span
                ><span class="stat-value" :key="state?.REG.r8"
                  >{{ hexify(state ? state.REG.r8 : 0) }}
                </span>
              </li>
              <li>
                <span class="stat-label">R9</span
                ><span class="stat-value" :key="state?.REG.r9"
                  >{{ hexify(state ? state.REG.r9 : 0) }}
                </span>
              </li>
              <li>
                <span class="stat-label">R10</span
                ><span class="stat-value" :key="state?.REG.r10"
                  >{{ hexify(state ? state.REG.r10 : 0) }}
                </span>
              </li>
              <li>
                <span class="stat-label">R11</span
                ><span class="stat-value" :key="state?.REG.r11"
                  >{{ hexify(state ? state.REG.r11 : 0) }}
                </span>
              </li>
              <li>
                <span class="stat-label">R12</span
                ><span class="stat-value" :key="state?.REG.r12"
                  >{{ hexify(state ? state.REG.r12 : 0) }}
                </span>
              </li>
              <li>
                <span class="stat-label">R13</span
                ><span class="stat-value" :key="state?.REG.r13"
                  >{{ hexify(state ? state.REG.r13 : 0) }}
                </span>
              </li>
              <li>
                <span class="stat-label">R14</span
                ><span class="stat-value" :key="state?.REG.r14"
                  >{{ hexify(state ? state.REG.r14 : 0) }}
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div @click="cycleMemory" class="wrapper">
      <div class="block">
        <div class="stat-wrapper">
          <div class="stat-panel">
            <ul>
              <li v-for="(value, addr) in memory">
                <span class="stat-label">{{ addr }}</span>
                <span class="stat-value" :key="value">
                  {{ hexify(value) }}</span
                >
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div class="wrapper">
      <div class="block">
        <div class="stat-wrapper">
          <div class="stat-panel">
            <ul>
              <li v-for="(value, flag) in state?.CC">
                <span class="stat-label">{{ flag }}</span>
                <span class="stat-value" :key="value"> {{ value }}</span>
              </li>
            </ul>
          </div>
          <div class="stat-panel">
            <ul>
              <li>
                <span class="stat-label" style="margin-right: 1em">STAT</span>
                <span class="stat-value" :key="state?.STAT">
                  {{ STAT_CODE[state?.STAT ?? 1] }}
                </span>
              </li>
              <li>
                <span class="stat-label" style="margin-right: 1em">PC</span>
                <span class="stat-value" :key="state?.PC">
                  {{ state?.PC ?? 0 }}
                </span>
              </li>
              <li>
                <span class="stat-label" style="margin-right: 1em">CYCLE</span>
                <span class="stat-value" :key="cycle">
                  {{ cycle }}
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.program-state {
  display: flex;
  flex-direction: column;
  position: relative;
  font-size: 1rem;
  gap: 0.3rem;
}

.wrapper {
  display: flex;
  gap: 1em;
}

.block {
  display: flex;
  flex-direction: column;
}

.stat-wrapper {
  display: flex;
  flex-direction: row;
  border: 1px solid var(--accent-green);
}

.stat-panel {
  display: flex;
  flex-direction: column;
  padding: 0.5rem 1.5rem;
  width: 100%;
}

.stat-panel ul {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.stat-panel li {
  width: 100%;
  display: flex;
  gap: 1rem;
}

.stat-label {
  display: flex;
  width: 2rem;
}

.stat-value {
  display: flex;
  flex: 1;
  animation: flash 0.3s linear;
}
</style>
