import { existsSync, readFileSync } from "node:fs";
import { spawn } from "node:child_process";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const frontendDir = path.resolve(__dirname, "..");
const backendDir = path.resolve(frontendDir, "..", "backend");
const backendPythonCandidates = [
  path.join(backendDir, ".venv", "Scripts", "python.exe"),
  path.join(backendDir, ".venv", "bin", "python"),
];
const backendPython = backendPythonCandidates.find((candidate) => existsSync(candidate));
const isWindows = process.platform === "win32";
const backendArgs = isWindows
  ? ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
  : ["-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"];

if (!backendPython) {
  console.error("Backend virtualenv is missing at backend/.venv.");
  console.error("Create it first with Python 3.11 or 3.12 and install backend/requirements.txt.");
  process.exit(1);
}

try {
  const pyvenvConfig = readFileSync(path.join(backendDir, ".venv", "pyvenv.cfg"), "utf8");
  const match = pyvenvConfig.match(/^version = (\d+)\.(\d+)(?:\.\d+)?$/m);
  const version = match ? `${match[1]}.${match[2]}` : "unknown";

  const [major, minor] = version.split(".").map(Number);
  if (major !== 3 || minor < 11 || minor > 12) {
    console.error(`Backend venv is using Python ${version}.`);
    console.error("ChromaDB in this project requires Python 3.11 or 3.12.");
    console.error("Recreate backend/.venv with Python 3.11 or 3.12, then reinstall requirements.");
    process.exit(1);
  }
} catch (error) {
  console.error("Could not verify the backend Python version.");
  console.error(error.message);
  process.exit(1);
}

const backend = isWindows
  ? spawn(
      `"${backendPython}" ${backendArgs.join(" ")}`,
      [],
      {
        cwd: backendDir,
        stdio: "inherit",
        shell: true,
      },
    )
  : spawn(
      `"${backendPython}" ${backendArgs.join(" ")}`,
      [],
      {
        cwd: backendDir,
        stdio: "inherit",
        shell: true,
      },
    );

const frontend = spawn("npm", ["run", "dev:frontend"], {
  cwd: frontendDir,
  stdio: "inherit",
  shell: isWindows,
});

let shuttingDown = false;

function shutdown(exitCode = 0) {
  if (shuttingDown) {
    return;
  }
  shuttingDown = true;

  if (!backend.killed) {
    backend.kill("SIGTERM");
  }

  if (!frontend.killed) {
    frontend.kill("SIGTERM");
  }

  setTimeout(() => process.exit(exitCode), 150);
}

backend.on("exit", (code) => {
  if (!shuttingDown) {
    console.error(`Backend exited with code ${code ?? 0}.`);
    shutdown(code ?? 1);
  }
});

frontend.on("exit", (code) => {
  if (!shuttingDown) {
    shutdown(code ?? 0);
  }
});

["SIGINT", "SIGTERM"].forEach((signal) => {
  process.on(signal, () => shutdown(0));
});
