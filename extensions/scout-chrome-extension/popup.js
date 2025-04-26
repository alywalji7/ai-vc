// AI.VC Scout Chrome Extension - Popup Script

document.addEventListener('DOMContentLoaded', function() {
  const loginContainer = document.getElementById('loginContainer');
  const logoutContainer = document.getElementById('logoutContainer');
  const loginButton = document.getElementById('loginButton');
  const logoutButton = document.getElementById('logoutButton');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const loginStatus = document.getElementById('loginStatus');
  
  // Check authentication status on popup open
  checkAuthStatus();
  
  // Add event listeners
  loginButton.addEventListener('click', handleLogin);
  logoutButton.addEventListener('click', handleLogout);
  
  // Check if user is authenticated
  function checkAuthStatus() {
    chrome.storage.local.get(['authToken'], function(result) {
      if (result.authToken) {
        // User is logged in
        loginContainer.style.display = 'none';
        logoutContainer.style.display = 'block';
      } else {
        // User is not logged in
        loginContainer.style.display = 'block';
        logoutContainer.style.display = 'none';
      }
    });
  }
  
  // Handle login button click
  async function handleLogin() {
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    
    if (!email || !password) {
      showStatus('Please enter both email and password', 'error');
      return;
    }
    
    loginButton.disabled = true;
    
    try {
      // In a real implementation, this would call your authentication API
      // For now, we'll simulate a successful login with a mock token
      const token = `mock_token_${Date.now()}`;
      
      // Save token to storage
      await chrome.storage.local.set({ authToken: token });
      
      // Update UI
      showStatus('Login successful!', 'success');
      setTimeout(checkAuthStatus, 1000);
      
    } catch (error) {
      showStatus(`Login failed: ${error.message}`, 'error');
      console.error('Login error:', error);
    } finally {
      loginButton.disabled = false;
    }
  }
  
  // Handle logout button click
  async function handleLogout() {
    try {
      // Remove auth token from storage
      await chrome.storage.local.remove(['authToken']);
      
      // Update UI
      checkAuthStatus();
    } catch (error) {
      console.error('Logout error:', error);
    }
  }
  
  // Show status message
  function showStatus(message, type) {
    loginStatus.textContent = message;
    loginStatus.className = 'status';
    if (type) {
      loginStatus.classList.add(type);
    }
  }
});