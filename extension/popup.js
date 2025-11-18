let allEvents = [];
let selectedEventIndices = new Set();

// Rotating placeholder examples
const placeholderExamples = [
  'only rock concerts',
  'events in May',
  'only free events',
  'events in London only',
  'events in the weekend',
  'only events after 19:00',
  'workshops and seminars'
];

let placeholderIndex = 0;
let placeholderInterval = null;
let typingInterval = null;
let isUserFocused = false;

// Typing animation for placeholder
function typeText(element, text, callback) {
  let charIndex = 0;
  element.placeholder = '';

  clearInterval(typingInterval);
  typingInterval = setInterval(() => {
    if (charIndex < text.length) {
      element.placeholder += text.charAt(charIndex);
      charIndex++;
    } else {
      clearInterval(typingInterval);
      if (callback) callback();
    }
  }, 50); // Speed of typing (50ms per character)
}

// Initialize rotating placeholders
function initPlaceholderRotation() {
  const userQueryInput = document.getElementById('userQuery');

  // Type the first placeholder immediately
  typeText(userQueryInput, placeholderExamples[0]);

  // Start rotation
  placeholderInterval = setInterval(() => {
    if (!isUserFocused && !userQueryInput.value) {
      placeholderIndex = (placeholderIndex + 1) % placeholderExamples.length;
      typeText(userQueryInput, placeholderExamples[placeholderIndex]);
    }
  }, 4000); // Wait 4 seconds between phrases (includes typing time + display time)

  // Handle focus events
  userQueryInput.addEventListener('focus', () => {
    isUserFocused = true;
    clearInterval(typingInterval);
    if (!userQueryInput.value) {
      userQueryInput.placeholder = 'e.g., only rock concerts';
    }
  });

  userQueryInput.addEventListener('blur', () => {
    isUserFocused = false;
    if (!userQueryInput.value) {
      typeText(userQueryInput, placeholderExamples[placeholderIndex]);
    }
  });
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
  initPlaceholderRotation();
  initCharacterCounter();
});

// Character counter for user query
function initCharacterCounter() {
  const userQueryInput = document.getElementById('userQuery');
  const charCount = document.getElementById('charCount');

  userQueryInput.addEventListener('input', () => {
    charCount.textContent = userQueryInput.value.length;
  });
}

// Send message to background script
function sendMessage(action, data = {}) {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ action, ...data }, resolve);
  });
}

// Extract inner text from page
function extractText() {
  return document.body.innerText;
}

// Format date for input field (YYYY-MM-DD)
function formatDateForInput(dateStr) {
  const date = new Date(dateStr);
  return date.toISOString().split('T')[0];
}

// Format time for input field (HH:MM)
function formatTimeForInput(dateStr) {
  const date = new Date(dateStr);
  return date.toTimeString().slice(0, 5);
}

// Check if event spans multiple days
function isMultiDayEvent(startTime, endTime) {
  const start = new Date(startTime);
  const end = new Date(endTime);
  return start.toDateString() !== end.toDateString();
}

// Update event data when edited
function updateEventField(index, field, value) {
  if (!allEvents[index]) return;

  const event = allEvents[index];

  // Clone start and end times for validation
  let start = new Date(event.start_time);
  let end = new Date(event.end_time);

  // Apply temporary edit for validation
  if (field === 'start_date' || field === 'end_date') {
    const [year, month, day] = value.split('-');
    if (field === 'start_date') start.setFullYear(year, month - 1, day);
    else end.setFullYear(year, month - 1, day);
  } else if (field === 'start_time_only' || field === 'end_time_only') {
    const [hours, minutes] = value.split(':');
    if (field === 'start_time_only') start.setHours(hours, minutes);
    else end.setHours(hours, minutes);
  }

  // Validate time order
  if (end <= start) {
    alert('End date/time must be after the start date/time.');
    // Cancel the edit by resetting the field to the previous value
    revertInputField(index, field, event);
    return;
  }

  // Apply the valid change
  if (field === 'title' || field === 'location') {
    event[field] = value;
  } else if (field === 'start_date' || field === 'end_date') {
    const timeField = field === 'start_date' ? 'start_time' : 'end_time';
    const currentDate = new Date(event[timeField]);
    const [year, month, day] = value.split('-');
    currentDate.setFullYear(year, month - 1, day);
    event[timeField] = currentDate.toISOString();
  } else if (field === 'start_time_only' || field === 'end_time_only') {
    const timeField = field === 'start_time_only' ? 'start_time' : 'end_time';
    const currentDate = new Date(event[timeField]);
    const [hours, minutes] = value.split(':');
    currentDate.setHours(hours, minutes);
    event[timeField] = currentDate.toISOString();
  }

  console.log('Updated event:', event);
}

