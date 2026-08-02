(function () {
  const root = document.documentElement;
  const languageButton = document.querySelector("[data-language-toggle]");
  const themeButton = document.querySelector("[data-theme-toggle]");
  const accessButton = document.querySelector("[data-access-toggle]");
  const routeDemo = document.querySelector("[data-route-demo]");
  const routeInput = document.querySelector("#route-input");
  const routeResult = document.querySelector("[data-route-result]");
  const loadMizarButton = document.querySelector("[data-load-mizar]");
  const accessOrder = ["base", "autism-calm", "adhd-sprint", "deep-work"];
  const accessLabels = {
    base: "Access",
    "autism-calm": "Autism Calm",
    "adhd-sprint": "ADHD Sprint",
    "deep-work": "Deep Work"
  };

  function readSetting(key, fallback) {
    try {
      return localStorage.getItem(key) || fallback;
    } catch (_error) {
      return fallback;
    }
  }

  function writeSetting(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (_error) {
      return;
    }
  }

  function setLanguage(value) {
    const language = value === "fr" ? "fr" : "en";
    root.lang = language;
    if (languageButton) {
      languageButton.textContent = "Language: " + language.toUpperCase();
      languageButton.setAttribute("aria-pressed", String(language === "fr"));
    }
    writeSetting("securedme.quanthor.language", language);
  }

  function setTheme(value) {
    const theme = value === "day" ? "day" : "night";
    root.dataset.theme = theme;
    root.style.colorScheme = theme === "day" ? "light" : "dark";
    if (themeButton) {
      themeButton.textContent = "Theme: " + (theme === "day" ? "Day" : "Night");
      themeButton.setAttribute("aria-pressed", String(theme === "night"));
    }
    writeSetting("securedme.quanthor.theme", theme);
  }

  function setAccess(value) {
    const access = accessOrder.includes(value) ? value : "base";
    root.dataset.access = access;
    if (accessButton) {
      accessButton.textContent = accessLabels[access];
    }
    writeSetting("securedme.quanthor.access", access);
  }

  setLanguage(readSetting("securedme.quanthor.language", "en"));
  setTheme(readSetting("securedme.quanthor.theme", "night"));
  setAccess(readSetting("securedme.quanthor.access", "base"));

  if (languageButton) {
    languageButton.addEventListener("click", function () {
      setLanguage(root.lang === "fr" ? "en" : "fr");
    });
  }

  if (themeButton) {
    themeButton.addEventListener("click", function () {
      setTheme(root.dataset.theme === "night" ? "day" : "night");
    });
  }

  if (accessButton) {
    accessButton.addEventListener("click", function () {
      const current = accessOrder.indexOf(root.dataset.access || "base");
      setAccess(accessOrder[(current + 1) % accessOrder.length]);
    });
  }

  function renderRouteInspection() {
    if (!(routeInput instanceof HTMLTextAreaElement) || !routeResult) {
      return;
    }

    const value = routeInput.value.trim();
    const looksComplete = /\benviron\b/i.test(value) && /\bbegin\b/i.test(value) && /\bend\s*;/i.test(value);
    const looksLikeMizar = /\b(theorem|definition|registration|scheme)\b/i.test(value);
    const proposedRoute = looksComplete ? "verify_mizar" : looksLikeMizar ? "draft_mizar" : "needs_clarification";
    const explanation = looksComplete
      ? "Complete article markers detected. The local Mizar verifier is still required before any proof claim."
      : looksLikeMizar
        ? "Formal intent detected. Complete the article before sending it to the local verifier."
        : "The request needs a theorem statement, assumptions, or a complete Mizar article before routing.";

    routeResult.querySelector("strong").textContent = proposedRoute;
    routeResult.querySelector("p").textContent = explanation;
    const trace = routeResult.querySelector("dl > div:last-child dd");
    if (trace) {
      const auditToggle = document.querySelector("[data-audit-toggle]");
      trace.textContent = auditToggle instanceof HTMLInputElement && auditToggle.checked ? "Enabled" : "Disabled";
    }
  }

  routeDemo?.addEventListener("submit", function (event) {
    event.preventDefault();
    renderRouteInspection();
  });

  loadMizarButton?.addEventListener("click", function () {
    if (routeInput instanceof HTMLTextAreaElement) {
      routeInput.value = "environ\n  vocabularies XREAL_0;\nbegin\n  theorem for x being Real holds x + 0 = x;\nend;";
      renderRouteInspection();
      routeInput.focus();
    }
  });
})();
