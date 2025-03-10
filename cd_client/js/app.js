/**
 * ChangeDetection.io Client
 * A beautiful UI for interacting with the ChangeDetection.io API
 */

document.addEventListener('DOMContentLoaded', () =>
{
  // App state
  const state = {
    apiUrl: '',
    apiKey: '',
    isConnected: false,
    watches: {},
    currentWatchId: null,
    connectFromStorage: false
  };

  // DOM elements
  const elements = {
    // Connection
    connectionForm: document.getElementById('connectionForm'),
    apiUrlInput: document.getElementById('apiUrl'),
    apiKeyInput: document.getElementById('apiKey'),
    togglePasswordBtn: document.getElementById('togglePassword'),
    statusIndicator: document.getElementById('statusIndicator'),
    connectionStatus: document.getElementById('connectionStatus'),
    connectionSettingsBtn: document.getElementById('connectionSettingsBtn'),

    // Connection Settings Modal
    connectionSettingsModal: document.getElementById('connectionSettingsModal'),
    updateConnectionForm: document.getElementById('updateConnectionForm'),
    updateApiUrlInput: document.getElementById('updateApiUrl'),
    updateApiKeyInput: document.getElementById('updateApiKey'),
    toggleUpdatePasswordBtn: document.getElementById('toggleUpdatePassword'),
    closeConnectionSettingsModalBtn: document.getElementById('closeConnectionSettingsModal'),
    cancelUpdateConnectionBtn: document.getElementById('cancelUpdateConnection'),
    disconnectBtn: document.getElementById('disconnectBtn'),

    // Panels
    setupPanel: document.getElementById('setupPanel'),
    appMain: document.getElementById('appMain'),

    // Watch List
    watchList: document.getElementById('watchList'),
    searchWatches: document.getElementById('searchWatches'),
    addWatchBtn: document.getElementById('addWatchBtn'),

    // Watch Details
    welcomeScreen: document.getElementById('welcomeScreen'),
    watchDetails: document.getElementById('watchDetails'),
    watchTitle: document.getElementById('watchTitle'),
    watchUrl: document.getElementById('watchUrl'),
    lastChecked: document.getElementById('lastChecked'),
    statusBadge: document.getElementById('statusBadge'),
    editWatchBtn: document.getElementById('editWatchBtn'),
    checkNowBtn: document.getElementById('checkNowBtn'),
    deleteWatchBtn: document.getElementById('deleteWatchBtn'),

    // Tabs
    tabButtons: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content'),
    historyList: document.getElementById('historyList'),

    // Settings
    watchFilters: document.getElementById('watchFilters'),
    watchTags: document.getElementById('watchTags'),
    watchMethod: document.getElementById('watchMethod'),
    watchHeaders: document.getElementById('watchHeaders'),
    saveSettingsBtn: document.getElementById('saveSettingsBtn'),

    // Preview
    previewFrame: document.getElementById('previewFrame'),

    // Add Watch Modal
    addWatchModal: document.getElementById('addWatchModal'),
    addWatchForm: document.getElementById('addWatchForm'),
    newWatchUrl: document.getElementById('newWatchUrl'),
    newWatchTitle: document.getElementById('newWatchTitle'),
    newWatchTags: document.getElementById('newWatchTags'),
    closeAddModal: document.getElementById('closeAddModal'),
    cancelAddWatch: document.getElementById('cancelAddWatch'),

    // Delete Modal
    confirmDeleteModal: document.getElementById('confirmDeleteModal'),
    confirmDeleteBtn: document.getElementById('confirmDeleteBtn'),
    cancelDeleteBtn: document.getElementById('cancelDeleteBtn'),
    closeDeleteModal: document.getElementById('closeDeleteModal'),

    // Loading
    loadingOverlay: document.getElementById('loadingOverlay'),
    loadingText: document.getElementById('loadingText'),

    // Toasts
    toastContainer: document.getElementById('toastContainer')
  };

  // Initialize the application
  function init()
  {
    // Attach event listeners
    attachEventListeners();

    // Check for saved connection
    checkSavedConnection();
  }

  // Attach all event listeners
  function attachEventListeners()
  {
    // Connection form
    elements.connectionForm.addEventListener('submit', handleConnect);
    elements.togglePasswordBtn.addEventListener('click', togglePasswordVisibility);
    elements.connectionSettingsBtn.addEventListener('click', openConnectionSettingsModal);

    // Connection Settings Modal
    elements.updateConnectionForm.addEventListener('submit', handleUpdateConnection);
    elements.toggleUpdatePasswordBtn.addEventListener('click', toggleUpdatePasswordVisibility);
    elements.closeConnectionSettingsModalBtn.addEventListener('click', closeConnectionSettingsModal);
    elements.cancelUpdateConnectionBtn.addEventListener('click', closeConnectionSettingsModal);
    elements.disconnectBtn.addEventListener('click', handleDisconnect);

    // Watch list
    elements.addWatchBtn.addEventListener('click', openAddWatchModal);
    elements.searchWatches.addEventListener('input', handleSearchWatches);

    // Watch details
    elements.checkNowBtn.addEventListener('click', handleCheckNow);
    elements.deleteWatchBtn.addEventListener('click', openDeleteModal);

    // Tabs
    elements.tabButtons.forEach(button =>
    {
      button.addEventListener('click', () => switchTab(button.dataset.tab));
    });

    // Settings
    elements.saveSettingsBtn.addEventListener('click', handleSaveSettings);

    // Add Watch Modal
    elements.addWatchForm.addEventListener('submit', handleAddWatch);
    elements.closeAddModal.addEventListener('click', closeAddWatchModal);
    elements.cancelAddWatch.addEventListener('click', closeAddWatchModal);

    // Delete Modal
    elements.confirmDeleteBtn.addEventListener('click', handleDeleteWatch);
    elements.cancelDeleteBtn.addEventListener('click', closeDeleteModal);
    elements.closeDeleteModal.addEventListener('click', closeDeleteModal);
  }

  // Check if there's a saved connection
  function checkSavedConnection()
  {
    const savedApiUrl = localStorage.getItem('apiUrl');
    const savedApiKey = localStorage.getItem('apiKey');

    if (savedApiUrl && savedApiKey) {
      elements.apiUrlInput.value = savedApiUrl;
      elements.apiKeyInput.value = savedApiKey;
      state.connectFromStorage = true;
      handleConnect(new Event('submit'));
    }
  }

  // Toggle password visibility
  function togglePasswordVisibility()
  {
    const type = elements.apiKeyInput.type === 'password' ? 'text' : 'password';
    elements.apiKeyInput.type = type;

    const icon = elements.togglePasswordBtn.querySelector('i');
    icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
  }

  // Toggle update password visibility
  function toggleUpdatePasswordVisibility()
  {
    const type = elements.updateApiKeyInput.type === 'password' ? 'text' : 'password';
    elements.updateApiKeyInput.type = type;

    const icon = elements.toggleUpdatePasswordBtn.querySelector('i');
    icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
  }

  // Handle connection
  async function handleConnect(event)
  {
    event.preventDefault();

    const apiUrl = elements.apiUrlInput.value.trim();
    const apiKey = elements.apiKeyInput.value.trim();

    if (!apiUrl || !apiKey) {
      showToast('Please enter both API URL and API Key', 'error');
      return;
    }

    state.apiUrl = apiUrl;
    state.apiKey = apiKey;

    showLoading('Connecting...');

    try {
      await testConnection();

      // Save connection details
      localStorage.setItem('apiUrl', apiUrl);
      localStorage.setItem('apiKey', apiKey);

      // Update UI
      updateConnectionStatus(true);
      showMainApp();

      // Load watches
      await loadWatches();
    } catch (error) {
      if (!state.connectFromStorage) {
        showToast(`Connection failed: ${error.message}`, 'error');
      }
      updateConnectionStatus(false);
    } finally {
      hideLoading();
      state.connectFromStorage = false;
    }
  }

  // Test API connection
  async function testConnection()
  {
    try {
      // Try different endpoints that might exist in the API
      let response;

      // First try /watches endpoint
      response = await makeApiRequest('GET', 'systeminfo');
      if (response.ok) return true;
    } catch (error) {
      console.error('Connection test failed:', error);
      throw new Error('Could not connect to the API');
    }
  }

  // Update connection status in UI
  function updateConnectionStatus(isConnected)
  {
    state.isConnected = isConnected;

    if (isConnected) {
      elements.statusIndicator.classList.add('connected');
      elements.connectionStatus.textContent = 'Connected';
    } else {
      elements.statusIndicator.classList.remove('connected');
      elements.connectionStatus.textContent = 'Disconnected';
    }
  }

  // Show main app UI
  function showMainApp()
  {
    elements.setupPanel.classList.add('hidden');
    elements.appMain.classList.remove('hidden');
  }

  // Load all watches
  async function loadWatches()
  {
    showLoading('Loading watches...');

    try {
      let response;
      let data;

      // Try both watch and watches endpoints
      try {
        response = await makeApiRequest('GET', 'watch');
        data = await response.json();
      } catch (e) {
        console.log('watch endpoint failed, trying watches');
        response = await makeApiRequest('GET', 'watches');
        data = await response.json();
      }

      console.log('Watches data:', data);

      // Ensure data is an object
      if (Array.isArray(data)) {
        // Convert array to object with IDs as keys
        const watchesObj = {};
        data.forEach((watch, index) =>
        {
          const id = watch.uuid || watch.id || `watch-${index}`;
          watchesObj[id] = watch;
        });
        state.watches = watchesObj;
      } else {
        state.watches = data;
      }

      renderWatchList();

      if (Object.keys(state.watches).length === 0) {
        showToast('No watches found. Create your first watch!', 'info');
      }
    } catch (error) {
      console.error('Error loading watches:', error);
      showToast('Failed to load watches', 'error');
    } finally {
      hideLoading();
    }
  }

  // Render watch list in sidebar
  function renderWatchList()
  {
    elements.watchList.innerHTML = '';

    const searchTerm = elements.searchWatches.value.toLowerCase();
    let hasMatches = false;

    for (const [id, watch] of Object.entries(state.watches)) {
      // Apply search filter
      if (searchTerm) {
        const title = (watch.title || '').toLowerCase();
        const url = (watch.url || '').toLowerCase();

        if (!title.includes(searchTerm) && !url.includes(searchTerm)) {
          continue;
        }
      }

      hasMatches = true;

      const li = document.createElement('li');
      li.className = 'watch-item';
      li.dataset.id = id;

      if (state.currentWatchId === id) {
        li.classList.add('active');
      }

      const hasChanged = watch.last_changed !== "0" && watch.last_changed;
      const statusClass = hasChanged ? 'changed' : 'unchanged';
      const statusText = hasChanged ? 'Changed' : 'No Change';

      li.innerHTML = `
        <div class="watch-item-title">${watch.title || 'Untitled Watch'}</div>
        <div class="watch-item-url">${watch.url}</div>
        <div class="watch-item-status">
          <span class="watch-item-badge badge-${statusClass}">${statusText}</span>
          <span class="watch-item-time">${formatDate(watch.last_checked) || 'Never checked'}</span>
        </div>
      `;

      li.addEventListener('click', () => selectWatch(id));
      elements.watchList.appendChild(li);
    }

    if (!hasMatches) {
      elements.watchList.innerHTML = `
        <div class="empty-state">
          <p>No watches found matching "${searchTerm}"</p>
        </div>
      `;
    }
  }

  // Select a watch to display details
  function selectWatch(watchId)
  {
    state.currentWatchId = watchId;

    // Update active state in list
    document.querySelectorAll('.watch-item').forEach(item =>
    {
      item.classList.toggle('active', item.dataset.id === watchId);
    });

    // Show watch details panel
    elements.welcomeScreen.classList.add('hidden');
    elements.watchDetails.classList.remove('hidden');

    // Load watch details
    const watch = state.watches[watchId];

    // Update UI
    elements.watchTitle.textContent = watch.title || 'Untitled Watch';
    elements.watchUrl.textContent = watch.url || '';
    elements.lastChecked.textContent = formatDate(watch.last_checked) || 'Never';

    const hasChanged = watch.last_changed !== "0" && watch.last_changed;
    elements.statusBadge.textContent = hasChanged ? 'Changed' : 'No Change';
    elements.statusBadge.className = 'status-badge';
    elements.statusBadge.classList.add(hasChanged ? 'status-changed' : 'status-unchanged');

    // Load settings
    elements.watchFilters.value = watch.include_filters || '';
    elements.watchTags.value = Array.isArray(watch.tags) ? watch.tags.join(', ') : '';
    elements.watchMethod.value = watch.method || 'GET';

    try {
      const headers = typeof watch.headers === 'object' ? watch.headers : {};
      elements.watchHeaders.value = JSON.stringify(headers, null, 2);
    } catch (e) {
      elements.watchHeaders.value = '{}';
    }

    // Load history tab
    loadWatchHistory(watchId);

    // Set up preview tab
    elements.previewFrame.src = watch.url;
  }

  // Load watch history
  async function loadWatchHistory(watchId)
  {
    elements.historyList.innerHTML = `
      <div class="empty-state">
        <i class="fas fa-spinner fa-spin"></i>
        <p>Loading history...</p>
      </div>
    `;

    try {
      const response = await makeApiRequest('GET', `/watch/${watchId}/history`);
      const historyData = await response.json();
      console.log('History response:', historyData);

      // Convert object with timestamps as keys to array of objects
      const historyItems = Object.entries(historyData).map(([timestamp, path]) => ({
        timestamp: parseInt(timestamp),
        path: path
      }));

      console.log('Processed history items:', historyItems);

      if (!historyItems || historyItems.length === 0) {
        elements.historyList.innerHTML = `
          <div class="empty-state">
            <i class="fas fa-history"></i>
            <p>No history available yet</p>
          </div>
        `;
        return;
      }

      renderHistoryList(historyItems);
    } catch (error) {
      console.error('Error loading history:', error);
      elements.historyList.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-exclamation-triangle"></i>
          <p>Failed to load history: ${error.message}</p>
        </div>
      `;
    }
  }

  // Render history list
  function renderHistoryList(historyItems)
  {
    elements.historyList.innerHTML = '';

    historyItems.sort((a, b) => b.timestamp - a.timestamp) // Sort newest first
      .forEach(item =>
      {
        const timestamp = new Date(item.timestamp * 1000);

        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';

        historyItem.innerHTML = `
          <div class="history-info">
            <div class="history-date">${timestamp.toLocaleDateString()}</div>
            <div class="history-time">${timestamp.toLocaleTimeString()}</div>
          </div>
        `;

        elements.historyList.appendChild(historyItem);
      });

    if (elements.historyList.children.length === 0) {
      elements.historyList.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-history"></i>
          <p>No history items to display</p>
        </div>
      `;
    }
  }

  // Switch between tabs
  function switchTab(tabName)
  {
    // Update tab buttons
    elements.tabButtons.forEach(button =>
    {
      button.classList.toggle('active', button.dataset.tab === tabName);
    });

    // Update tab content
    elements.tabContents.forEach(content =>
    {
      const isActive = content.id === `${tabName}Tab`;
      content.classList.toggle('active', isActive);
    });
  }

  // Handle search in watch list
  function handleSearchWatches()
  {
    renderWatchList();
  }

  // Handle check now button
  async function handleCheckNow()
  {
    if (!state.currentWatchId) return;

    showLoading('Checking for changes...');

    try {
      await makeApiRequest('GET', `/watch/${state.currentWatchId}/recheck=1`);
      showToast('Check triggered successfully', 'success');

      // Reload watch data
      await loadWatches();
      selectWatch(state.currentWatchId);
    } catch (error) {
      console.error('Error triggering check:', error);
      showToast('Failed to trigger check', 'error');
    } finally {
      hideLoading();
    }
  }

  // Handle save settings
  async function handleSaveSettings()
  {
    if (!state.currentWatchId) return;

    showLoading('Saving settings...');

    try {
      const watch = state.watches[state.currentWatchId];

      const updateData = {
        url: watch.url,
        title: watch.title || '',
      };

      // Get filters
      const filters = elements.watchFilters.value.trim();
      if (filters) updateData.include_filters = filters;

      // Get tags
      const tagsText = elements.watchTags.value.trim();
      if (tagsText) {
        updateData.tags = tagsText.split(',').map(tag => tag.trim()).filter(tag => tag);
      }

      // Get method
      updateData.method = elements.watchMethod.value;

      // Get headers
      try {
        const headersText = elements.watchHeaders.value.trim();
        if (headersText) {
          updateData.headers = JSON.parse(headersText);
        }
      } catch (e) {
        showToast('Invalid JSON in headers field', 'error');
        hideLoading();
        return;
      }

      // Update watch
      await makeApiRequest('PUT', `/watch/${state.currentWatchId}`, updateData);

      // Reload watches
      await loadWatches();
      selectWatch(state.currentWatchId);

      showToast('Paramètres mis à jour', 'success');
    } catch (error) {
      console.error('Error saving settings:', error);
      showToast('Erreur de la mise à jour des paramètres', 'error');
    } finally {
      hideLoading();
    }
  }

  // Open add watch modal
  function openAddWatchModal()
  {
    elements.addWatchModal.classList.add('active');
    elements.newWatchUrl.focus();
  }

  // Close add watch modal
  function closeAddWatchModal()
  {
    elements.addWatchModal.classList.remove('active');
    elements.addWatchForm.reset();
  }

  // Handle add watch form submission
  async function handleAddWatch(event)
  {
    event.preventDefault();

    const url = elements.newWatchUrl.value.trim();
    if (!url) {
      showToast('L\'adresse est requise', 'error');
      return;
    }

    showLoading('Creating watch...');

    try {
      const data = {
        url: url,
        title: elements.newWatchTitle.value.trim() || `Watch for ${url}`
      };

      // Add tags if provided
      const tagsText = elements.newWatchTags.value.trim();
      if (tagsText) {
        data.tags = tagsText.split(',').map(tag => tag.trim()).filter(tag => tag);
      }

      const response = await makeApiRequest('POST', '/watch', data);
      const newWatch = await response.json();

      closeAddWatchModal();

      // Reload watches and select the new one
      await loadWatches();

      if (newWatch && newWatch.id) {
        selectWatch(newWatch.id);
      }

      showToast('Watch created successfully', 'success');
    } catch (error) {
      console.error('Erreur lors de la création de la watch:', error);
      showToast('Erreur lors de la création de la watch', 'error');
    } finally {
      hideLoading();
    }
  }

  // Open delete confirmation modal
  function openDeleteModal()
  {
    elements.confirmDeleteModal.classList.add('active');
  }

  // Close delete confirmation modal
  function closeDeleteModal()
  {
    elements.confirmDeleteModal.classList.remove('active');
  }

  // Open connection settings modal
  function openConnectionSettingsModal()
  {
    // Populate fields with current values
    elements.updateApiUrlInput.value = state.apiUrl;
    elements.updateApiKeyInput.value = state.apiKey;

    // Show modal
    elements.connectionSettingsModal.classList.add('active');
  }

  // Close connection settings modal
  function closeConnectionSettingsModal()
  {
    elements.connectionSettingsModal.classList.remove('active');
  }

  // Handle update connection form submission
  async function handleUpdateConnection(event)
  {
    event.preventDefault();

    const apiUrl = elements.updateApiUrlInput.value.trim();
    const apiKey = elements.updateApiKeyInput.value.trim();

    if (!apiUrl || !apiKey) {
      showToast('Entrer l\'adresse de l\'API ainsi que la clé d\'API correspondante', 'error');
      return;
    }

    showLoading('Updating connection...');

    // Save old values in case we need to revert
    const oldApiUrl = state.apiUrl;
    const oldApiKey = state.apiKey;

    // Update state with new values
    state.apiUrl = apiUrl;
    state.apiKey = apiKey;

    try {
      await testConnection();

      // Save new connection details
      localStorage.setItem('apiUrl', apiUrl);
      localStorage.setItem('apiKey', apiKey);

      // Update UI
      updateConnectionStatus(true);
      closeConnectionSettingsModal();

      // Reload watches with new connection
      await loadWatches();

      showToast('Mise à jour effectué', 'success');
    } catch (error) {
      console.error('Connection update failed:', error);

      // Revert to old values
      state.apiUrl = oldApiUrl;
      state.apiKey = oldApiKey;

      showToast(`Echec de la mise à jour des information de connection: ${error.message}`, 'error');
      updateConnectionStatus(true); // Keep the connected status since we reverted
    } finally {
      hideLoading();
    }
  }

  // Handle disconnect button
  function handleDisconnect()
  {
    // Clear state
    state.apiUrl = '';
    state.apiKey = '';
    state.isConnected = false;
    state.watches = {};
    state.currentWatchId = null;

    // Clear local storage
    localStorage.removeItem('apiUrl');
    localStorage.removeItem('apiKey');

    // Update UI
    updateConnectionStatus(false);
    closeConnectionSettingsModal();

    // Show setup panel
    elements.appMain.classList.add('hidden');
    elements.setupPanel.classList.remove('hidden');

    showToast('Disconnected successfully', 'info');
  }

  // Handle delete watch confirmation
  async function handleDeleteWatch()
  {
    if (!state.currentWatchId) return;

    showLoading('Suppression en cours...');

    try {
      await makeApiRequest('DELETE', `/watch/${state.currentWatchId}`);

      closeDeleteModal();

      // Remove from state
      delete state.watches[state.currentWatchId];

      // Reset current watch
      state.currentWatchId = null;

      // Show welcome screen
      elements.watchDetails.classList.add('hidden');
      elements.welcomeScreen.classList.remove('hidden');

      // Update watch list
      renderWatchList();

      showToast('Suppression effectuée', 'success');
    } catch (error) {
      console.error('Error deleting watch:', error);
      showToast('Failed to delete watch', 'error');
    } finally {
      hideLoading();
    }
  }

  // Show loading overlay
  function showLoading(message = 'Loading...')
  {
    elements.loadingText.textContent = message;
    elements.loadingOverlay.classList.add('active');
  }

  // Hide loading overlay
  function hideLoading()
  {
    elements.loadingOverlay.classList.remove('active');
  }

  // Show toast notification
  function showToast(message, type = 'info')
  {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    let icon;
    switch (type) {
      case 'success': icon = 'check-circle'; break;
      case 'error': icon = 'exclamation-circle'; break;
      case 'warning': icon = 'exclamation-triangle'; break;
      default: icon = 'info-circle';
    }

    toast.innerHTML = `
      <i class="fas fa-${icon}"></i>
      <span class="toast-message">${message}</span>
    `;

    elements.toastContainer.appendChild(toast);

    // Remove after animation
    setTimeout(() =>
    {
      toast.remove();
    }, 5000);
  }

  // Make API request
  async function makeApiRequest(method, endpoint, data = null)
  {
    // Remove leading slash if present in endpoint
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;

    // Try API path format: /api/v1/{endpoint}
    const url = `${state.apiUrl}/api/v1/${cleanEndpoint}`;

    console.log('Making API request to:', url);

    const headers = {
      'Content-Type': 'application/json',
      'X-API-Key': state.apiKey
    };

    const options = {
      method,
      headers,
      credentials: 'same-origin'
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    return fetch(url, options);
  }

  // Format date string
  function formatDate(timestamp)
  {
    if (!timestamp) return '';

    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
  }

  // Initialize app
  init();
});