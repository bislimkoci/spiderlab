const value = (input, suffix = "") => input === null || input === undefined ? "--" : `${input}${suffix}`;
const percent = (input) => Math.max(0, Math.min(100, Number(input) || 0));

function formatUptime(seconds) {
  if (seconds === null || seconds === undefined) return "--";
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  if (hours > 0) return `${hours}h ${minutes}m`;
  if (minutes > 0) return `${minutes}m ${secs}s`;
  return `${secs}s`;
}

function setText(id, text) {
  document.getElementById(id).textContent = text;
}

function setBar(id, barValue) {
  document.getElementById(id).style.width = `${percent(barValue)}%`;
}

async function refreshStats() {
  try {
    const response = await fetch("/api/stats", { cache: "no-store" });
    const stats = await response.json();
    const camera = stats.camera;
    const system = stats.system;

    setText("worker-state", camera.running ? "Online" : "Offline");
    setText("fps", value(camera.fps));
    setText("target-fps", value(camera.target_fps));
    setText("frames", value(camera.frames));
    setText("uptime", formatUptime(system.uptime_seconds));

    setText("cpu-temp", value(system.cpu_temp_c, " deg C"));
    setText("cpu-percent", value(system.cpu_percent, "%"));
    setText("ram-percent", value(system.memory.percent, "%"));
    setText("app-ram", value(system.process.rss_mb, " MB"));

    setBar("temp-bar", system.cpu_temp_c === null ? 0 : system.cpu_temp_c / 85 * 100);
    setBar("cpu-bar", system.cpu_percent);
    setBar("ram-bar", system.memory.percent);
    setBar("app-ram-bar", system.process.rss_mb === null ? 0 : system.process.rss_mb / 512 * 100);

    setText(
      "memory-detail",
      `${value(system.memory.used_mb, " MB")} used / ${value(system.memory.total_mb, " MB")} total, ${value(system.memory.available_mb, " MB")} available`
    );
    setText(
      "load-average",
      `1m ${value(system.load_average.one)}, 5m ${value(system.load_average.five)}, 15m ${value(system.load_average.fifteen)}`
    );
    setText(
      "camera-detail",
      camera.has_frame
        ? `${value(camera.frames)} frames captured at ${value(camera.fps)} fps`
        : "Waiting for first frame"
    );
  } catch (error) {
    setText("worker-state", "Telemetry lost");
  }
}

refreshStats();
setInterval(refreshStats, 1000);
