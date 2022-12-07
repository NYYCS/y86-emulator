import { ref, computed, watch, watchEffect } from "vue";

import { useApi } from "./useApi";
import { useYoFile } from "./useYoFile";

const HISTORY_BATCH_SIZE = 100000;

const axios = useApi();

type Flag = 0 | 1;

export enum StatCode {
  AOK = 1,
  HLT = 2,
  ADR = 3,
  INS = 4,
}

interface CPUState {
  PC: number;
  REG: {
    rax: number;
    rcx: number;
    rdx: number;
    rbx: number;
    rsp: number;
    rbp: number;
    rsi: number;
    rdi: number;
    r8: number;
    r9: number;
    r10: number;
    r11: number;
    r12: number;
    r13: number;
    r14: number;
  };
  MEM: Record<number, number>;
  CC: {
    ZF: Flag;
    SF: Flag;
    OF: Flag;
  };
  STAT: StatCode;
}

const history = ref<CPUState[]>([]);
const halting = computed(() => {
  if (history.value.length == 0) return true;
  return history.value.at(-1)!.STAT != StatCode.AOK;
});
const cycle = ref(0);

export function useCpu() {
  const { file } = useYoFile();

  const state = computed<CPUState | undefined>(() => {
    if (!file.value) return undefined;
    return history.value[cycle.value];
  });

  watchEffect(async () => {
    if (!file.value) return;
    const res = await axios.post("/exec/" + file?.value.filename);
    history.value = res.data.history;
    cycle.value = 0;
  });

  watch(
    () =>
      cycle.value ===
      Math.ceil(history.value.length / HISTORY_BATCH_SIZE) *
        HISTORY_BATCH_SIZE *
        0.8,
    async () => {
      if (cycle.value === HISTORY_BATCH_SIZE * 0.8 && !halting.value) {
        const res = await axios.post(
          "/exec/" + file.value!.filename,
          history.value.at(-1)
        );
        history.value = [...history.value, ...res.data.history];
      }
    }
  );

  return { history, halting, cycle, state };
}
