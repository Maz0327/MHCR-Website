/**
 * Mile High Custom Remodels - Main JavaScript
 * Handles navigation, scroll effects, and interactivity
 */

(function() {
    'use strict';

    // ============================================
    // DOM Elements
    // ============================================
    const header = document.getElementById('header');
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    const navDropdowns = document.querySelectorAll('.nav-dropdown');

    // ============================================
    // Mobile Navigation Toggle
    // ============================================
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
            navToggle.setAttribute('aria-expanded', !isExpanded);
            navMenu.classList.toggle('active');

            // Prevent body scroll when menu is open
            document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navToggle.setAttribute('aria-expanded', 'false');
                navMenu.classList.remove('active');
                document.body.style.overflow = '';
            }
        });

        // Close menu when pressing Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && navMenu.classList.contains('active')) {
                navToggle.setAttribute('aria-expanded', 'false');
                navMenu.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }

    // ============================================
    // Mobile Dropdown Handling
    // ============================================
    // Always attach listener; check width inside handler so resize works correctly
    navDropdowns.forEach(function(dropdown) {
        const link = dropdown.querySelector('.nav-link');
        if (link) {
            link.addEventListener('click', function(e) {
                if (window.innerWidth < 1024) {
                    e.preventDefault();
                    dropdown.classList.toggle('open');
                }
            });
        }
    });

    // Reset dropdown states on resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (window.innerWidth >= 1024) {
                navDropdowns.forEach(function(dropdown) {
                    dropdown.classList.remove('open');
                });
                if (navMenu) navMenu.classList.remove('active');
                if (navToggle) navToggle.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
            }
        }, 250);
    });

    // ============================================
    // Sticky Header with Hide/Show on Scroll
    // ============================================
    let lastScrollY = window.scrollY;
    let ticking = false;

    function updateHeader() {
        const currentScrollY = window.scrollY;

        // Add scrolled class for shadow effect
        if (currentScrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }

        lastScrollY = currentScrollY;
        ticking = false;
    }

    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(updateHeader);
            ticking = true;
        }
    }, { passive: true });

    // ============================================
    // Smooth Scroll for Anchor Links
    // ============================================
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');

            if (targetId === '#') return;

            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                e.preventDefault();

                // Close mobile menu if open
                if (navMenu) navMenu.classList.remove('active');
                if (navToggle) navToggle.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';

                // Calculate offset for fixed header
                const headerHeight = header ? header.offsetHeight : 0;
                const topBarHeight = document.querySelector('.top-bar')?.offsetHeight || 0;
                const targetPosition = targetElement.getBoundingClientRect().top + window.scrollY - headerHeight - 20;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // ============================================
    // FAQ Accordion Enhancement
    // ============================================
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(function(item) {
        const summary = item.querySelector('summary');

        if (summary) {
            summary.addEventListener('click', function(e) {
                // Optional: Close other FAQ items when one is opened
                // Uncomment if you want accordion behavior:
                /*
                faqItems.forEach(function(otherItem) {
                    if (otherItem !== item && otherItem.hasAttribute('open')) {
                        otherItem.removeAttribute('open');
                    }
                });
                */
            });
        }
    });

    // ============================================
    // Click-to-Call Tracking (Analytics Ready)
    // ============================================
    const phoneLinks = document.querySelectorAll('a[href^="tel:"]');

    phoneLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            // Track phone click event
            if (typeof gtag !== 'undefined') {
                gtag('event', 'phone_click', {
                    'event_category': 'Contact',
                    'event_label': this.href
                });
            }
        });
    });

    // ============================================
    // Form Validation Enhancement
    // ============================================
    const forms = document.querySelectorAll('form');

    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');

                    // Add error message if not exists
                    if (!field.nextElementSibling?.classList.contains('error-message')) {
                        const errorMsg = document.createElement('span');
                        errorMsg.className = 'error-message';
                        errorMsg.textContent = 'This field is required';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                } else {
                    field.classList.remove('error');
                    const errorMsg = field.nextElementSibling;
                    if (errorMsg?.classList.contains('error-message')) {
                        errorMsg.remove();
                    }
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });

        // Remove error state on input
        form.querySelectorAll('input, textarea, select').forEach(function(field) {
            field.addEventListener('input', function() {
                this.classList.remove('error');
                const errorMsg = this.nextElementSibling;
                if (errorMsg?.classList.contains('error-message')) {
                    errorMsg.remove();
                }
            });
        });
    });

    // ============================================
    // Intersection Observer for Animations
    // ============================================
    if ('IntersectionObserver' in window) {
        const animatedElements = document.querySelectorAll('.service-card, .area-card, .testimonial-card, .process-step');

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        // Use CSS class instead of inline styles (prevents content being hidden if JS fails)
        animatedElements.forEach(function(el) {
            el.classList.add('fade-in-up');
            observer.observe(el);
        });
    }

    // ============================================
    // Lazy Loading Images (Native only — fallback not needed in modern browsers)
    // ============================================
    const images = document.querySelectorAll('img[loading="lazy"][data-src]');
    images.forEach(function(img) {
        if (img.dataset.src) {
            img.src = img.dataset.src;
        }
    });

    // ============================================
    // Gallery Filter (moved from gallery.html inline script)
    // ============================================
    const filterButtons = document.querySelectorAll('.filter-btn');
    const galleryItems = document.querySelectorAll('.gallery-item');

    if (filterButtons.length > 0) {
        filterButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                // Update active button and aria-selected
                filterButtons.forEach(function(btn) {
                    btn.classList.remove('active');
                    btn.setAttribute('aria-selected', 'false');
                });
                this.classList.add('active');
                this.setAttribute('aria-selected', 'true');

                var filter = this.getAttribute('data-filter');

                galleryItems.forEach(function(item) {
                    if (filter === 'all' || item.getAttribute('data-category') === filter) {
                        item.classList.remove('gallery-hidden');
                        item.classList.add('gallery-visible');
                    } else {
                        item.classList.remove('gallery-visible');
                        item.classList.add('gallery-hidden');
                    }
                });
            });
        });
    }

    // ============================================
    // Service Worker Registration (PWA Ready)
    // ============================================
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            // Uncomment to enable service worker:
            /*
            navigator.serviceWorker.register('/sw.js')
                .then(function(registration) {
                    console.log('ServiceWorker registration successful');
                })
                .catch(function(err) {
                    console.log('ServiceWorker registration failed:', err);
                });
            */
        });
    }

    // ============================================
    // Console Welcome Message (dev only)
    // ============================================
    if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') {
        console.log(
            '%cMile High Custom Remodels',
            'font-size: 24px; font-weight: bold; color: #E85A1B;'
        );
        console.log(
            '%cDenver\'s Trusted Home Remodeling Contractor',
            'font-size: 14px; color: #E85A1B;'
        );
    }

})();
