// Opens Ctrl+clicked .html/.htm terminal links via lavish-axi in Helium.
import { exec, home, notify } from "herdr";

function cleanRawPath(raw) {
  if (!raw || typeof raw !== "string") return null;
  let p = raw.trim().replace(/^['"`]|['"`]$/g, "");
  if (/^file:\/\//i.test(p)) {
    p = decodeURIComponent(p.replace(/^file:\/\/\/?/i, ""));
    if (/^\/[a-zA-Z]:/.test(p)) p = p.slice(1);
  }
  // Strip #anchor or :line(:col) suffix
  p = p.replace(/#.*$/, "").replace(/:\d+(?::\d+)?(?:-\d+)?$/, "");
  return p || null;
}

function isAbsolute(p) {
  return /^[a-zA-Z]:[\\/]/.test(p) || p.startsWith("\\\\") || p.startsWith("/");
}

function resolvePath(click) {
  if (click?.link?.path) return click.link.path;
  const raw = cleanRawPath(click?.link?.raw);
  if (!raw) return null;
  if (isAbsolute(raw)) return raw;
  const cwd = click?.source?.cwd;
  if (!cwd) return null;
  const sep = cwd.includes("\\") ? "\\" : "/";
  return `${cwd.replace(/[\\/]+$/, "")}${sep}${raw.replace(/^[\\/]+/, "")}`;
}

async function openInHelium(target) {
  const helium = `${home()}\\AppData\\Local\\imput\\Helium\\Application\\chrome.exe`;
  // Detached launch so handleLink returns immediately even if Helium isn't running yet.
  await exec("cmd", ["/c", "start", "", helium, target], { timeout: 10000 });
}

export async function handleLink(click) {
  if (click?.source?.machine) return "pass";

  const filePath = resolvePath(click);
  if (!filePath || !/\.html?$/i.test(filePath)) return "pass";

  const lavishCli = `${home()}\\AppData\\Roaming\\npm\\node_modules\\lavish-axi\\dist\\cli.mjs`;

  try {
    const res = await exec("node", [lavishCli, filePath, "--no-open", "--reopen"], { timeout: 15000 });
    const url = (res.stdout || "").match(/https?:\/\/[^\s"'<>]+/)?.[0];
    if (res.code === 0 && url) {
      await openInHelium(url);
      return "handled";
    }
    // Fallback: open the HTML file directly in Helium if lavish-axi couldn't serve it.
    await openInHelium(filePath);
    notify({
      title: "Opened HTML directly in Helium",
      body: (res.stderr || res.stdout || "lavish-axi failed").trim().slice(0, 160),
      level: "warning",
      timeout: 4000,
    });
    return "handled";
  } catch (err) {
    try {
      await openInHelium(filePath);
      return "handled";
    } catch (err2) {
      notify({
        title: "Could not open HTML file",
        body: String(err2?.message || err?.message || err2),
        level: "error",
        timeout: 5000,
      });
      return "handled";
    }
  }
}