function revertInputField(index, field, event) {
  const selector = `.editable-field[data-index="${index}"][data-field="${field}"]`;
  const input = document.querySelector(selector);

  if (!input) return;

  if (field === 'start_date' || field === 'end_date') {
    const dateStr = field === 'start_date' ? event.start_time : event.end_time;
    input.value = formatDateForInput(dateStr);
  } else if (field === 'start_time_only' || field === 'end_time_only') {
    const timeStr = field === 'start_time_only' ? event.start_time : event.end_time;
    input.value = formatTimeForInput(timeStr);
  }
}

document.getElementById('extractBtn').addEventListener('click', async () => {
  const extractBtn = document.getElementById('extractBtn');
  const originalText = extractBtn.innerHTML;
  const userQuery = document.getElementById('userQuery').value.trim();

  extractBtn.disabled = true;
  extractBtn.innerHTML = 'Extracting...';

  try {
    const [tab] = await chrome.tabs.query({active: true, currentWindow: true});

    const extracted = await chrome.scripting.executeScript({
      target: {tabId: tab.id},
      function: extractText
    });

    const text = extracted[0].result;

    const payload = {
      input_text: text,
      url: location.href
    };

    // Add user query if provided
    if (userQuery) {
      payload.user_query = userQuery;
    }

    const result = await sendMessage('fetchList', {
      data: payload
    });

    if (!result.success) {
      throw new Error(result.error);
    }

    displayEvents(result.data);

    extractBtn.innerHTML = originalText;
    extractBtn.disabled = false;
  } catch (error) {
    extractBtn.innerHTML = 'Error - Try Again';
    alert(error);
    setTimeout(() => {
      extractBtn.innerHTML = originalText;
      extractBtn.disabled = false;
    }, 2000);
  }
});


function displayEvents(data) {
  const resultsDiv = document.getElementById('results');

  console.log(data);

  const parsed_data = data;
  console.log(parsed_data.events);

  // Store events globally
  allEvents = parsed_data.events || [];
  selectedEventIndices.clear();

  // Check if there are events in the response
  if (!allEvents || allEvents.length === 0) {
    resultsDiv.innerHTML = '<p class="no-events">No events found on this page.</p>';
    document.getElementById('submitBtn').classList.add('hidden');
    return;
  }

  // Show submit button
  document.getElementById('submitBtn').classList.remove('hidden');
  document.getElementById('submitBtn').disabled = true;

  // Build HTML for events
  let html = '<div class="events-container">';

  // Header with event count and selected count
  html += `
    <div class="events-header">
      <h3>Found ${allEvents.length} event${allEvents.length > 1 ? 's' : ''}</h3>
      <span class="selected-count" id="selectedCount">0 selected</span>
    </div>
  `;

  // Select all checkbox
  html += `
    <div class="select-all-container">
      <input type="checkbox" id="selectAll">
      <label for="selectAll">Select All</label>
    </div>
  `;

  allEvents.forEach((event, index) => {
    const startDateInput = formatDateForInput(event.start_time);
    const endDateInput = formatDateForInput(event.end_time);
    const startTimeInput = formatTimeForInput(event.start_time);
    const endTimeInput = formatTimeForInput(event.end_time);

    html += `
      <div class="event-card" data-index="${index}">
        <div class="event-header">
          <input type="checkbox" class="event-checkbox" data-index="${index}">
          <div style="flex: 1;">
            <span contenteditable="true" class="editable-field editable-title" data-index="${index}" data-field="title">${event.title}</span>
            <div class="event-details">`;

    html += `
            <p>
              <strong>Start:</strong>
              <input type="date" class="editable-field" data-index="${index}" data-field="start_date" value="${startDateInput}">
              <input type="time" class="editable-field" data-index="${index}" data-field="start_time_only" value="${startTimeInput}">
            </p>
            <p>
              <strong>End:</strong>
              <input type="date" class="editable-field" data-index="${index}" data-field="end_date" value="${endDateInput}">
              <input type="time" class="editable-field" data-index="${index}" data-field="end_time_only" value="${endTimeInput}">
            </p>`;

    html += `
              <p>
                <strong>Location:</strong>
                <span contenteditable="true" class="editable-field" data-index="${index}" data-field="location">${event.location}</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    `;
  });

  html += '</div>';
  resultsDiv.innerHTML = html;

  // Attach event listeners
  attachEventListeners();
  attachEditListeners();
}

function attachEditListeners() {
  // Content editable fields (title and location)
  const editableFields = document.querySelectorAll('[contenteditable="true"]');
  editableFields.forEach(field => {
    field.addEventListener('blur', function() {
      const index = parseInt(this.getAttribute('data-index'));
      const fieldName = this.getAttribute('data-field');
      updateEventField(index, fieldName, this.textContent.trim());
    });

    field.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        this.blur();
      }
    });
  });

  // Date and time inputs
  const dateTimeInputs = document.querySelectorAll('input[type="date"], input[type="time"]');
  dateTimeInputs.forEach(input => {
    input.addEventListener('change', function() {
      const index = parseInt(this.getAttribute('data-index'));
      const fieldName = this.getAttribute('data-field');
      updateEventField(index, fieldName, this.value);
    });
  });
}

