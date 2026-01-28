/**
 * PRYNTOR LANDING PAGE - APPLICATION LOGIC
 * Handles form mode switching, animations, and interactions
 */

(function() {
  'use strict';

  // ==================== UTILITIES ====================

  /**
   * Debounce function to limit event handler calls
   */
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // ==================== FORM MODE SWITCHING ====================

  function initFormModeToggle() {
    const toggleButtons = document.querySelectorAll('.mode-toggle-btn');
    const forms = document.querySelectorAll('.form');

    toggleButtons.forEach(button => {
      button.addEventListener('click', () => {
        const mode = button.getAttribute('data-mode');

        // Update button states
        toggleButtons.forEach(btn => {
          btn.classList.remove('active');
          btn.setAttribute('aria-selected', 'false');
        });
        button.classList.add('active');
        button.setAttribute('aria-selected', 'true');

        // Update form visibility
        forms.forEach(form => {
          form.classList.remove('active');
          form.style.display = 'none';
        });

        // Show selected form
        const targetFormId = mode === 'waitlist' ? 'waitlist-form' : 'contact-form-panel';
        const targetForm = document.getElementById(targetFormId);
        if (targetForm) {
          targetForm.classList.add('active');
          targetForm.style.display = 'block';
        }
      });
    });
  }

  // ==================== FORM SUBMISSION ====================

  function initFormHandling() {
    const forms = document.querySelectorAll('form[data-netlify]');

    forms.forEach(form => {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitButton = form.querySelector('button[type="submit"]');
        const successMessage = form.querySelector('.form-success');
        const formData = new FormData(form);

        // Check honeypot
        if (formData.get('bot-field')) {
          console.warn('Bot detected');
          return;
        }

        // Disable submit button
        if (submitButton) {
          submitButton.disabled = true;
          submitButton.textContent = 'Sending...';
        }

        try {
          // For Netlify Forms
          const response = await fetch('/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams(formData).toString()
          });

          if (response.ok) {
            // Show success message
            if (successMessage) {
              successMessage.style.display = 'block';
              successMessage.setAttribute('role', 'alert');
            }

            // Reset form
            form.reset();

            // Re-enable button after delay
            setTimeout(() => {
              if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = form.id === 'waitlist-form' ? 'Request Access' : 'Send Message';
              }
              if (successMessage) {
                successMessage.style.display = 'none';
              }
            }, 5000);
          } else {
            throw new Error('Form submission failed');
          }
        } catch (error) {
          console.error('Form submission error:', error);
          alert('There was an error submitting the form. Please try emailing lebo@pryntor.co.za directly.');

          // Re-enable button
          if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = form.id === 'waitlist-form' ? 'Request Access' : 'Send Message';
          }
        }
      });
    });
  }

  // ==================== SCROLL ANIMATIONS ====================

  function initScrollAnimations() {
    const sections = document.querySelectorAll('.fade-in-section');

    // Intersection Observer options
    const options = {
      root: null,
      rootMargin: '0px',
      threshold: 0.1
    };

    // Callback for intersection
    const callback = (entries, observer) => {
      entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
          // Add staggered delay
          setTimeout(() => {
            entry.target.classList.add('visible');
          }, index * 150);

          // Unobserve after animation
          observer.unobserve(entry.target);
        }
      });
    };

    // Create observer
    const observer = new IntersectionObserver(callback, options);

    // Observe all sections
    sections.forEach(section => {
      observer.observe(section);
    });
  }

  // ==================== CONTROL LINE ANIMATION ====================

  function initControlLineAnimation() {
    const controlLine = document.querySelector('.control-line');
    if (!controlLine) return;

    let scrollY = 0;
    let ticking = false;

    const updateControlLine = () => {
      const scrollPercentage = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight);
      const translateValue = scrollPercentage * 100;

      // Subtle movement (max 10px)
      controlLine.style.transform = `translateY(${Math.min(translateValue / 10, 10)}px)`;

      ticking = false;
    };

    const onScroll = () => {
      scrollY = window.scrollY;

      if (!ticking) {
        window.requestAnimationFrame(updateControlLine);
        ticking = true;
      }
    };

    // Debounced scroll listener
    window.addEventListener('scroll', debounce(onScroll, 10), { passive: true });
  }

  // ==================== SMOOTH SCROLL ====================

  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');

        // Skip if it's just "#"
        if (href === '#') return;

        const target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });

          // Update focus for accessibility
          target.focus({ preventScroll: true });
        }
      });
    });
  }

  // ==================== ACCESSIBILITY ENHANCEMENTS ====================

  function initAccessibility() {
    // Add aria-live regions for dynamic content
    const forms = document.querySelectorAll('.form');
    forms.forEach(form => {
      const successMessage = form.querySelector('.form-success');
      if (successMessage) {
        successMessage.setAttribute('aria-live', 'polite');
        successMessage.setAttribute('aria-atomic', 'true');
      }
    });

    // Keyboard navigation for FAQ
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
      const summary = item.querySelector('.faq-question');
      if (summary) {
        summary.setAttribute('role', 'button');
        summary.setAttribute('aria-expanded', item.hasAttribute('open') ? 'true' : 'false');

        item.addEventListener('toggle', () => {
          summary.setAttribute('aria-expanded', item.hasAttribute('open') ? 'true' : 'false');
        });
      }
    });
  }

  // ==================== FORM VALIDATION ENHANCEMENTS ====================

  function initFormValidation() {
    const inputs = document.querySelectorAll('.form-input');

    inputs.forEach(input => {
      // Show validation state on blur
      input.addEventListener('blur', () => {
        if (input.validity.valid) {
          input.style.borderColor = '';
        } else if (input.value.length > 0) {
          input.style.borderColor = 'var(--color-error)';
        }
      });

      // Clear error state on input
      input.addEventListener('input', () => {
        if (input.validity.valid) {
          input.style.borderColor = '';
        }
      });
    });
  }

  // ==================== PERFORMANCE MONITORING ====================

  function logPerformanceMetrics() {
    if ('performance' in window && 'PerformanceObserver' in window) {
      // Log largest contentful paint
      try {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          console.log('LCP:', lastEntry.renderTime || lastEntry.loadTime);
        });
        observer.observe({ entryTypes: ['largest-contentful-paint'] });
      } catch (e) {
        // Silently fail if not supported
      }
    }
  }

  // ==================== INITIALIZATION ====================

  function init() {
    // Wait for DOM to be fully loaded
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
      return;
    }

    console.log('Pryntor Landing Page - Initializing...');

    // Initialize all features
    initFormModeToggle();
    initFormHandling();
    initScrollAnimations();
    initControlLineAnimation();
    initSmoothScroll();
    initAccessibility();
    initFormValidation();

    // Performance monitoring (development only)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      logPerformanceMetrics();
    }

    console.log('Pryntor Landing Page - Ready');
  }

  // ==================== ERROR HANDLING ====================

  window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
  });

  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
  });

  // ==================== START ====================

  init();

})();
