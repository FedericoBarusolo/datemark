importScripts('auth.js');

// Handle messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  handleMessage(request, sender, sendResponse);
  return true; // Keep channel open for async response
});

async function handleMessage(request, sender, sendResponse) {
  try {
    switch (request.action) {
      case 'checkAuth':
        const authResult = await authManager.silentAuth();
        sendResponse(authResult);
        break;

      case 'login':
        const loginResult = await authManager.interactiveAuth();
        sendResponse(loginResult);
        break;

      case 'logout':
        await authManager.logout();
        sendResponse({ success: true });
        break;

      case 'fetchList':
        const list = await authManager.callCloudRun('/agent', request.data);
        sendResponse({ success: true, data: list });
        break;

      case 'addToCalendar':
        const results = await authManager.addToCalendar(request.events);
        sendResponse({ success: true, results });
        break;

      default:
        sendResponse({ success: false, error: 'Unknown action' });
    }
  } catch (error) {
    console.error('Background error:', error);
    sendResponse({ success: false, error: error.message });
  }
}

// Clear token cache on extension install/update
chrome.runtime.onInstalled.addListener(() => {
  console.log('Extension installed/updated');
});