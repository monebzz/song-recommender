// Ultra-Premium JavaScript for Song Recommender
// All animations, interactions, and effects

class SongRecommenderApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupCanvas();
        this.setupEventListeners();
        this.setupScrollEffects();
        this.setupAnimations();
        this.startAnimationLoop();
    }

    setupCanvas() {
        // Skip canvas setup if canvases don't exist (removed for performance)
        this.mouseTrailCanvas = document.getElementById('mouse-trail-canvas');
        this.particleCanvas = document.getElementById('particle-canvas');

        if (!this.mouseTrailCanvas && !this.particleCanvas) {
            return; // No canvases to set up
        }

        if (this.mouseTrailCanvas) {
            this.mouseTrailCtx = this.mouseTrailCanvas.getContext('2d');
            this.resizeCanvas(this.mouseTrailCanvas);
        }

        if (this.particleCanvas) {
            this.particleCtx = this.particleCanvas.getContext('2d');
            this.resizeCanvas(this.particleCanvas);
        }

        // Mouse trail particles
        this.mouseTrail = [];
        this.maxTrailLength = 20;

        // Particle system
        this.particles = [];
        this.maxParticles = 50;
        this.mouse = { x: 0, y: 0 };

        // Connected particles
        this.connections = [];
    }

    resizeCanvas(canvas) {
        const rect = canvas.getBoundingClientRect();
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    setupEventListeners() {
        // Mouse movement
        document.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
            this.addMouseTrailParticle(e.clientX, e.clientY);
        });

        // Mouse click for particle burst
        document.addEventListener('click', (e) => {
            this.createParticleBurst(e.clientX, e.clientY);
        });

        // Window resize
        window.addEventListener('resize', () => {
            this.resizeCanvas(this.mouseTrailCanvas);
            this.resizeCanvas(this.particleCanvas);
        });

        // Button interactions
        document.querySelectorAll('.btn, .nav-link, .card').forEach(el => {
            el.addEventListener('mouseenter', this.handleHover.bind(this));
            el.addEventListener('mouseleave', this.handleHoverEnd.bind(this));
            el.addEventListener('click', this.handleClick.bind(this));
        });

        // Form interactions
        document.querySelectorAll('input, textarea').forEach(el => {
            el.addEventListener('focus', this.handleFocus.bind(this));
            el.addEventListener('blur', this.handleBlur.bind(this));
            el.addEventListener('input', this.handleInput.bind(this));
        });

        // Scroll effects
        this.setupScrollProgress();
        this.setupBackToTop();

        // Message close buttons
        document.querySelectorAll('.message-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.target.closest('.message').remove();
            });
        });

        // Navigation toggle
        const navToggle = document.querySelector('.nav-toggle');
        if (navToggle) {
            navToggle.addEventListener('click', this.toggleNavigation.bind(this));
        }

        // User dropdown menu
        const userMenuBtn = document.getElementById('userMenuBtn');
        if (userMenuBtn) {
            userMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleUserDropdown();
            });
        }

        // Prevent dropdown from closing when clicking inside the dropdown menu
        const dropdownMenu = document.getElementById('dropdownMenu');
        if (dropdownMenu) {
            dropdownMenu.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }

        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            const userDropdown = document.querySelector('.user-dropdown');
            if (userDropdown && !e.target.closest('.user-dropdown')) {
                userDropdown.classList.remove('active');
            }
        });
    }

    setupScrollEffects() {
        // Intersection Observer for fade-in animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, observerOptions);

        // Observe elements for scroll animations
        document.querySelectorAll('.scroll-fade-in, .card, .feature-card').forEach(el => {
            this.observer.observe(el);
        });

        // Counter animations
        this.setupCounters();
    }

    setupAnimations() {
        // Typing effect for hero text
        this.setupTypingEffect();

        // Floating elements
        this.setupFloatingElements();

        // Text glow effects
        this.setupTextGlow();
    }

    startAnimationLoop() {
        // Only start animation loop if canvases exist
        if (this.mouseTrailCanvas || this.particleCanvas) {
            const animate = () => {
                this.updateMouseTrail();
                this.updateParticles();
                this.updateConnections();
                this.render();

                requestAnimationFrame(animate);
            };
            animate();
        }
    }

    // Mouse Trail System
    addMouseTrailParticle(x, y) {
        this.mouseTrail.push({
            x: x,
            y: y,
            life: 1,
            size: Math.random() * 8 + 4,
            color: `hsl(${Math.random() * 60 + 340}, 100%, ${Math.random() * 30 + 50}%)`
        });

        if (this.mouseTrail.length > this.maxTrailLength) {
            this.mouseTrail.shift();
        }
    }

    updateMouseTrail() {
        this.mouseTrail.forEach((particle, index) => {
            particle.life -= 0.02;
            if (particle.life <= 0) {
                this.mouseTrail.splice(index, 1);
            }
        });
    }

    // Particle System
    createParticle() {
        return {
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
            vx: (Math.random() - 0.5) * 2,
            vy: (Math.random() - 0.5) * 2,
            size: Math.random() * 3 + 1,
            life: Math.random() * 100 + 50,
            maxLife: Math.random() * 100 + 50,
            color: Math.random() > 0.5 ? '#FF0844' : '#FFFFFF',
            alpha: Math.random() * 0.8 + 0.2
        };
    }

    createParticleBurst(x, y) {
        for (let i = 0; i < 15; i++) {
            const particle = {
                x: x,
                y: y,
                vx: (Math.random() - 0.5) * 10,
                vy: (Math.random() - 0.5) * 10,
                size: Math.random() * 6 + 2,
                life: Math.random() * 30 + 20,
                maxLife: Math.random() * 30 + 20,
                color: '#FF0844',
                alpha: 1,
                burst: true
            };
            this.particles.push(particle);
        }
    }

    updateParticles() {
        // Add new particles
        if (this.particles.length < this.maxParticles) {
            this.particles.push(this.createParticle());
        }

        // Update existing particles
        this.particles.forEach((particle, index) => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            particle.life--;

            // Bounce off edges
            if (particle.x < 0 || particle.x > window.innerWidth) particle.vx *= -1;
            if (particle.y < 0 || particle.y > window.innerHeight) particle.vy *= -1;

            // Mouse interaction
            const dx = particle.x - this.mouse.x;
            const dy = particle.y - this.mouse.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 100) {
                const force = (100 - distance) / 100;
                particle.vx += (dx / distance) * force * 0.5;
                particle.vy += (dy / distance) * force * 0.5;
            }

            // Remove dead particles
            if (particle.life <= 0) {
                this.particles.splice(index, 1);
            }
        });
    }

    updateConnections() {
        this.connections = [];

        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const p1 = this.particles[i];
                const p2 = this.particles[j];
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 120) {
                    this.connections.push({
                        p1: p1,
                        p2: p2,
                        distance: distance,
                        alpha: (120 - distance) / 120
                    });
                }
            }
        }
    }

    render() {
        // Skip rendering if canvases don't exist
        if (!this.mouseTrailCtx || !this.particleCtx) {
            return;
        }

        // Clear canvases
        this.mouseTrailCtx.clearRect(0, 0, window.innerWidth, window.innerHeight);
        this.particleCtx.clearRect(0, 0, window.innerWidth, window.innerHeight);

        // Draw mouse trail
        this.mouseTrail.forEach(particle => {
            this.mouseTrailCtx.save();
            this.mouseTrailCtx.globalAlpha = particle.life;
            this.mouseTrailCtx.fillStyle = particle.color;
            this.mouseTrailCtx.shadowColor = particle.color;
            this.mouseTrailCtx.shadowBlur = 20;
            this.mouseTrailCtx.beginPath();
            this.mouseTrailCtx.arc(particle.x, particle.y, particle.size * particle.life, 0, Math.PI * 2);
            this.mouseTrailCtx.fill();
            this.mouseTrailCtx.restore();
        });

        // Draw particle connections
        this.connections.forEach(connection => {
            this.particleCtx.save();
            this.particleCtx.globalAlpha = connection.alpha * 0.3;
            this.particleCtx.strokeStyle = '#FF0844';
            this.particleCtx.lineWidth = 1;
            this.particleCtx.beginPath();
            this.particleCtx.moveTo(connection.p1.x, connection.p1.y);
            this.particleCtx.lineTo(connection.p2.x, connection.p2.y);
            this.particleCtx.stroke();
            this.particleCtx.restore();
        });

        // Draw particles
        this.particles.forEach(particle => {
            this.particleCtx.save();
            this.particleCtx.globalAlpha = particle.alpha * (particle.life / particle.maxLife);
            this.particleCtx.fillStyle = particle.color;
            this.particleCtx.shadowColor = particle.color;
            this.particleCtx.shadowBlur = particle.burst ? 15 : 5;
            this.particleCtx.beginPath();
            this.particleCtx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.particleCtx.fill();
            this.particleCtx.restore();
        });
    }

    // Event Handlers
    handleHover(e) {
        const rect = e.target.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        // Create hover particles
        for (let i = 0; i < 5; i++) {
            const particle = {
                x: centerX + (Math.random() - 0.5) * rect.width,
                y: centerY + (Math.random() - 0.5) * rect.height,
                vx: (Math.random() - 0.5) * 4,
                vy: (Math.random() - 0.5) * 4,
                size: Math.random() * 3 + 1,
                life: Math.random() * 20 + 10,
                maxLife: Math.random() * 20 + 10,
                color: '#FF0844',
                alpha: 1,
                hover: true
            };
            this.particles.push(particle);
        }
    }

    handleHoverEnd(e) {
        // Remove hover particles
        this.particles = this.particles.filter(p => !p.hover);
    }

    handleClick(e) {
        // Ripple effect
        const ripple = document.createElement('div');
        ripple.className = 'ripple-effect';
        ripple.style.left = e.clientX - e.target.offsetLeft + 'px';
        ripple.style.top = e.clientY - e.target.offsetTop + 'px';
        e.target.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    }

    handleFocus(e) {
        e.target.parentElement.classList.add('focused');
    }

    handleBlur(e) {
        e.target.parentElement.classList.remove('focused');
    }

    handleInput(e) {
        // Character counter for textareas
        if (e.target.tagName === 'TEXTAREA') {
            const counter = e.target.parentElement.querySelector('.char-counter');
            if (counter) {
                counter.textContent = `${e.target.value.length}/500`;
            }
        }
    }

    // Navigation
    toggleNavigation() {
        document.querySelector('.nav-menu').classList.toggle('active');
        document.querySelector('.nav-toggle').classList.toggle('active');
    }

    toggleUserDropdown() {
        const dropdownMenu = document.getElementById('dropdownMenu');
        if (dropdownMenu) {
            dropdownMenu.classList.toggle('active');
        }
    }

    toggleDropdown(dropdown) {
        // Close any other open dropdowns first
        document.querySelectorAll('.nav-dropdown.active').forEach(activeDropdown => {
            if (activeDropdown !== dropdown) {
                activeDropdown.classList.remove('active');
            }
        });
        // Toggle the clicked dropdown
        dropdown.classList.toggle('active');
    }

    // Scroll Effects
    setupScrollProgress() {
        const progressBar = document.querySelector('.scroll-progress');

        window.addEventListener('scroll', () => {
            const scrollTop = window.pageYOffset;
            const docHeight = document.body.offsetHeight - window.innerHeight;
            const scrollPercent = (scrollTop / docHeight) * 100;
            progressBar.style.width = scrollPercent + '%';
        });
    }

    setupBackToTop() {
        const backToTopBtn = document.querySelector('.back-to-top');

        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
        });

        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    setupCounters() {
        const counters = document.querySelectorAll('.counter');

        counters.forEach(counter => {
            const target = parseInt(counter.dataset.target);
            const duration = 2000;
            const step = target / (duration / 16);
            let current = 0;

            const updateCounter = () => {
                current += step;
                if (current < target) {
                    counter.textContent = Math.floor(current);
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target;
                }
            };

            this.observer.observe(counter);
            counter.addEventListener('animationstart', updateCounter);
        });
    }

    // Special Effects
    setupTypingEffect() {
        const typingElements = document.querySelectorAll('.typing-effect');

        typingElements.forEach(element => {
            const text = element.textContent;
            element.textContent = '';
            element.style.borderRight = '2px solid #FF0844';

            let i = 0;
            const type = () => {
                if (i < text.length) {
                    element.textContent += text.charAt(i);
                    i++;
                    setTimeout(type, 100);
                } else {
                    element.style.borderRight = 'none';
                }
            };

            this.observer.observe(element);
            element.addEventListener('animationstart', type);
        });
    }

    setupFloatingElements() {
        const floatingElements = document.querySelectorAll('.floating');

        floatingElements.forEach((element, index) => {
            element.style.animationDelay = `${index * 0.5}s`;
        });
    }

    setupTextGlow() {
        const glowElements = document.querySelectorAll('.text-glow');

        const glow = () => {
            glowElements.forEach(element => {
                element.style.textShadow = `0 0 20px #FF0844, 0 0 40px #FF0844, 0 0 60px #FF0844`;
                setTimeout(() => {
                    element.style.textShadow = 'none';
                }, 1000);
            });
        };

        setInterval(glow, 3000);
    }
}

