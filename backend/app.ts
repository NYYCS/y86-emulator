import express from "express";
import multer from "multer";
import cors from "cors";

import { exec } from "child_process";
import fs from "node:fs/promises";

const upload = multer({ dest: "yo_files/" });

const app = express();
app.use(express.json());
app.use(cors());

app.get("/yo-files", async (req, res) => {
  const filenames = await fs.readdir("yo_files/");
  const files = await Promise.all(
    filenames.map((filename) =>
      fs
        .readFile("yo_files/" + filename, { encoding: "utf-8" })
        .then((text) => ({ filename, content: text }))
    )
  );
  return res.status(200).json({ files });
});

app.post("/yo_files", upload.single("file"), async (req, res) => {
  return res.status(200);
});

app.post("/exec/:target", async (req, res) => {
  const { target = "" } = req.params as { target?: string };
  const files = await fs.readdir("yo_files/");
  if (!files.includes(target)) {
    return res.status(404).json({ message: "File not found." });
  }
  const cmd =
    Object.keys(req.body).length !== 0
      ? `python3 emulator/main.py --state "${JSON.stringify(
          req.body
        )}" < yo_files/${target}`
      : `python3 emulator/main.py < yo_files/${target}`;

  exec(cmd, { maxBuffer: 1024 * 4096 }, (err, stdout, stderr) => {
    return res.status(200).json({ history: JSON.parse(stdout) });
  });
});

app.listen(8080, () => {
  console.log("Listening at port 8080...");
});
