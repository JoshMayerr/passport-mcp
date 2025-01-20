const HOST_NAME = "com.browserpassport.native_messaging_host";

// Initialize state when service worker loads
let isMonitoring = false;

// Listen for web requests
chrome.webRequest.onSendHeaders.addListener(
  async (details) => {
    if (!isMonitoring) return;

    try {
      // Get cookies for the domain
      const url = new URL(details.url);
      const cookies = await chrome.cookies.getAll({
        domain: url.hostname,
      });

      // Prepare data for native host
      const requestData = {
        timestamp: new Date().toISOString(),
        url: details.url,
        headers:
          details.requestHeaders?.map((h) => ({
            name: h.name,
            value: h.value,
          })) || [],
        cookies: cookies.map((cookie) => ({
          name: cookie.name,
          value: cookie.value,
        })),
      };

      // Send to native host
      const message = {
        type: "request_data",
        data: requestData,
      };

      const response = await chrome.runtime.sendNativeMessage(
        HOST_NAME,
        message
      );

      console.debug("Native host response:", response);
    } catch (error) {
      console.error("Error sending request data:", error);
    }
  },
  { urls: ["<all_urls>"] },
  ["requestHeaders"]
);

// Handle messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.type) {
    case "getStatus":
      sendResponse({ isMonitoring });
      break;

    case "toggleMonitoring":
      isMonitoring = !isMonitoring;
      sendResponse({ isMonitoring });
      break;

    case "getDomainData":
      getDomainData(message.domain)
        .then((response) => sendResponse(response))
        .catch((error) => sendResponse({ error: error.message }));
      return true; // Required for async response
  }
});

async function getDomainData(domain: string) {
  const message = {
    type: "get_domain_data",
    domain,
  };

  try {
    return await chrome.runtime.sendNativeMessage(HOST_NAME, message);
  } catch (error) {
    console.error("Error getting domain data:", error);
    throw error;
  }
}
