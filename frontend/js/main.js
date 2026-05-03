/*
 * frontend/js/main.js
 * Central client-side UI logic for SkillGap Analyzer.
 *
 * Purpose and guidance:
 *  - This file contains UI helpers, form handlers, and simple API calls
 *    used by the static frontend pages under `frontend/`.
 *  - For development the backend base URL is `http://localhost:5000/api`.
 *    Before deploying to production (Vercel), change `API_BASE` to your
 *    production API URL or configure a rewrite/proxy so that `/api` routes
 *    reach the backend.
 *  - Tokens are stored in `localStorage` for simplicity. For higher
 *    security use HTTP-only cookies in production and CSRF protections.
 *
 * Commenting policy:
 *  - Keep logic simple and avoid leaking secrets into client code.
 */

// Immediately apply the saved theme preference to reduce flash-of-unstyled-theme.
const savedTheme = localStorage.getItem('theme') || 'light';
if (savedTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
}

function isValidGmail(email) {
    // Validate that the provided email is a gmail address. This is a
    // lightweight client-side check for UX only; server-side must re-verify.
    return /^[A-Za-z0-9._%+-]+@gmail\.com$/i.test((email || '').trim());
}

function isStrongPassword(password) {
    return typeof password === 'string'
        && password.length >= 8
        && /[A-Za-z]/.test(password)
        && /\d/.test(password)
        && /[^A-Za-z0-9]/.test(password);
}

function isAdminPage() {
    return window.location.pathname.endsWith('admin.html');
}

function isAdminLoginPage() {
    return window.location.pathname.endsWith('admin-login.html');
}

