// AI.VC Scout Chrome Extension - Note Page Script

document.addEventListener('DOMContentLoaded', function() {
  const urlInput = document.getElementById('url');
  const titleInput = document.getElementById('title');
  const notesTextarea = document.getElementById('notes');
  const saveButton = document.getElementById('saveButton');
  const cancelButton = document.getElementById('cancelButton');
  const statusDiv = document.getElementById('status');
  
  // Get URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const url = urlParams.get('url');
  const title = urlParams.get('title');
  
  // Set initial values
  urlInput.value = url || '';
  titleInput.value = title || '';
  
  // Add event listeners
  saveButton.addEventListener('click', handleSave);
  cancelButton.addEventListener('click', handleCancel);
  
  // Handle save button click
  async function handleSave() {
    if (!urlInput.value || !titleInput.value) {
      showStatus('URL and company name are required', 'error');
      return;
    }
    
    saveButton.disabled = true;
    
    try {
      // Prepare data
      const data = {
        url: urlInput.value,
        title: titleInput.value,
        notes: notesTextarea.value
      };
      
      // Send message to background script
      chrome.runtime.sendMessage({
        action: 'saveCompany',
        data: data
      }, function(response) {
        if (response && response.success) {
          showStatus('Company saved successfully!', 'success');
          // Close window after a short delay
          setTimeout(() => window.close(), 2000);
        } else {
          const errorMessage = (response && response.message) ? response.message : 'An unknown error occurred';
          showStatus(`Error: ${errorMessage}`, 'error');
          saveButton.disabled = false;
        }
      });
      
    } catch (error) {
      showStatus(`Error: ${error.message}`, 'error');
      console.error('Save error:', error);
      saveButton.disabled = false;
    }
  }
  
  // Handle cancel button click
  function handleCancel() {
    window.close();
  }
  
  // Show status message
  function showStatus(message, type) {
    statusDiv.textContent = message;
    statusDiv.className = 'status';
    statusDiv.style.display = 'block';
    if (type) {
      statusDiv.classList.add(type);
    }
  }
});