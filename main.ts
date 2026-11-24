// The World in One Day: Tuesday 24 November 2026 — make.fun entry.
//
// The repository holds entry.png, a one-page newspaper front page that
// sums up the world's news of Tuesday 24 November 2026, rendered by
// compose.py. This program's job is only to deliver it: copy the image
// that sits beside this file into the output directory as entry.png.
//
// The output directory is /output when the grader runs the program, or
// the MAKEFUN_OUTPUT_DIR environment variable when it is run locally:
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
//
// Node 22 standard library only; no network.

import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");

if (!existsSync(source)) {
  throw new Error(`entry.png is missing beside main.ts (looked in ${here})`);
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });

const target = join(outDir, "entry.png");
copyFileSync(source, target);

// Verify the delivery byte for byte: the grader runs this program twice
// and both runs must produce the identical image, so a short or garbled
// copy is a failure worth naming rather than shipping silently.
const delivered = readFileSync(target);
const original = readFileSync(source);
if (!delivered.equals(original)) {
  throw new Error(
    `copied entry.png differs from the source (${delivered.length} vs ${original.length} bytes)`,
  );
}

console.log(`entry.png delivered to ${target} (${delivered.length} bytes)`);