document.addEventListener('DOMContentLoaded', () => {
    // Initialization entry: wire up UI elements and forms.
    console.log('SkillGap Analyzer UI initialized');

    // Theme Toggle
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (themeToggleBtn) {
        // Set initial icon and text based on saved theme
        const icon = themeToggleBtn.querySelector('i');
        const pText = themeToggleBtn.querySelector('span');
        if (savedTheme === 'dark') {
            icon.classList.remove('ph-moon');
            icon.classList.add('ph-sun');
            pText.textContent = 'Light Mode';
        } else {
            icon.classList.remove('ph-sun');
            icon.classList.add('ph-moon');
            pText.textContent = 'Dark Mode';
        }

        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);

            // Icon handling
            if (newTheme === 'dark') {
                icon.classList.remove('ph-moon');
                icon.classList.add('ph-sun');
                pText.textContent = 'Light Mode';
            } else {
                icon.classList.remove('ph-sun');
                icon.classList.add('ph-moon');
                pText.textContent = 'Dark Mode';
            }
        });
    }

    // --- API Integration Section ---
    // Use a relative `/api` path in production (works when frontend is
    // served from Vercel and the backend is proxied). For local development
    // detect localhost and forward to local backend on port 5000.
    const API_BASE = (location.hostname === 'localhost' || location.hostname === '127.0.0.1')
        ? 'http://localhost:5000/api'
        : '/api';

    // Login Form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = loginForm.querySelector('button');
            const originalText = btn.textContent;
            btn.textContent = 'Loading...';
            btn.disabled = true;

            const emailField = loginForm.querySelector('#loginEmail') || loginForm.querySelector('#email');
            const passwordField = loginForm.querySelector('#loginPassword') || loginForm.querySelector('#password');
            // Collect values from the form fields. We trim/validate on the
            // client side for better UX but always validate on the server.
            const email = emailField ? emailField.value : '';
            const password = passwordField ? passwordField.value : '';

            if (!isValidGmail(email)) {
                alert('Please enter a valid Gmail address.');
                btn.textContent = originalText;
                btn.disabled = false;
                return;
            }

            try {
                const res = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await res.json();
                if (res.ok) {
                    // Persist the token in localStorage to keep the example simple.
                    // NOTE: Storing JWTs in localStorage exposes them to XSS; for
                    // production prefer secure, HTTP-only cookies.
                    localStorage.setItem('token', data.token);
                    localStorage.setItem('last_user_token', data.token);
                    if (email) {
                        localStorage.setItem('last_user_email', email);
                    }
                    window.location.href = 'dashboard.html';
                } else {
                    alert('Login failed: ' + (data.error || 'Invalid credentials'));
                }
            } catch (err) {
                alert('Network error. Is the backend running?');
            } finally {
                btn.textContent = originalText;
                btn.disabled = false;
            }
        });
    }

    // Signup Form
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = signupForm.querySelector('button');
            const originalText = btn.textContent;
            btn.textContent = 'Loading...';
            btn.disabled = true;

            const nameField = signupForm.querySelector('#signupName') || signupForm.querySelector('#name');
            const emailField = signupForm.querySelector('#signupEmail') || signupForm.querySelector('#email');
            const passwordField = signupForm.querySelector('#signupPassword') || signupForm.querySelector('#password');
            const careerField = signupForm.querySelector('#signupCareer') || signupForm.querySelector('#career');
            const photoField = signupForm.querySelector('#profilePhoto');

            // Gather form inputs
            const name = nameField ? nameField.value : '';
            const email = emailField ? emailField.value : '';
            const password = passwordField ? passwordField.value : '';
            const career_goal = careerField ? careerField.value : '';
            let profile_photo = null;

            if (!isValidGmail(email)) {
                alert('Only valid Gmail addresses are allowed.');
                btn.textContent = originalText;
                btn.disabled = false;
                return;
            }

            if (!isStrongPassword(password)) {
                alert('Password must be at least 8 characters long and include letters, numbers, and symbols.');
                btn.textContent = originalText;
                btn.disabled = false;
                return;
            }

            if (photoField && photoField.files && photoField.files[0]) {
                const file = photoField.files[0];
                if (!file.type.startsWith('image/')) {
                    alert('Please choose an image file for your profile photo.');
                    btn.textContent = originalText;
                    btn.disabled = false;
                    return;
                }

                profile_photo = await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(reader.result);
                    reader.onerror = () => reject(new Error('Failed to read profile photo.'));
                    reader.readAsDataURL(file);
                });
            }

            try {
                const res = await fetch(`${API_BASE}/auth/signup`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password, career_goal, profile_photo })
                });
                const data = await res.json();
                if (res.ok) {
                    // On success, suggest the user log in. Consider auto-login
                    // flows in the future but avoid exposing credentials.
                    alert('Account successfully created! Please log in to continue.');
                    window.location.href = 'index.html';
                } else {
                    alert('Signup failed: ' + (data.error || 'Unknown error'));
                }
            } catch (err) {
                alert('Network error. Is the backend running?');
            } finally {
                btn.textContent = originalText;
                btn.disabled = false;
            }
        });
    }

    // Admin Login Form
    const adminLoginForm = document.getElementById('adminLoginForm');
    const userProfileBtn = document.getElementById('userProfileBtn');
    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = adminLoginForm.querySelector('button');
            const originalText = btn.textContent;
            btn.textContent = 'Verifying...';
            btn.disabled = true;

            const usernameField = adminLoginForm.querySelector('#adminUsername');
            const passwordField = adminLoginForm.querySelector('#adminPassword');
            const username = usernameField ? usernameField.value.trim() : '';
            const password = passwordField ? passwordField.value : '';

            try {
                const res = await fetch(`${API_BASE}/admin/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await res.json();

                if (res.ok) {
                    localStorage.setItem('admin_token', data.token);
                    if (data.admin && data.admin.username) {
                        localStorage.setItem('admin_username', data.admin.username);
                    }
                    window.location.href = 'admin.html';
                } else {
                    alert('Admin login failed: ' + (data.error || 'Invalid credentials'));
                }
            } catch (err) {
                alert('Network error. Is the backend running?');
            } finally {
                btn.textContent = originalText;
                btn.disabled = false;
            }
        });
    }

    if (userProfileBtn) {
        userProfileBtn.addEventListener('click', () => {
            const lastUserToken = localStorage.getItem('last_user_token') || localStorage.getItem('token');
            if (!lastUserToken) {
                alert('No previous user profile found. Please log in as a user first.');
                window.location.href = 'index.html';
                return;
            }

            localStorage.setItem('token', lastUserToken);
            window.location.href = 'profile.html';
        });
    }

    // --- Dashboard Protection & Data Load ---
    const isDashboard = window.location.pathname.endsWith('dashboard.html');
    if (isDashboard) {
        const token = localStorage.getItem('token');
        if (!token) {
            // Not logged in, kick out to login page
            window.location.href = 'index.html';
        } else {
            // Fetch Dashboard Data and Roadmap
            Promise.all([
                fetch(`${API_BASE}/student/dashboard`, { headers: { 'Authorization': `Bearer ${token}` } }),
                fetch(`${API_BASE}/student/roadmap`, { headers: { 'Authorization': `Bearer ${token}` } })
            ])
                .then(async ([dashRes, roadRes]) => {
                    if (!dashRes.ok) {
                        localStorage.removeItem('token');
                        window.location.href = 'index.html';
                        throw new Error('Unauthorized');
                    }
                    const data = await dashRes.json();
                    const roadData = roadRes.ok ? await roadRes.json() : null;

                    if (data.user) {
                        const u = data.user;
                        // Update Welcome Message
                        const fname = u.name.split(' ')[0];
                        const welcomeMsg = document.querySelector('.welcome-msg h1');
                        if (welcomeMsg) welcomeMsg.innerHTML = `Welcome back, ${fname}! 👋`;

                        // Update Top Right Avatar
                        const avatar = document.querySelector('.avatar');
                        if (avatar) avatar.textContent = u.name.substring(0, 2).toUpperCase();
                        const userInfoName = document.querySelector('.user-info span:first-child');
                        if (userInfoName) userInfoName.textContent = u.name;

                        // Update Target Career
                        const careerBadge = document.querySelector('.career-badge');
                        if (careerBadge) careerBadge.innerHTML = `<i class="ph-fill ph-code"></i> Target: ${u.career_goal || 'Not set'}`;

                        // Update Readiness Score
                        const rs = u.readiness_score || 0;
                        const readinessSpan = document.querySelector('.progress-value');
                        if (readinessSpan) readinessSpan.textContent = `${rs}%`;
                        const progressCircle = document.querySelector('.circular-progress');
                        if (progressCircle) {
                            progressCircle.style.background = `conic-gradient(var(--primary) ${rs * 3.6}deg, var(--bg-card) 0deg)`;
                        }

                        // Populate Current Skills
                        const currentContainer = document.getElementById('currentSkillsContainer');
                        if (currentContainer) {
                            currentContainer.innerHTML = '';
                            if (u.skills && u.skills.length > 0) {
                                u.skills.forEach(skill => {
                                    currentContainer.innerHTML += `<span class="tag tag-success">${skill}</span>`;
                                });
                            } else {
                                currentContainer.innerHTML = '<span style="color: var(--text-muted); font-size: 0.85rem;">No skills logged yet.</span>';
                            }
                        }

                        // Populate Completed Skills
                        const completedContainer = document.getElementById('completedSkillsContainer');
                        if (completedContainer) {
                            completedContainer.innerHTML = '';
                            if (u.completed_skills && u.completed_skills.length > 0) {
                                u.completed_skills.forEach(skill => {
                                    completedContainer.innerHTML += `<span class="tag tag-success">${skill}</span>`;
                                });
                            } else {
                                completedContainer.innerHTML = '<span style="font-size: 0.85rem; color: var(--text-muted);">No completed modules yet.</span>';
                            }
                        }
