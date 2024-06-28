import * as fs from "fs";
import * as path from "path";

function loadJSON(file, dir) {
  const filePath = path.join(dir, file);
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

const pythonDataDir = path.join("src", "data");
export { pythonDataDir, loadJSON };