function attachEventListeners() {
  // Select all checkbox
  const selectAllCheckbox = document.getElementById('selectAll');
  if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener('change', handleSelectAll);
  }

  // Individual event checkboxes
  const eventCheckboxes = document.querySelectorAll('.event-checkbox');
  eventCheckboxes.forEach(checkbox => {
    checkbox.addEventListener('change', handleEventCheckbox);
  });
}

function handleSelectAll(e) {
  const isChecked = e.target.checked;
  const eventCheckboxes = document.querySelectorAll('.event-checkbox');

  selectedEventIndices.clear();

  eventCheckboxes.forEach((checkbox, index) => {
    checkbox.checked = isChecked;
    const card = checkbox.closest('.event-card');

    if (isChecked) {
      selectedEventIndices.add(index);
      card.classList.add('selected');
    } else {
      card.classList.remove('selected');
    }
  });

  updateSelectedCount();
  logFilteredEvents();
}

function handleEventCheckbox(e) {
  const index = parseInt(e.target.getAttribute('data-index'));
  const card = e.target.closest('.event-card');

  if (e.target.checked) {
    selectedEventIndices.add(index);
    card.classList.add('selected');
  } else {
    selectedEventIndices.delete(index);
    card.classList.remove('selected');
  }

  // Update select all checkbox state
  const selectAllCheckbox = document.getElementById('selectAll');
  const eventCheckboxes = document.querySelectorAll('.event-checkbox');
  const allChecked = Array.from(eventCheckboxes).every(cb => cb.checked);
  const noneChecked = Array.from(eventCheckboxes).every(cb => !cb.checked);

  if (selectAllCheckbox) {
    selectAllCheckbox.checked = allChecked;
    selectAllCheckbox.indeterminate = !allChecked && !noneChecked;
  }

  updateSelectedCount();
  logFilteredEvents();
}

function updateSelectedCount() {
  const selectedCountEl = document.getElementById('selectedCount');
  const submitBtn = document.getElementById('submitBtn');

  if (selectedCountEl) {
    selectedCountEl.textContent = `${selectedEventIndices.size} selected`;
  }

  // Enable/disable submit button based on selection
  if (submitBtn) {
    submitBtn.disabled = selectedEventIndices.size === 0;
  }
}

function logFilteredEvents() {
  const filteredEvents = allEvents.filter((event, index) =>
    selectedEventIndices.has(index)
  );

  console.log('Selected events:', filteredEvents);
  console.log(`Total selected: ${filteredEvents.length} out of ${allEvents.length}`);
}

// Add selected items to calendar
document.getElementById('submitBtn').addEventListener('click', async () => {
  const submitBtn = document.getElementById('submitBtn');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Submitting...';

  try {
    await submitSelectedEvents();
    submitBtn.textContent = 'Submitted!';
    setTimeout(() => {
      submitBtn.textContent = 'Submit Selected Events';
      submitBtn.disabled = selectedEventIndices.size === 0;
    }, 2000);
  } catch (error) {
    submitBtn.textContent = 'Error - Try Again';
    setTimeout(() => {
      submitBtn.textContent = 'Submit Selected Events';
      submitBtn.disabled = selectedEventIndices.size === 0;
    }, 2000);
  }
});

async function submitSelectedEvents() {

  const filteredEvents = allEvents.filter((event, index) =>
    selectedEventIndices.has(index)
  );

  if (filteredEvents.length === 0) {
    showStatus('Please select at least one item', 'error');
    return;
  }

  submitSelectedEvents.disabled = true;

  // Convert selected items to calendar events
  const events = Array.from(filteredEvents).map(item => {
    return {
      summary: item.title,
      location: item.location,
      start: {
        dateTime: item.start_time,
        timeZone: item.time_zone
      },
      end: {
        dateTime: item.end_time,
        timeZone: item.time_zone
      }
    };
  });

  const result = await sendMessage('addToCalendar', { events });

  if (result.success) {
    const successCount = result.results.filter(r => r.success).length;
    showStatus(`Added ${successCount} of ${events.length} events to calendar`, 'success');

    // Uncheck all checkboxes
    filteredEvents.forEach(cb => cb.checked = false);
  } else {
    showStatus('Failed to add events: ' + result.error, 'error');
  }

  addToCalendarBtn.disabled = false;
}

function showStatus(message, type) {
  console.log(`[${type.toUpperCase()}] ${message}`);
}