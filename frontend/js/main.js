/*
 * main.js
 * Frontend UI behavior and API integration helpers used across pages.
 */

// Immediately apply the saved theme.
const savedTheme = localStorage.getItem("theme") || "light";
if (savedTheme === "dark") {
    document.documentElement.setAttribute("data-theme", "dark");
}

function isValidEmail(email) {
    // Lightweight client-side email validation (RFC-lite).
    return /^[^@\s]+@[^@\s]+\.[^@\s]+$/i.test((email || "").trim());
}

function isStrongPassword(password) {
    return (
        typeof password === "string" &&
        password.length >= 8 &&
        /[A-Za-z]/.test(password) &&
        /\d/.test(password) &&
        /[^A-Za-z0-9]/.test(password)
    );
}

function isAdminPage() {
    const pathname = window.location.pathname;
    return (
        pathname.includes("admin.html") ||
        (typeof window !== "undefined" &&
            window.location.href.includes("admin.html"))
    );
}

function isAdminLoginPage() {
    return window.location.pathname.endsWith("admin-login.html");
}

function isProfilePage() {
    return window.location.pathname.endsWith("profile.html");
}

function bindPasswordVisibilityToggles() {
    document.querySelectorAll(".password-toggle-btn").forEach((button) => {
        const icon = button.querySelector("i");
        button.addEventListener("click", () => {
            const wrapper = button.closest(".password-input-wrapper");
            if (!wrapper) return;
            const passwordInput = wrapper.querySelector(
                "input[type='password'], input[type='text']",
            );
            if (!passwordInput) return;

            const isPassword = passwordInput.type === "password";
            passwordInput.type = isPassword ? "text" : "password";

            if (icon) {
                icon.classList.toggle("ph-eye", !isPassword);
                icon.classList.toggle("ph-eye-slash", isPassword);
            }
            button.setAttribute(
                "aria-label",
                isPassword ? "Hide password" : "Show password",
            );
        });
    });
}

function isDashboardPage() {
    return window.location.pathname.endsWith("dashboard.html");
}

function showCourseInsight(courseTitle, courseNote) {
    const insightBanner = document.getElementById("courseInsightBanner");
    const insightTitle = document.getElementById("courseInsightTitle");
    const insightText = document.getElementById("courseInsightText");

    if (!insightBanner || !insightTitle || !insightText) {
        return;
    }

    insightTitle.textContent = `Smart pick: ${courseTitle}`;
    insightText.textContent = courseNote;
    insightBanner.style.display = "block";
}