// Custom Audio Player Class
class AudioPlayer {
    constructor(audioElement) {
        this.audio = audioElement;
        this.container = audioElement.parentElement;
        this.isPlaying = false;
        this.isMuted = false;
        this.currentTime = 0;
        this.duration = 0;
        this.volume = 1;

        this.init();
    }

    init() {
        this.createPlayerUI();
        this.setupEventListeners();
        this.updateTimeDisplay();
    }

    createPlayerUI() {
        // Hide original audio element
        this.audio.style.display = 'none';

        // Create custom player container
        this.playerContainer = document.createElement('div');
        this.playerContainer.className = 'custom-audio-player';

        // Create player HTML structure
        this.playerContainer.innerHTML = `
            <div class="audio-player-controls">
                <button class="play-pause-btn" aria-label="Play/Pause">
                    <svg class="play-icon" viewBox="0 0 24 24" width="20" height="20">
                        <path d="M8 5v14l11-7z"/>
                    </svg>
                    <svg class="pause-icon" viewBox="0 0 24 24" width="20" height="20" style="display: none;">
                        <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                    </svg>
                </button>

                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                </div>

                <div class="time-display">
                    <span class="current-time">0:00</span>
                    <span class="time-separator">/</span>
                    <span class="total-time">0:00</span>
                </div>

                <div class="volume-container">
                    <button class="volume-btn" aria-label="Volume">
                        <svg class="volume-high-icon" viewBox="0 0 24 24" width="16" height="16">
                            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                        </svg>
                        <svg class="volume-mute-icon" viewBox="0 0 24 24" width="16" height="16" style="display: none;">
                            <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v1.79l2.48 2.25.02-.01zm-6.5 0c0 .83.26 1.65.75 2.28l-1.07 1.07c-.91-.75-1.68-1.82-1.68-3.35 0-1.77 1.02-3.29 2.5-4.03v1.79l2.48 2.25-.02-.01zM5.12 3.56L3.71 2.15 2.3 3.56l2.41 2.41c-.91.75-1.68 1.82-1.68 3.35 0 1.77 1.02 3.29 2.5 4.03v1.79c-2.89-.86-5-3.54-5-6.71s2.11-5.85 5-6.71l.01-.01 1.41 1.41zm7.38 7.38l-2.48-2.25.02.01c-.26.37-.42.81-.42 1.24 0 .43.16.87.42 1.24l.02-.01 2.48-2.25-2.48-2.25z"/>
                        </svg>
                    </button>
                    <div class="volume-slider-container">
                        <input type="range" class="volume-slider" min="0" max="1" step="0.1" value="1">
                    </div>
                </div>
            </div>
        `;

        // Insert custom player after original audio element
        this.container.insertBefore(this.playerContainer, this.audio.nextSibling);

        // Get references to UI elements
        this.playPauseBtn = this.playerContainer.querySelector('.play-pause-btn');
        this.playIcon = this.playerContainer.querySelector('.play-icon');
        this.pauseIcon = this.playerContainer.querySelector('.pause-icon');
        this.progressBar = this.playerContainer.querySelector('.progress-bar');
        this.progressFill = this.playerContainer.querySelector('.progress-fill');
        this.currentTimeDisplay = this.playerContainer.querySelector('.current-time');
        this.totalTimeDisplay = this.playerContainer.querySelector('.total-time');
        this.volumeBtn = this.playerContainer.querySelector('.volume-btn');
        this.volumeHighIcon = this.playerContainer.querySelector('.volume-high-icon');
        this.volumeMuteIcon = this.playerContainer.querySelector('.volume-mute-icon');
        this.volumeSlider = this.playerContainer.querySelector('.volume-slider');
    }

