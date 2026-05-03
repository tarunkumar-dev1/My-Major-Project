/*
  config.js
  Central place for frontend runtime configuration.

  - Local development uses the Flask backend on port 5000.
  - Deployed builds use a relative `/api` base so Vercel can proxy to Railway.

  If you deploy the frontend without a Vercel rewrite, replace the production
  fallback with your Railway backend URL.
*/
(function (global) {
    const hostname =
        global.location && global.location.hostname
            ? global.location.hostname
            : "";
    const isLocalHost = hostname === "localhost" || hostname === "127.0.0.1";

    const API_BASE_URL =
        global.SKILLGAP_API_BASE_URL ||
        (isLocalHost
            ? "http://127.0.0.1:5000/api"
            : "https://backendaiskillgap.tarunkumar17.me/api");

    global.SKILLGAP_CONFIG = Object.freeze({
        API_BASE_URL: API_BASE_URL.replace(/\/$/, ""),
    });
})(window);
