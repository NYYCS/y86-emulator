import { ref, computed, Ref, ComputedRef } from "vue";
import { useApi } from "./useApi";

const axios = useApi();

type YoFile = { filename: string; content: string };
type YoFileContext = Record<number, number>;

interface Yo {
  file: Ref<YoFile | undefined>;
  files: Ref<YoFile[]>;
  context: ComputedRef<YoFileContext>;
  uploadYoFile: (file: File) => Promise<void>;
}

const file = ref<YoFile | undefined>();
const files = ref<YoFile[]>([]);
const context = computed(() => {
  if (!file.value) return undefined;
  return file.value.content
    .trim()
    .split("\n")
    .reduce((prev, next, index) => {
      const [left] = next.split("|");
      const addrBincode = left.split(":");
      if (addrBincode.length == 2) {
        const [addr] = addrBincode;
        prev[Number.parseInt(addr, 16)] = index;
      }
      return prev;
    }, {} as Record<number, number>);
});

export async function uploadYoFile(uploadedFile: File) {
  const formData = new FormData();
  formData.append("file", uploadedFile);
  await axios.post("/yo_files", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  await getYoFile();

  file.value = files.value.find(
    (yoFile) => yoFile.filename === uploadedFile.name
  );
}

export async function getYoFile() {
  const res = await axios.get("/yo-files");
  file.value = res.data.files[0];
  files.value = res.data.files;
}

await getYoFile();

export function useYoFile() {
  return { file, files, context, uploadYoFile } as Yo;
}