    setupEventListeners() {
        // Play/Pause button
        this.playPauseBtn.addEventListener('click', () => this.togglePlayPause());

        // Progress bar click
        this.progressBar.addEventListener('click', (e) => this.seekToPosition(e));

        // Volume controls
        this.volumeBtn.addEventListener('click', () => this.toggleMute());
        this.volumeSlider.addEventListener('input', (e) => this.setVolume(e.target.value));

        // Audio events
        this.audio.addEventListener('loadedmetadata', () => this.onLoadedMetadata());
        this.audio.addEventListener('timeupdate', () => this.onTimeUpdate());
        this.audio.addEventListener('ended', () => this.onEnded());
        this.audio.addEventListener('play', () => this.onPlay());
        this.audio.addEventListener('pause', () => this.onPause());
        this.audio.addEventListener('volumechange', () => this.onVolumeChange());
    }

    togglePlayPause() {
        if (this.isPlaying) {
            this.audio.pause();
        } else {
            this.audio.play();
        }
    }

    seekToPosition(e) {
        const rect = this.progressBar.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const percentage = clickX / rect.width;
        const newTime = percentage * this.duration;

        this.audio.currentTime = newTime;
        this.updateProgressBar();
    }

    toggleMute() {
        this.audio.muted = !this.audio.muted;
    }

