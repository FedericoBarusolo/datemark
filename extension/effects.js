/**
 * UI Effects and Visual Enhancements
 * Handles animations, visual feedback, and non-functional UI improvements
 */

// Sparkle effect for buttons
function createSparkles(button) {
  const sparkleCount = 3;
  for (let i = 0; i < sparkleCount; i++) {
    setTimeout(() => {
      const sparkle = document.createElement('div');
      sparkle.className = 'sparkle';
      sparkle.style.left = Math.random() * 100 + '%';
      sparkle.style.top = Math.random() * 100 + '%';
      sparkle.style.animation = 'sparkle 0.6s ease-out';
      button.appendChild(sparkle);

      setTimeout(() => sparkle.remove(), 600);
    }, i * 100);
  }
}

// Initialize sparkle effect on extract button
function initExtractButtonEffects() {
  const extractBtn = document.getElementById('extractBtn');

  if (extractBtn) {
    extractBtn.addEventListener('mouseenter', function() {
      if (!this.disabled) {
        createSparkles(this);
      }
    });
  }
}

// Initialize all UI effects when DOM is ready
function initUIEffects() {
  initExtractButtonEffects();
  // Add more UI effects here as needed
}

// Auto-initialize if DOM is already loaded, otherwise wait
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initUIEffects);
} else {
  initUIEffects();
}