const { app, BrowserWindow } = require("electron");
const fs = require("node:fs");
const http = require("node:http");
const path = require("node:path");

const webRoot = path.resolve(__dirname, "..", "dist");
const contentTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".ico": "image/x-icon",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".woff2": "font/woff2",
};

const server = http.createServer((request, response) => {
  let requestPath;
  try {
    requestPath = decodeURIComponent(new URL(request.url ?? "/", "http://localhost").pathname);
  } catch {
    response.writeHead(400).end();
    return;
  }

  const requestedFile = requestPath === "/" ? "index.html" : requestPath.slice(1);
  const filePath = path.resolve(webRoot, requestedFile);
  if (!filePath.startsWith(`${webRoot}${path.sep}`)) {
    response.writeHead(403).end();
    return;
  }

  const servedFile = fs.existsSync(filePath) && fs.statSync(filePath).isFile()
    ? filePath
    : path.join(webRoot, "index.html");
  fs.readFile(servedFile, (error, content) => {
    if (error) {
      response.writeHead(404).end();
      return;
    }
    response.writeHead(200, {
      "Content-Type": contentTypes[path.extname(servedFile)] ?? "application/octet-stream",
      "X-Content-Type-Options": "nosniff",
    });
    response.end(content);
  });
});

async function openApp() {
  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(5174, "127.0.0.1", resolve);
  });

  const window = new BrowserWindow({
    width: 1280,
    height: 840,
    minWidth: 360,
    minHeight: 600,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });
  const apiUrl = process.env.WASLA_API_URL ?? process.env.VITE_API_URL ?? "http://127.0.0.1:8000";
  const query = new URLSearchParams({ platform: "desktop", apiUrl });
  await window.loadURL(`http://127.0.0.1:5174/?${query}`);
}

app.whenReady().then(openApp);
app.on("before-quit", () => server.close());
app.on("window-all-closed", () => app.quit());