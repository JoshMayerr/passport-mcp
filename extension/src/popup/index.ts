document.addEventListener("DOMContentLoaded", async () => {
  const toggle = document.getElementById(
    "monitoring-toggle"
  ) as HTMLInputElement;
  const statusIndicator = document.getElementById("status-indicator");
  const statusText = document.getElementById("status-text");

  // Get initial state
  const response = await chrome.runtime.sendMessage({ type: "getStatus" });
  toggle.checked = response.isMonitoring;
  updateStatus(response.isMonitoring);

  // Handle toggle changes
  toggle.addEventListener("change", async () => {
    const response = await chrome.runtime.sendMessage({
      type: "toggleMonitoring",
    });
    updateStatus(response.isMonitoring);
  });

  function updateStatus(isMonitoring: boolean) {
    if (statusIndicator && statusText) {
      // Update indicator color
      statusIndicator.className = `w-3 h-3 rounded-full ${
        isMonitoring ? "bg-green-500" : "bg-gray-300"
      }`;

      // Update status text
      statusText.textContent = isMonitoring
        ? "Monitoring requests..."
        : "Not monitoring";
    }
  }
});