function openRecommendedCourse(courseCard, apiBase) {
    const title =
        courseCard.getAttribute("data-course-title") || "Recommended Course";
    const courseUrl = courseCard.getAttribute("data-course-url") || "#";
    const courseNote =
        courseCard.getAttribute("data-course-note") ||
        "This course matches your current roadmap.";

    // Remember the user's choice so the dashboard can surface it later.
    localStorage.setItem(
        "last_recommended_course",
        JSON.stringify({
            title,
            url: courseUrl,
            note: courseNote,
            clickedAt: new Date().toISOString(),
        }),
    );

    showCourseInsight(title, courseNote);

    // Give the user immediate feedback and a clear path forward.
    if (courseUrl && courseUrl !== "#") {
        window.open(courseUrl, "_blank", "noopener,noreferrer");
    }

    // Add a small intelligent nudge based on the current page state.
    if (apiBase) {
        setTimeout(() => {
            console.info(`Smart recommendation opened: ${title}`);
        }, 0);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    // Initialization entry: wire up UI elements and forms.
    console.log("SkillGap Analyzer UI initialized");

    // === ADMIN PAGE CHECK - RUN FIRST ===
    if (window.location.href.includes("admin.html")) {
        const adminToken = localStorage.getItem("admin_token");
        const adminLoginSection = document.getElementById("adminLoginSection");
        const adminDashboardShell = document.getElementById(
            "adminDashboardShell",
        );

        console.log("Admin page detected", { hasToken: !!adminToken });

        if (!adminToken) {
            // No token - show login form
            if (adminLoginSection) adminLoginSection.style.display = "block";
            if (adminDashboardShell) {
                adminDashboardShell.style.display = "none";
                adminDashboardShell.style.visibility = "hidden";
            }
        } else {
            // Has token - show dashboard
            if (adminLoginSection) adminLoginSection.style.display = "none";
            if (adminDashboardShell) {
                adminDashboardShell.style.display = "flex";
                adminDashboardShell.style.visibility = "visible";
            }
        }
    }

    const sidebar = document.querySelector(".sidebar");
    const sidebarLogo = document.querySelector(".sidebar-logo");
    const savedSidebarState =
        localStorage.getItem("sidebar_collapsed") === "true";

    if (
        sidebar &&
        sidebarLogo &&
        !document.getElementById("sidebarCollapseToggle")
    ) {
        const toggleButton = document.createElement("button");
        toggleButton.type = "button";
        toggleButton.id = "sidebarCollapseToggle";
        toggleButton.className = "sidebar-collapse-toggle";
        toggleButton.setAttribute("aria-label", "Toggle sidebar");
        toggleButton.innerHTML = '<i class="ph ph-list"></i>';
        sidebarLogo.appendChild(toggleButton);

        const applySidebarState = (collapsed) => {
            document.body.classList.toggle("sidebar-collapsed", collapsed);
            localStorage.setItem("sidebar_collapsed", String(collapsed));
            toggleButton.setAttribute(
                "aria-label",
                collapsed ? "Expand sidebar" : "Collapse sidebar",
            );
        };

        applySidebarState(savedSidebarState);
        toggleButton.addEventListener("click", () => {
            applySidebarState(
                !document.body.classList.contains("sidebar-collapsed"),
            );
        });

        // Preserve readable labels for the expanded state and native hints for the collapsed state.
        document
            .querySelectorAll(
                ".sidebar .nav-link, .sidebar .sidebar-logo, .sidebar .nav-link button",
            )
            .forEach((el) => {
                const text = el.querySelector("span")?.textContent?.trim();
                if (text) el.setAttribute("title", text);
            });
    }

    // Theme Toggle
    const themeToggleBtn = document.getElementById("theme-toggle");
    bindPasswordVisibilityToggles();
    if (themeToggleBtn) {
        // Set initial icon and text based on saved theme
        const icon = themeToggleBtn.querySelector("i");
        const pText = themeToggleBtn.querySelector("span");
        if (savedTheme === "dark") {
            icon.classList.remove("ph-moon");
            icon.classList.add("ph-sun");
            pText.textContent = "Light Mode";
        } else {
            icon.classList.remove("ph-sun");
            icon.classList.add("ph-moon");
            pText.textContent = "Dark Mode";
        }

        themeToggleBtn.addEventListener("click", () => {
            const currentTheme =
                document.documentElement.getAttribute("data-theme") || "light";
            const newTheme = currentTheme === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", newTheme);
            localStorage.setItem("theme", newTheme);

            // Icon handling
            if (newTheme === "dark") {
                icon.classList.remove("ph-moon");
                icon.classList.add("ph-sun");
                pText.textContent = "Light Mode";
            } else {
                icon.classList.remove("ph-sun");
                icon.classList.add("ph-moon");
                pText.textContent = "Dark Mode";
            }
        });
    }

    // --- API Integration Section ---
    const API_BASE =
        window.SKILLGAP_CONFIG?.API_BASE_URL ||
        "https://backendaiskillgap.tarunkumar17.me/api";

    // Sidebar visibility rules:
    // - On regular user pages, hide only the Admin tab.
    // - On the admin dashboard page, show only the Admin dashboard entry.
    (function enforceSidebarVisibility() {
        const userToken = localStorage.getItem("token");
        const adminToken = localStorage.getItem("admin_token");
        const adminPage = isAdminPage();

        // Hide admin links for regular users on user-facing pages.
        if (userToken && !adminPage) {
            document
                .querySelectorAll(
                    'a[href="admin-login.html"], a[href="admin.html"]',
                )
                .forEach((el) => {
                    el.style.display = "none";
                });
        }

        // On the admin dashboard, restrict the visible navigation to the
        // admin dashboard entry only (but keep logout and theme buttons)
        if (adminToken && adminPage) {
            document.querySelectorAll(".sidebar .nav-link").forEach((el) => {
                const href = el.getAttribute("href") || "";
                const isLogout =
                    el.getAttribute("data-admin-logout") === "true";
                const isTheme = el.id === "theme-toggle";

                // Keep logout and theme buttons visible
                if (isLogout || isTheme) {
                    el.style.display = "";
                } else if (href !== "admin.html" && href !== "#") {
                    el.style.display = "none";
                } else if (href === "admin.html") {
                    el.classList.add("active");
                    el.style.display = "";
                }
            });
        }
    })();

    const isProfile = isProfilePage();
    if (isProfile) {
        const token = localStorage.getItem("token");
        if (!token) {
            window.location.href = "index.html";
            return;
        }

        const headerAvatar = document.getElementById("headerAvatar");
        const headerName = document.getElementById("headerName");
        const profileName = document.getElementById("profileName");
        const profileEmail = document.getElementById("profileEmail");
        const profileCareer = document.getElementById("profileCareer");
        const mainAvatar = document.getElementById("mainAvatar");
        const editName = document.getElementById("editName");
        const editEmail = document.getElementById("editEmail");
        const editCareer = document.getElementById("editCareer");
        const editProfileBtn = document.getElementById("editProfileBtn");
        const saveProfileBtn = document.getElementById("saveProfileBtn");
        const profilePhotoInput = document.getElementById("profilePhotoInput");
        const changePasswordBtn = document.getElementById("changePasswordBtn");
        const passwordPanel = document.getElementById("passwordPanel");
        const passwordChevron = document.getElementById("passwordChevron");
        const savePasswordBtn = document.getElementById("savePasswordBtn");
        const currentPassword = document.getElementById("currentPassword");
        const newPassword = document.getElementById("newPassword");
        const prefEmailNotifications = document.getElementById(
            "prefEmailNotifications",
        );
        const prefPublicProfile = document.getElementById("prefPublicProfile");

        let selectedPhotoData = null;

        const setAvatarText = (name) => {
            const initials = name
                ? name
                      .split(" ")
                      .map((word) => word[0])
                      .slice(0, 2)
                      .join("")
                      .toUpperCase()
                : "--";

            if (headerAvatar) headerAvatar.textContent = initials;
            if (mainAvatar) {
                if (selectedPhotoData) {
                    mainAvatar.style.backgroundImage = `url(${selectedPhotoData})`;
                    mainAvatar.style.backgroundSize = "cover";
                    mainAvatar.style.backgroundPosition = "center";
                    mainAvatar.textContent = "";
                } else {
                    mainAvatar.style.backgroundImage = "";
                    mainAvatar.textContent = initials;
                }
            }
        };

        const setEditMode = (enabled) => {
            if (editName) editName.disabled = !enabled;
            if (editCareer) editCareer.disabled = !enabled;
            if (saveProfileBtn)
                saveProfileBtn.style.display = enabled ? "inline-flex" : "none";
            if (editProfileBtn)
                editProfileBtn.textContent = enabled
                    ? "Cancel"
                    : "Edit Profile";
        };

        const loadProfile = async () => {
            try {
                const res = await fetch(`${API_BASE}/student/dashboard`, {
                    headers: { Authorization: `Bearer ${token}` },
                });
                if (!res.ok) {
                    localStorage.removeItem("token");
                    window.location.href = "index.html";
                    return;
                }
                const data = await res.json();
                const user = data.user || {};
                const name = user.name || "User";
                const email = user.email || "";
                const career_goal = user.career_goal || "";
                const readiness = user.readiness_score || 0;
                const skillsCount = (user.skills || []).length;
                const completedCount = (user.completed_skills || []).length;
                const preferences = user.preferences || {};

                if (headerName) headerName.textContent = name;
                if (profileName) profileName.textContent = name;
                if (profileEmail) profileEmail.textContent = email;
                if (profileCareer)
                    profileCareer.textContent = career_goal || "Not Set";
                if (editName) editName.value = name;
                if (editEmail) editEmail.value = email;
                if (editCareer)
                    editCareer.value =
                        career_goal || editCareer.options[0]?.value || "";
                if (prefEmailNotifications)
                    prefEmailNotifications.checked = Boolean(
                        preferences.email_notifications,
                    );
                if (prefPublicProfile)
                    prefPublicProfile.checked = Boolean(
                        preferences.public_profile,
                    );
                if (document.getElementById("statReadiness"))
                    document.getElementById("statReadiness").textContent =
                        `${readiness}%`;
                if (document.getElementById("statSkills"))
                    document.getElementById("statSkills").textContent =
                        `${skillsCount}`;
                if (document.getElementById("statCompleted"))
                    document.getElementById("statCompleted").textContent =
                        `${completedCount}`;
                setAvatarText(name);
                setEditMode(false);
            } catch (err) {
                console.error("Profile load failed", err);
            }
        };

        if (profilePhotoInput) {
            profilePhotoInput.addEventListener("change", async (event) => {
                const file = event.target.files?.[0];
                if (!file) return;
                if (!file.type.startsWith("image/")) {
                    alert("Please select a valid image file.");
                    return;
                }
                selectedPhotoData = await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(reader.result);
                    reader.onerror = () =>
                        reject(new Error("Failed to read profile image."));
                    reader.readAsDataURL(file);
                });
                setAvatarText(editName?.value || "");
            });
        }

        if (editProfileBtn) {
            editProfileBtn.addEventListener("click", () => {
                const currentlyEditing = editName && !editName.disabled;
                setEditMode(!currentlyEditing);
            });
        }

        if (saveProfileBtn) {
            saveProfileBtn.addEventListener("click", async () => {
                const updates = {};
                const nameValue = editName?.value.trim();
                const careerValue = editCareer?.value || "";
                if (nameValue) updates.name = nameValue;
                if (careerValue) updates.career_goal = careerValue;
                if (selectedPhotoData)
                    updates.profile_photo = selectedPhotoData;
                updates.preferences = {
                    email_notifications: Boolean(
                        prefEmailNotifications?.checked,
                    ),
                    public_profile: Boolean(prefPublicProfile?.checked),
                };

                try {
                    const res = await fetch(`${API_BASE}/student/profile`, {
                        method: "PUT",
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: `Bearer ${token}`,
                        },
                        body: JSON.stringify(updates),
                    });
                    const result = await res.json();
                    if (!res.ok)
                        throw new Error(
                            result.error || "Unable to save profile.",
                        );
                    alert(result.message || "Profile updated.");
                    await loadProfile();
                } catch (err) {
                    console.error(err);
                    alert(err.message || "Profile update failed.");
                }
            });
        }

        if (changePasswordBtn && passwordPanel && passwordChevron) {
            changePasswordBtn.addEventListener("click", () => {
                const isOpen = passwordPanel.style.display === "block";
                passwordPanel.style.display = isOpen ? "none" : "block";
                passwordChevron.classList.toggle("ph-caret-down", isOpen);
                passwordChevron.classList.toggle("ph-caret-up", !isOpen);
            });
        }

        if (savePasswordBtn) {
            savePasswordBtn.addEventListener("click", async () => {
                const currentValue = currentPassword?.value || "";
                const newValue = newPassword?.value || "";
                if (!currentValue || !newValue) {
                    alert("Please fill both current and new passwords.");
                    return;
                }
                if (!isStrongPassword(newValue)) {
                    alert(
                        "New password must be at least 8 characters long and include letters, numbers, and symbols.",
                    );
                    return;
                }
                try {
                    const res = await fetch(
                        `${API_BASE}/student/profile/password`,
                        {
                            method: "PUT",
                            headers: {
                                "Content-Type": "application/json",
                                Authorization: `Bearer ${token}`,
                            },
                            body: JSON.stringify({
                                current_password: currentValue,
                                new_password: newValue,
                            }),
                        },
                    );
                    const result = await res.json();
                    if (!res.ok)
                        throw new Error(
                            result.error || "Password change failed.",
                        );
                    alert(result.message || "Password updated successfully.");
                    if (currentPassword) currentPassword.value = "";
                    if (newPassword) newPassword.value = "";
                } catch (err) {
                    console.error(err);
                    alert(err.message || "Password update failed.");
                }
            });
        }

        loadProfile();
    }

    // Login Form
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const btn = loginForm.querySelector("button");
            const originalText = btn.textContent;
            btn.textContent = "Loading...";
            btn.disabled = true;

            const emailField =
                loginForm.querySelector("#loginEmail") ||
                loginForm.querySelector("#email");
            const passwordField =
                loginForm.querySelector("#loginPassword") ||
                loginForm.querySelector("#password");
            // Collect values from the form fields. We trim/validate on the
            // client side for better UX but always validate on the server.
            const email = emailField ? emailField.value : "";
            const password = passwordField ? passwordField.value : "";

            if (!isValidEmail(email)) {
                alert("Please enter a valid email address.");
                btn.textContent = originalText;
                btn.disabled = false;
                return;
            }

            try {
                const res = await fetch(`${API_BASE}/auth/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password }),
                });
                const data = await res.json();
                if (res.ok) {
                    // Persist the token in localStorage to keep the example simple.
                    // NOTE: Storing JWTs in localStorage exposes them to XSS; for
                    // production prefer secure, HTTP-only cookies.
                    localStorage.setItem("token", data.token);
                    localStorage.setItem("last_user_token", data.token);
                    if (email) {
                        localStorage.setItem("last_user_email", email);
                    }
                    window.location.href = "dashboard.html";
                } else {
                    alert(
                        "Login failed: " +
                            (data.error || "Invalid credentials"),
                    );
                }
            } catch (err) {
                alert("Network error. Is the backend running?");
            } finally {
                btn.textContent = originalText;
                btn.disabled = false;
            }
        });
    }

    // Signup Form
    const signupForm = document.getElementById("signupForm");
    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const btn = signupForm.querySelector("button");
            const originalText = btn.textContent;
            btn.textContent = "Loading...";
            btn.disabled = true;

            const nameField =
                signupForm.querySelector("#signupName") ||
                signupForm.querySelector("#name");
            const emailField =
                signupForm.querySelector("#signupEmail") ||
                signupForm.querySelector("#email");
            const passwordField =
                signupForm.querySelector("#signupPassword") ||
                signupForm.querySelector("#password");
            const careerField =
                signupForm.querySelector("#signupCareer") ||
                signupForm.querySelector("#career");
            const photoField = signupForm.querySelector("#profilePhoto");

            // Gather form inputs
            const name = nameField ? nameField.value : "";
            const email = emailField ? emailField.value : "";
            const password = passwordField ? passwordField.value : "";
            const career_goal = careerField ? careerField.value : "";
            let profile_photo = null;

            if (!isValidEmail(email)) {
                alert("Only valid email addresses are allowed.");
                btn.textContent = originalText;
                btn.disabled = false;
                return;
            }

            if (!isStrongPassword(password)) {
                alert(
                    "Password must be at least 8 characters long and include letters, numbers, and symbols.",
                );
                btn.textContent = originalText;
                btn.disabled = false;
                return;
            }

            if (photoField && photoField.files && photoField.files[0]) {
                const file = photoField.files[0];
                if (!file.type.startsWith("image/")) {
                    alert(
                        "Please choose an image file for your profile photo.",
                    );
                    btn.textContent = originalText;
                    btn.disabled = false;
                    return;
                }

                profile_photo = await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(reader.result);
                    reader.onerror = () =>
                        reject(new Error("Failed to read profile photo."));
                    reader.readAsDataURL(file);
                });
            }

            try {
                const res = await fetch(`${API_BASE}/auth/signup`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        name,
                        email,
                        password,
                        career_goal,
                        profile_photo,
                    }),
                });
                const data = await res.json();
                if (res.ok) {
                    // On success, suggest the user log in. Consider auto-login
                    // flows in the future but avoid exposing credentials.
                    alert(
                        "Account successfully created! Please log in to continue.",
                    );
                    window.location.href = "index.html";
                } else {
                    alert("Signup failed: " + (data.error || "Unknown error"));
                }
            } catch (err) {
                alert("Network error. Is the backend running?");
            } finally {
                btn.textContent = originalText;
                btn.disabled = false;
            }
        });
    }

    // Admin Login Form
    const adminLoginForm = document.getElementById("adminLoginForm");
    const userProfileBtn = document.getElementById("userProfileBtn");
    if (adminLoginForm) {
        adminLoginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const btn = adminLoginForm.querySelector("button");
            const originalText = btn.textContent;
            btn.textContent = "Verifying...";
            btn.disabled = true;

            const usernameField =
                adminLoginForm.querySelector("#adminUsername");
            const passwordField =
                adminLoginForm.querySelector("#adminPassword");
            const username = usernameField ? usernameField.value.trim() : "";
            const password = passwordField ? passwordField.value : "";

            try {
                const res = await fetch(`${API_BASE}/admin/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password }),
                });
                const data = await res.json();

                if (res.ok) {
                    localStorage.setItem("admin_token", data.token);
                    if (data.admin && data.admin.username) {
                        localStorage.setItem(
                            "admin_username",
                            data.admin.username,
                        );
                    }
                    window.location.href = "admin.html";
                } else {
                    alert(
                        "Admin login failed: " +
                            (data.error || "Invalid credentials"),
                    );
                }
            } catch (err) {
                alert("Network error. Is the backend running?");
            } finally {
                btn.textContent = originalText;
                btn.disabled = false;
            }
        });
    }

    if (userProfileBtn) {
        userProfileBtn.addEventListener("click", () => {
            localStorage.removeItem("token");
            localStorage.removeItem("last_user_token");
            window.location.href = "index.html";
        });
    }

    // --- Dashboard Protection & Data Load ---
    const isDashboard = window.location.pathname.endsWith("dashboard.html");
    if (isDashboard) {
        let dashboardStaticInitialized = false;

        function initializeDashboardStaticUI(u) {
            const fname = u.name.split(" ")[0];
            const welcomeMsg = document.querySelector(".welcome-msg h1");
            if (welcomeMsg) welcomeMsg.innerHTML = `Welcome back, ${fname}! 👋`;

            const avatar = document.querySelector(".avatar");
            if (avatar)
                avatar.textContent = u.name.substring(0, 2).toUpperCase();
            const userInfoName = document.querySelector(
                ".user-info span:first-child",
            );
            if (userInfoName) userInfoName.textContent = u.name;

            const careerBadge = document.querySelector(".career-badge");
            if (careerBadge)
                careerBadge.innerHTML = `<i class="ph-fill ph-code"></i> Target: ${u.career_goal || "Not set"}`;

            const logoutBtn = document.getElementById("logout-btn");
            if (logoutBtn) {
                logoutBtn.addEventListener("click", (e) => {
                    e.preventDefault();
                    localStorage.removeItem("token");
                    window.location.href = "index.html";
                });
            }

            document.querySelectorAll(".course-card").forEach((card) => {
                card.style.cursor = "pointer";
                card.setAttribute("role", "button");
                card.setAttribute("tabindex", "0");

                const triggerOpen = () => openRecommendedCourse(card, API_BASE);

                card.addEventListener("click", (event) => {
                    const clickedButton =
                        event.target.closest(".start-course-btn");
                    if (clickedButton || event.currentTarget === card) {
                        triggerOpen();
                    }
                });

                card.addEventListener("keydown", (event) => {
                    if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        triggerOpen();
                    }
                });
            });

            const recommendedCourse = localStorage.getItem(
                "last_recommended_course",
            );
            if (recommendedCourse) {
                try {
                    const parsed = JSON.parse(recommendedCourse);
                    showCourseInsight(
                        parsed.title,
                        `${parsed.note} Last opened on ${new Date(
                            parsed.clickedAt,
                        ).toLocaleString()}.`,
                    );
                } catch (error) {
                    // Ignore malformed stored state.
                }
            }
        }

        const token = localStorage.getItem("token");
        if (!token) {
            // Not logged in, kick out to login page
            window.location.href = "index.html";
        } else {
            // Function to refresh dashboard data once
            async function refreshDashboardData() {
                try {
                    const [dashRes, roadRes] = await Promise.all([
                        fetch(`${API_BASE}/student/dashboard`, {
                            headers: { Authorization: `Bearer ${token}` },
                        }),
                        fetch(`${API_BASE}/student/roadmap`, {
                            headers: { Authorization: `Bearer ${token}` },
                        }),
                    ]);

                    if (!dashRes.ok) {
                        localStorage.removeItem("token");
                        window.location.href = "index.html";
                        throw new Error("Unauthorized");
                    }

                    const data = await dashRes.json();
                    const roadData = roadRes.ok ? await roadRes.json() : null;

                    if (data.user) {
                        const u = data.user;
                        if (!dashboardStaticInitialized) {
                            initializeDashboardStaticUI(u);
                            dashboardStaticInitialized = true;
                        }

                        // Update Readiness Score (Real-time)
                        const rs = u.readiness_score || 0;
                        const readinessSpan =
                            document.querySelector(".progress-value");
                        const readinessLabel =
                            document.querySelector(".progress-label");
                        const readinessMessage =
                            document.getElementById("readinessMessage");
                        if (readinessSpan) readinessSpan.textContent = `${rs}%`;
                        if (readinessLabel) {
                            readinessLabel.textContent =
                                rs >= 80
                                    ? "On Track"
                                    : rs >= 60
                                      ? "Ready"
                                      : "Building";
                        }
                        const progressCircle =
                            document.querySelector(".circular-progress");
                        if (progressCircle) {
                            progressCircle.style.background = `conic-gradient(var(--primary) ${rs * 3.6}deg, var(--bg-card) 0deg)`;
                        }

                        // Update Current Skills
                        const currentContainer = document.getElementById(
                            "currentSkillsContainer",
                        );
                        if (currentContainer) {
                            currentContainer.innerHTML = "";
                            if (u.skills && u.skills.length > 0) {
                                u.skills.forEach((skill) => {
                                    currentContainer.innerHTML += `<span class="tag tag-success">${skill}</span>`;
                                });
                            } else {
                                currentContainer.innerHTML =
                                    '<span style="color: var(--text-muted); font-size: 0.85rem;">No skills logged yet.</span>';
                            }
                        }

                        // Update Completed Skills
                        const completedContainer = document.getElementById(
                            "completedSkillsContainer",
                        );
                        if (completedContainer) {
                            completedContainer.innerHTML = "";
                            if (
                                u.completed_skills &&
                                u.completed_skills.length > 0
                            ) {
                                u.completed_skills.forEach((skill) => {
                                    completedContainer.innerHTML += `<span class="tag tag-success">${skill}</span>`;
                                });
                            } else {
                                completedContainer.innerHTML =
                                    '<span style="font-size: 0.85rem; color: var(--text-muted);">No completed modules yet.</span>';
                            }
                        }
                        // Update Missing Skills & Roadmap
                        const missingContainer = document.getElementById(
                            "missingSkillsContainer",
                        );
                        const roadmapContainer = document.getElementById(
                            "roadmapTimelineContainer",
                        );

                        if (
                            roadData &&
                            roadData.roadmap &&
                            roadData.roadmap.generated_steps
                        ) {
                            const steps = roadData.roadmap.generated_steps;

                            if (missingContainer) {
                                missingContainer.innerHTML = "";
                                const allKnown = [
                                    ...(u.skills || []),
                                    ...(u.completed_skills || []),
                                ];
                                let missingFound = false;
                                let missingCount = 0;

                                steps.forEach((step) => {
                                    if (!allKnown.includes(step.target_skill)) {
                                        missingContainer.innerHTML += `<span class="tag tag-warning">${step.target_skill}</span>`;
                                        missingFound = true;
                                        missingCount += 1;
                                    }
                                });

                                if (!missingFound) {
                                    missingContainer.innerHTML =
                                        '<span class="tag tag-success">All roadmap skills mastered!</span>';
                                }

                                if (readinessMessage) {
                                    if (rs >= 100 || missingCount === 0) {
                                        readinessMessage.textContent =
                                            "Great job! You have mastered the current roadmap.";
                                    } else if (rs >= 80) {
                                        readinessMessage.textContent = `You're almost there! Master ${missingCount} more skill${missingCount === 1 ? "" : "s"} to reach full readiness.`;
                                    } else {
                                        const remainingToTarget = Math.max(
                                            0,
                                            80 - rs,
                                        );
                                        readinessMessage.textContent = `You're building momentum. Master ${missingCount} skill${missingCount === 1 ? "" : "s"} and gain ${remainingToTarget}% more readiness to reach 80%.`;
                                    }
                                }
                            }

                            // Render Timeline
                            if (roadmapContainer) {
                                roadmapContainer.innerHTML = "";
                                steps.forEach((step, index) => {
                                    const isCompleted = (
                                        u.completed_skills || []
                                    ).includes(step.target_skill);
                                    const itemClass = isCompleted
                                        ? "timeline-item completed"
                                        : "timeline-item";
                                    const titleColor = isCompleted
                                        ? ""
                                        : "color: var(--primary);";

                                    let actionHtml = "";
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

                                // Re-attach events to completion buttons
                                document
                                    .querySelectorAll(".start-module-btn")
                                    .forEach((btn) => {
                                        btn.addEventListener(
                                            "click",
                                            async (e) => {
                                                const skillName =
                                                    e.target.getAttribute(
                                                        "data-skill",
                                                    );
                                                const originalText =
                                                    e.target.textContent;
                                                e.target.disabled = true;
                                                e.target.textContent =
                                                    "Saving...";

                                                try {
                                                    const res = await fetch(
                                                        `${API_BASE}/student/mark-completed`,
                                                        {
                                                            method: "POST",
                                                            headers: {
                                                                Authorization: `Bearer ${token}`,
                                                                "Content-Type":
                                                                    "application/json",
                                                            },
                                                            body: JSON.stringify(
                                                                {
                                                                    skill: skillName,
                                                                },
                                                            ),
                                                        },
                                                    );
                                                    if (res.ok) {
                                                        const response =
                                                            await res.json();

                                                        // Show immediate success feedback
                                                        e.target.textContent =
                                                            "✓ Completed!";
                                                        e.target.style.backgroundColor =
                                                            "var(--success)";
                                                        e.target.style.color =
                                                            "white";

                                                        // Add pulse animation to readiness score
                                                        const readinessSpan =
                                                            document.querySelector(
                                                                ".progress-value",
                                                            );
                                                        if (readinessSpan) {
                                                            readinessSpan.style.animation =
                                                                "pulse 0.6s ease-out";
                                                        }

                                                        // Refresh data immediately
                                                        setTimeout(async () => {
                                                            await refreshDashboardData();

                                                            // Show success message
                                                            if (
                                                                response.new_readiness_score !==
                                                                undefined
                                                            ) {
                                                                const notification =
                                                                    document.createElement(
                                                                        "div",
                                                                    );
                                                                notification.textContent = `✓ Skill completed! Readiness: ${response.new_readiness_score}%`;
                                                                notification.style.cssText = `
                                                            position: fixed;
                                                            top: 20px;
                                                            right: 20px;
                                                            background: var(--success);
                                                            color: white;
                                                            padding: 1rem 1.5rem;
                                                            border-radius: 0.5rem;
                                                            z-index: 1000;
                                                            font-weight: 600;
                                                            animation: slideIn 0.3s ease-out;
                                                        `;
                                                                document.body.appendChild(
                                                                    notification,
                                                                );

                                                                setTimeout(
                                                                    () => {
                                                                        notification.style.animation =
                                                                            "slideOut 0.3s ease-out forwards";
                                                                        setTimeout(
                                                                            () =>
                                                                                notification.remove(),
                                                                            300,
                                                                        );
                                                                    },
                                                                    2000,
                                                                );
                                                            }
                                                        }, 200);
                                                    } else {
                                                        alert(
                                                            "Failed to mark completed.",
                                                        );
                                                        e.target.disabled = false;
                                                        e.target.textContent =
                                                            originalText;
                                                    }
                                                } catch (err) {
                                                    console.error(err);
                                                    e.target.disabled = false;
                                                    e.target.textContent =
                                                        originalText;
                                                }
                                            },
                                        );
                                    });
                            }
                        } else {
                            if (missingContainer)
                                missingContainer.innerHTML =
                                    '<span style="color: var(--text-muted); font-size: 0.85rem;">No analysis complete.</span>';
                            if (roadmapContainer)
                                roadmapContainer.innerHTML =
                                    '<div style="text-align: center; color: var(--text-muted); padding: 2rem;">No active roadmap. Go to Analyze Skills.</div>';
                        }
                    }
                } catch (error) {
                    console.error("Error refreshing dashboard:", error);
                }
            }

            // Initial load
            refreshDashboardData();

            // One-time setup for static UI elements and event handlers occurs inside refreshDashboardData.
        }
    }

    // Admin portal protection
    console.log("Checking if admin page...", window.location.href);
    if (isAdminPage()) {
        console.log("Admin page detected");
        const adminToken = localStorage.getItem("admin_token");
        console.log("Admin token:", adminToken ? "exists" : "missing");

        const adminLoginSection = document.getElementById("adminLoginSection");
        const adminDashboardShell = document.getElementById(
            "adminDashboardShell",
        );

        if (!adminToken) {
            // No token - show login form only
            console.log("No token, showing login form");
            if (adminLoginSection) {
                adminLoginSection.style.display = "block";
            }
            if (adminDashboardShell) {
                adminDashboardShell.style.display = "none";
                adminDashboardShell.style.visibility = "hidden";
            }
            return;
        }

        // Has token - show dashboard, hide login
        console.log("Token exists, showing dashboard");
        if (adminLoginSection) {
            adminLoginSection.style.display = "none";
        }
        if (adminDashboardShell) {
            adminDashboardShell.style.display = "flex";
            adminDashboardShell.style.visibility = "visible";
        }

        // Attach logout handlers
        const adminLogoutButtons = document.querySelectorAll(
            'a[data-admin-logout="true"], button[data-admin-logout="true"]',
        );
        console.log("Found logout buttons:", adminLogoutButtons.length);
        adminLogoutButtons.forEach((button) => {
            button.addEventListener("click", (e) => {
                e.preventDefault();
                localStorage.removeItem("admin_token");
                localStorage.removeItem("admin_username");
                window.location.href = "admin-login.html";
            });
        });

        // Fetch admin dashboard data and populate the UI
        (async function loadAdminData() {
            try {
                const res = await fetch(`${API_BASE}/admin/dashboard`, {
                    headers: { Authorization: `Bearer ${adminToken}` },
                });
                if (!res.ok) {
                    localStorage.removeItem("admin_token");
                    window.location.href = "admin-login.html";
                    return;
                }
                const payload = await res.json();

                // Populate stat cards (ensure admin.html defines these ids)
                const stats = payload.stats || {};
                const setText = (id, value) => {
                    const el = document.getElementById(id);
                    if (el) el.textContent = value !== undefined ? value : "0";
                };

                const activeUsers =
                    stats.active_users || stats.total_users || 0;
                const careerPaths = stats.career_paths || 0;
                const linkedCourses = stats.linked_courses || 0;
                const analysesRun = stats.skill_analyses_run || 0;

                setText("adminStatActiveUsers", activeUsers);
                setText("adminStatCareerPaths", careerPaths);
                setText("adminStatLinkedCourses", linkedCourses);
                setText("adminStatAnalysesRun", analysesRun);

                // Recent signups table
                const tbody = document.getElementById("recentSignupsBody");
                if (tbody) {
                    tbody.innerHTML = "";
                    (payload.recent_signups || []).forEach((u) => {
                        const tr = document.createElement("tr");
                        tr.innerHTML = `
                            <td style="min-width:200px;">
                                <div style="display:flex;gap:0.5rem;align-items:center;">
                                    <div class="admin-avatar">${(u.name || u.email || "--").substring(0, 2).toUpperCase()}</div>
                                    <div>
                                        <div style="font-weight:600">${u.name || "Unknown"}</div>
                                        <div style="font-size:0.85rem;color:var(--text-muted)">${u.email || ""}</div>
                                    </div>
                                </div>
                            </td>
                            <td>${u.career_goal || "—"}</td>
                            <td>${u.readiness_score || 0}%</td>
                            <td>${u.login_count || 0}</td>
                        `;
                        tbody.appendChild(tr);
                    });
                }

                // Career trends
                const trendsWrap = document.getElementById("careerTrends");
                if (trendsWrap) {
                    trendsWrap.innerHTML = "";
                    (payload.career_trends || []).slice(0, 8).forEach((t) => {
                        const d = document.createElement("div");
                        d.className = "trend-item";
                        d.innerHTML = `<div>${t._id || "Unknown"}</div><div class="trend-count">${t.count || 0}</div>`;
                        trendsWrap.appendChild(d);
                    });
                }
            } catch (err) {
                console.error("Failed to load admin data:", err);
            }
        })();
    }

    if (isAdminLoginPage()) {
        const adminToken = localStorage.getItem("admin_token");
        if (adminToken) {
            window.location.href = "admin.html";
        }
    }

    // Global Logout Handler for all authenticated pages (Profile, Analyze, Progress, Admin)
    if (!isDashboard) {
        const globalLogout = document.querySelector('a[href="index.html"]');
        if (globalLogout && globalLogout.textContent.includes("Logout")) {
            globalLogout.addEventListener("click", (e) => {
                e.preventDefault();
                localStorage.removeItem("token");
                window.location.href = "index.html";
            });
        }
    }
});
