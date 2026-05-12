import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import fs from "fs";
import path from "path";

async function render() {
  const args = process.argv.slice(2);
  const propsFileIndex = args.indexOf("--props");
  const outputIndex = args.indexOf("--output");

  if (propsFileIndex === -1 || !args[propsFileIndex + 1]) {
    console.error(
      "Usage: npx tsx src/render.ts --props <props.json> --output <output.mp4>"
    );
    process.exit(1);
  }

  const propsFile = args[propsFileIndex + 1];
  const outputFile =
    outputIndex !== -1 ? args[outputIndex + 1] : "output.mp4";

  const propsData = JSON.parse(
    fs.readFileSync(propsFile, "utf-8")
  ) as Record<string, unknown>;

  console.log("Bundling Remotion project...");
  const bundleLocation = await bundle({
    entryPoint: path.resolve(__dirname, "./index.ts"),
    webpackOverride: (config) => config,
  });

  console.log("Selecting composition...");
  const composition = await selectComposition({
    serveUrl: bundleLocation,
    id: "YouTubeVideo",
    inputProps: propsData,
  });

  console.log(
    `Rendering video: ${composition.width}x${composition.height} @ ${composition.fps}fps`
  );
  console.log(`Duration: ${composition.durationInFrames} frames`);

  await renderMedia({
    composition,
    serveUrl: bundleLocation,
    codec: "h264",
    outputLocation: outputFile,
    inputProps: propsData,
    onProgress: ({ progress }) => {
      process.stdout.write(`\rRendering: ${(progress * 100).toFixed(1)}%`);
    },
  });

  console.log(`\nVideo rendered successfully: ${outputFile}`);
}

render().catch((err) => {
  console.error("Render failed:", err);
  process.exit(1);
});