    setVolume(value) {
        this.audio.volume = value;
        this.volume = value;
    }

    onLoadedMetadata() {
        this.duration = this.audio.duration;
        this.updateTimeDisplay();
    }

    onTimeUpdate() {
        this.currentTime = this.audio.currentTime;
        this.updateProgressBar();
        this.updateTimeDisplay();
    }

    onEnded() {
        this.isPlaying = false;
        this.updatePlayPauseButton();
    }

    onPlay() {
        this.isPlaying = true;
        this.updatePlayPauseButton();
    }

    onPause() {
        this.isPlaying = false;
        this.updatePlayPauseButton();
    }

    onVolumeChange() {
        this.isMuted = this.audio.muted;
        this.volume = this.audio.volume;
        this.updateVolumeDisplay();
    }

    updateProgressBar() {
        if (this.duration > 0) {
            const percentage = (this.currentTime / this.duration) * 100;
            this.progressFill.style.width = `${percentage}%`;
        }
    }

    updateTimeDisplay() {
        this.currentTimeDisplay.textContent = this.formatTime(this.currentTime);
        this.totalTimeDisplay.textContent = this.formatTime(this.duration);
    }

    updatePlayPauseButton() {
        if (this.isPlaying) {
            this.playIcon.style.display = 'none';
            this.pauseIcon.style.display = 'block';
        } else {
            this.playIcon.style.display = 'block';
            this.pauseIcon.style.display = 'none';
        }
    }

    updateVolumeDisplay() {
        if (this.isMuted || this.volume === 0) {
            this.volumeHighIcon.style.display = 'none';
            this.volumeMuteIcon.style.display = 'block';
        } else {
            this.volumeHighIcon.style.display = 'block';
            this.volumeMuteIcon.style.display = 'none';
        }
        this.volumeSlider.value = this.volume;
    }

    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';

        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SongRecommenderApp();

    // Initialize custom audio players
    document.querySelectorAll('audio').forEach(audio => {
        new AudioPlayer(audio);
    });
});

// Performance optimizations
window.addEventListener('load', () => {
    // Preload critical resources
    const images = document.querySelectorAll('img[data-src]');
    images.forEach(img => {
        img.src = img.dataset.src;
        img.classList.add('loaded');
    });

    // Reduce animations on low-performance devices
    if ('deviceMemory' in navigator && navigator.deviceMemory < 4) {
        document.body.classList.add('reduced-motion');
    }

    // Respect user's motion preferences
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.body.classList.add('reduced-motion');
    }
});
