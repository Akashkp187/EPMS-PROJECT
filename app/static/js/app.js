/* MetricForge - App JS with GSAP animations and interactivity */
document.addEventListener('DOMContentLoaded', function () {
    if (typeof gsap !== 'undefined') gsap.registerPlugin(ScrollTrigger);

    // Relative time for elements with data-time (ISO string or timestamp)
    function formatRelativeTime(date) {
        var now = new Date();
        var d = date instanceof Date ? date : new Date(date);
        var s = Math.round((now - d) / 1000);
        if (s < 60) return 'Just now';
        if (s < 3600) return Math.floor(s / 60) + 'm ago';
        if (s < 86400) return Math.floor(s / 3600) + 'h ago';
        if (s < 604800) return Math.floor(s / 86400) + 'd ago';
        if (s < 2592000) return Math.floor(s / 604800) + 'w ago';
        return d.toLocaleDateString();
    }
    document.querySelectorAll('[data-time]').forEach(function (el) {
        var t = el.getAttribute('data-time');
        if (t) {
            var friendly = formatRelativeTime(t);
            if (el.querySelector('.time-relative')) {
                el.querySelector('.time-relative').textContent = friendly;
            } else {
                el.textContent = friendly;
            }
        }
    });

    // Count-up animation for stat numbers (elements with data-count)
    document.querySelectorAll('[data-count]').forEach(function (el) {
        var target = parseInt(el.getAttribute('data-count'), 10);
        if (isNaN(target)) return;
        var duration = 0.8;
        var start = 0;
        if (typeof gsap !== 'undefined') {
            gsap.to({ v: start }, { v: target, duration: duration, ease: 'power2.out', onUpdate: function () {
                el.textContent = Math.round(this.targets()[0].v);
            } });
        } else {
            el.textContent = target;
        }
    });

    // Confirm modal for delete forms: form with data-confirm="Message"
    document.querySelectorAll('form[data-confirm]').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!window.confirm(form.getAttribute('data-confirm') || 'Are you sure?')) {
                e.preventDefault();
            }
        });
    });

    // Flash auto-dismiss (optional: add data-auto-dismiss="5" to flash-wrap for 5s)
    document.querySelectorAll('.flash-wrap[data-auto-dismiss]').forEach(function (wrap) {
        var sec = parseInt(wrap.getAttribute('data-auto-dismiss'), 10) || 5;
        wrap.querySelectorAll('.flash').forEach(function (flash) {
            setTimeout(function () {
                if (flash.parentNode) {
                    flash.style.opacity = '0';
                    if (typeof gsap !== 'undefined') {
                        gsap.to(flash, { height: 0, margin: 0, padding: 0, overflow: 'hidden', duration: 0.3, onComplete: function () { flash.remove(); } });
                    } else {
                        flash.remove();
                    }
                }
            }, sec * 1000);
        });
    });

    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    const saved = localStorage.getItem('metricforge-theme');
    
    // Apply initial theme with no transition to avoid flash
    if (saved) {
        html.classList.add('no-transition');
        html.setAttribute('data-theme', saved);
        setTimeout(() => html.classList.remove('no-transition'), 100);
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', function (e) {
            // Create transition overlay
            const overlay = document.createElement('div');
            overlay.classList.add('theme-transition-overlay');
            document.body.appendChild(overlay);

            // Get click coordinates for ripple origin
            const x = e.clientX;
            const y = e.clientY;
            
            // Start transition
            if (typeof gsap !== 'undefined') {
                // Circle clip-path transition
                gsap.set(overlay, { 
                    clipPath: `circle(0px at ${x}px ${y}px)`,
                    opacity: 1
                });

                const current = html.getAttribute('data-theme') || 'light';
                const next = current === 'light' ? 'dark' : 'light';
                
                // Animate overlay to cover screen
                gsap.to(overlay, {
                    clipPath: `circle(${Math.max(window.innerWidth, window.innerHeight) * 1.5}px at ${x}px ${y}px)`,
                    duration: 0.6,
                    ease: 'power2.inOut',
                    onComplete: () => {
                        // Switch theme
                        html.setAttribute('data-theme', next);
                        localStorage.setItem('metricforge-theme', next);
                        
                        // Fade out overlay
                        gsap.to(overlay, {
                            opacity: 0,
                            duration: 0.4,
                            onComplete: () => overlay.remove()
                        });
                        
                        // Animate elements that need to update
                        gsap.fromTo('.logo-img, .nav-link, .card, .input-float', 
                            { y: 5, opacity: 0.9 },
                            { y: 0, opacity: 1, duration: 0.3, stagger: 0.02, ease: 'power2.out' }
                        );
                    }
                });

                // Icon animation
                gsap.to(themeToggle, { 
                    rotation: next === 'dark' ? 180 : 0, 
                    scale: 0.8, 
                    duration: 0.2, 
                    yoyo: true, 
                    repeat: 1 
                });
            } else {
                // Fallback for no GSAP
                const current = html.getAttribute('data-theme') || 'light';
                const next = current === 'light' ? 'dark' : 'light';
                html.setAttribute('data-theme', next);
                localStorage.setItem('metricforge-theme', next);
                overlay.remove();
            }
        });
    }

    // Logo bar graph: click to animate bars (same as hover)
    const mainLogo = document.getElementById('main-logo');
    if (mainLogo) {
        mainLogo.addEventListener('click', function (e) {
            if (e.target.closest('a') && e.currentTarget.href) return;
            this.classList.add('is-active');
            var self = this;
            setTimeout(function () { self.classList.remove('is-active'); }, 600);
        });
    }

    // User dropdown
    const userBtn = document.getElementById('user-menu-btn');
    const userDrop = document.getElementById('user-dropdown');
    if (userBtn && userDrop) {
        userBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            const isActive = userDrop.classList.toggle('active');
            userBtn.setAttribute('aria-expanded', isActive ? 'true' : 'false');
        });
        document.addEventListener('click', function (e) {
            if (!userDrop.classList.contains('active')) return;
            if (e.target === userBtn || userBtn.contains(e.target) || userDrop.contains(e.target)) return;
            userDrop.classList.remove('active');
            userBtn.setAttribute('aria-expanded', 'false');
        });
    }

    // Main nav dropdowns (Performance / Manage) – close when mouse leaves or click outside
    document.querySelectorAll('.nav-item-dropdown').forEach(function (wrap) {
        const trigger = wrap.querySelector('.nav-dropdown-trigger');
        const menu = wrap.querySelector('.nav-dropdown-menu');
        if (!trigger || !menu) return;

        let hoverTimeout;

        // Hover open/close with small delay to feel smooth
        wrap.addEventListener('mouseenter', function () {
            clearTimeout(hoverTimeout);
            wrap.classList.add('is-open');
            if (trigger.querySelector('.chevron-icon')) {
                trigger.querySelector('.chevron-icon').classList.add('is-open');
            }
        });

        wrap.addEventListener('mouseleave', function () {
            hoverTimeout = setTimeout(function () {
                wrap.classList.remove('is-open');
                if (trigger.querySelector('.chevron-icon')) {
                    trigger.querySelector('.chevron-icon').classList.remove('is-open');
                }
            }, 120);
        });

        // Keyboard accessibility
        trigger.addEventListener('focus', function () {
            wrap.classList.add('is-open');
        });
        trigger.addEventListener('blur', function () {
            hoverTimeout = setTimeout(function () {
                wrap.classList.remove('is-open');
            }, 120);
        });

        // Click outside closes all dropdowns
        document.addEventListener('click', function (e) {
            if (!wrap.classList.contains('is-open')) return;
            if (wrap.contains(e.target)) return;
            wrap.classList.remove('is-open');
            if (trigger.querySelector('.chevron-icon')) {
                trigger.querySelector('.chevron-icon').classList.remove('is-open');
            }
        });
    });

    // Global search
    const searchInput = document.getElementById('global-search');
    const searchResults = document.getElementById('search-results');
    if (searchInput && searchResults) {
        let debounce;
        searchInput.addEventListener('input', function () {
            clearTimeout(debounce);
            const q = this.value.trim();
            if (q.length < 2) {
                searchResults.classList.remove('active');
                searchResults.innerHTML = '';
                return;
            }
            debounce = setTimeout(function () {
                fetch('/api/search?q=' + encodeURIComponent(q))
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        if (!data.results || data.results.length === 0) {
                            searchResults.innerHTML = '<div class="p-3 text-muted">No results</div>';
                        } else {
                            searchResults.innerHTML = data.results.map(function (u) {
                                return '<a href="' + u.url + '">' + u.name + ' <span class="text-muted">' + u.email + '</span></a>';
                            }).join('');
                        }
                        searchResults.classList.add('active');
                    })
                    .catch(function () {
                        searchResults.innerHTML = '<div class="p-3 text-muted">Search unavailable</div>';
                        searchResults.classList.add('active');
                    });
            }, 250);
        });
        searchInput.addEventListener('blur', function () {
            setTimeout(function () { searchResults.classList.remove('active'); }, 150);
        });
    }

    // Notifications badge
    const notifBadge = document.getElementById('notif-badge');
    if (notifBadge) {
        fetch('/api/dashboard/stats')
            .then(function (r) { return r.json(); })
            .then(function (d) {
                if (d.notifications_unread > 0) {
                    notifBadge.textContent = d.notifications_unread > 99 ? '99+' : d.notifications_unread;
                }
            })
            .catch(function () {});
    }

    // Page reveal animations
    var reveals = document.querySelectorAll('.reveal');
    if (reveals.length && typeof gsap !== 'undefined') {
        gsap.fromTo(reveals, { opacity: 0, y: 24 }, {
            opacity: 1,
            y: 0,
            duration: 0.5,
            stagger: 0.08,
            ease: 'power2.out'
        });
    }

    // Flash close
    document.querySelectorAll('.flash-close').forEach(function (btn) {
        btn.addEventListener('click', function () {
            this.closest('.flash').style.opacity = '0';
            gsap.to(this.closest('.flash'), { height: 0, margin: 0, padding: 0, overflow: 'hidden', duration: 0.3, onComplete: function () {
                this.target.remove();
            } });
        });
    });
});
