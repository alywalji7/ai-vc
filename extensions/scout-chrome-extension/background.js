// AI.VC Scout Chrome Extension - Background Script

// Create a context menu item
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "save-to-aivc",
    title: "Save to AI.VC",
    contexts: ["page"]
  });
});

// Handle context menu click
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "save-to-aivc") {
    // Get token from storage
    chrome.storage.local.get(['authToken'], (result) => {
      if (result.authToken) {
        // Open note taking popup
        chrome.windows.create({
          url: `note.html?url=${encodeURIComponent(tab.url)}&title=${encodeURIComponent(tab.title)}`,
          type: "popup",
          width: 500,
          height: 600
        });
      } else {
        // If no token, show message to log in
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'images/icon128.png',
          title: 'Authentication Required',
          message: 'Please log in to your AI.VC account first'
        });
        
        // Open the popup for login
        chrome.action.openPopup();
      }
    });
  }
});

// Listen for messages from popup and note.html
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "saveCompany") {
    saveCompanyToAIVC(request.data, sendResponse);
    return true; // Keep the messaging channel open for async response
  }
});

// Function to send data to AI.VC backend
async function saveCompanyToAIVC(data) {
  const API_BASE_URL = "https://api.ai.vc"; // Replace with your actual API URL
  
  try {
    // Get authentication token
    const storageData = await chrome.storage.local.get(['authToken']);
    const token = storageData.authToken;
    
    if (!token) {
      throw new Error("Authentication required");
    }
    
    // Send POST request to Scout API
    const response = await fetch(`${API_BASE_URL}/api/scout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        url: data.url,
        title: data.title,
        notes: data.notes
      })
    });
    
    const responseData = await response.json();
    
    if (!response.ok) {
      throw new Error(responseData.detail || "Failed to save company");
    }
    
    // Show success notification
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'images/icon128.png',
      title: 'Success',
      message: 'Company saved to AI.VC successfully!'
    });
    
    return responseData;
  } catch (error) {
    console.error("Error saving company:", error);
    
    // Show error notification
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'images/icon128.png',
      title: 'Error',
      message: `Failed to save company: ${error.message}`
    });
    
    throw error;
  }
}