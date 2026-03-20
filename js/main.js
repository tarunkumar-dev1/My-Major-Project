// Immediately apply the saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
if (savedTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
}

document.addEventListener('DOMContentLoaded', () => {
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
    const API_BASE = 'http://localhost:5000/api';

    // Login Form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = loginForm.querySelector('button');
            const originalText = btn.textContent;
            btn.textContent = 'Loading...';
            btn.disabled = true;

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const res = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await res.json();
                if (res.ok) {
                    localStorage.setItem('token', data.token);
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

            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const career_goal = document.getElementById('career').value;

            try {
                const res = await fetch(`${API_BASE}/auth/signup`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password, career_goal })
                });
                const data = await res.json();
                if (res.ok) {
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

                        // Populate Missing Skills & Roadmap
                        const missingContainer = document.getElementById('missingSkillsContainer');
                        const roadmapContainer = document.getElementById('roadmapTimelineContainer');

                        if (roadData && roadData.roadmap && roadData.roadmap.generated_steps) {
                            const steps = roadData.roadmap.generated_steps;

                            // Map missing skills based on roadmap targeted skills not in completed or skills
                            if (missingContainer) {
                                missingContainer.innerHTML = '';
                                const allKnown = [...(u.skills || []), ...(u.completed_skills || [])];
                                let missingFound = false;

                                steps.forEach(step => {
                                    if (!allKnown.includes(step.target_skill)) {
                                        missingContainer.innerHTML += `<span class="tag tag-warning">${step.target_skill}</span>`;
                                        missingFound = true;
                                    }
                                });

                                if (!missingFound) {
                                    missingContainer.innerHTML = '<span class="tag tag-success">All roadmap skills mastered!</span>';
                                }
                            }

                            // Render Timeline
                            if (roadmapContainer) {
                                roadmapContainer.innerHTML = '';
                                steps.forEach((step, index) => {
                                    const isCompleted = (u.completed_skills || []).includes(step.target_skill);

                                    // Determine styling
                                    const itemClass = isCompleted ? 'timeline-item completed' : 'timeline-item';
                                    const titleColor = isCompleted ? '' : 'color: var(--primary);';

                                    // Action Button
                                    let actionHtml = '';
                                    if (!isCompleted) {
                                        actionHtml = `<button class="btn btn-primary start-module-btn" data-skill="${step.target_skill}" style="padding: 0.4rem 0.8rem; font-size: 0.8rem; margin-top: 0.5rem;">Mark as Completed</button>`;
                                    }

                                    roadmapContainer.innerHTML += `
                                        <div class="${itemClass}">
                                            <div class="timeline-title" style="${titleColor}">Step ${index + 1}: ${step.module_title}</div>
                                            <div class="timeline-desc">Target Skill: <strong>${step.target_skill}</strong>. ${step.description}</div>
                                            ${actionHtml}
                                        </div>
                                    `;
                                });

                                // Attach events to completion buttons
                                document.querySelectorAll('.start-module-btn').forEach(btn => {
                                    btn.addEventListener('click', async (e) => {
                                        const skillName = e.target.getAttribute('data-skill');
                                        e.target.disabled = true;
                                        e.target.textContent = 'Saving...';

                                        try {
                                            const res = await fetch(`${API_BASE}/student/mark-completed`, {
                                                method: 'POST',
                                                headers: {
                                                    'Authorization': `Bearer ${token}`,
                                                    'Content-Type': 'application/json'
                                                },
                                                body: JSON.stringify({ skill: skillName })
                                            });
                                            if (res.ok) {
                                                window.location.reload();
                                            } else {
                                                alert("Failed to mark completed.");
                                                e.target.disabled = false;
                                                e.target.textContent = 'Mark as Completed';
                                            }
                                        } catch (err) {
                                            console.error(err);
                                        }
                                    });
                                });
                            }
                        } else {
                            if (missingContainer) missingContainer.innerHTML = '<span style="color: var(--text-muted); font-size: 0.85rem;">No analysis complete.</span>';
                            if (roadmapContainer) roadmapContainer.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 2rem;">No active roadmap. Go to Analyze Skills.</div>';
                        }

                        // Attach Logout Handler on Dashboard
                        const logoutBtn = document.querySelector('a[href="index.html"]');
                        if (logoutBtn && logoutBtn.textContent.includes('Logout')) {
                            logoutBtn.addEventListener('click', (e) => {
                                e.preventDefault();
                                localStorage.removeItem('token');
                                window.location.href = 'index.html';
                            });
                        }
                    }
                })
                .catch(console.error);
        }
    }

    // Global Logout Handler for all authenticated pages (Profile, Analyze, Progress, Admin)
    if (!isDashboard) {
        const globalLogout = document.querySelector('a[href="index.html"]');
        if (globalLogout && globalLogout.textContent.includes('Logout')) {
            globalLogout.addEventListener('click', (e) => {
                e.preventDefault();
                localStorage.removeItem('token');
                window.location.href = 'index.html';
            });
        }
    }

});
