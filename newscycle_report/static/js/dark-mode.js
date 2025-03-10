// Dark mode detection and application
function initDarkMode() {
  // Check for saved preference in localStorage
  const savedPreference = localStorage.getItem('darkMode');
  
  // Check if the OS prefers dark mode
  const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  // Apply dark mode class based on saved preference or OS preference
  if (savedPreference === 'dark' || (savedPreference === null && prefersDarkMode)) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
  
  // Listen for changes in OS preference
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    // Only apply OS preference if no saved preference exists
    if (localStorage.getItem('darkMode') === null) {
      if (e.matches) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  });
  
  // Create toggle button if it doesn't exist
  if (!document.getElementById('dark-mode-toggle')) {
    createDarkModeToggle();
  }
}

// Create toggle button for manual switching
function createDarkModeToggle() {
  // Create button element
  const toggle = document.createElement('button');
  toggle.id = 'dark-mode-toggle';
  toggle.innerHTML = '🌙';
  toggle.title = 'Toggle Dark Mode';
  
  // Style the button
  Object.assign(toggle.style, {
    position: 'fixed',
    bottom: '80px',
    right: '20px',
    zIndex: '1000',
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    border: 'none',
    backgroundColor: '#cbd5e0', // Light gray
    fontSize: '1.2rem',
    cursor: 'pointer',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    boxShadow: '0 2px 10px rgba(0,0,0,0.2)'
  });
  
  // Update button appearance based on current mode
  updateToggleAppearance(toggle);
  
  // Add click event listener
  toggle.addEventListener('click', () => {
    // Toggle dark mode
    if (document.documentElement.classList.contains('dark')) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('darkMode', 'light');
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('darkMode', 'dark');
    }
    
    // Update button appearance
    updateToggleAppearance(toggle);
  });
  
  // Add button to document
  document.body.appendChild(toggle);
}

// Update toggle button appearance based on current mode
function updateToggleAppearance(toggle) {
  if (document.documentElement.classList.contains('dark')) {
    toggle.innerHTML = '☀️';
    toggle.title = 'Switch to Light Mode';
    toggle.style.backgroundColor = '#4a5568'; // Dark gray
  } else {
    toggle.innerHTML = '🌙';
    toggle.title = 'Switch to Dark Mode';
    toggle.style.backgroundColor = '#cbd5e0'; // Light gray
  }
}

// Initialize dark mode when DOM content is loaded
document.addEventListener('DOMContentLoaded', initDarkMode);
