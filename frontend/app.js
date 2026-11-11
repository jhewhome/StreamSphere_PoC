const TOKEN_KEY = "streamsphere_token";
const USER_KEY = "streamsphere_user";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function getUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

function setSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(path, { ...options, headers });
  let data = null;
  const text = await response.text();
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { detail: text };
  }

  if (!response.ok) {
    const detail = data?.detail || response.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

function requireAuth(role = null) {
  const user = getUser();
  const token = getToken();
  if (!user || !token) {
    window.location.href = "/login";
    return null;
  }
  if (role && user.role !== role) {
    window.location.href = "/";
    return null;
  }
  return user;
}

async function logout() {
  try {
    await api("/api/logout", { method: "POST" });
  } catch {
    // ignore network/auth errors on logout
  }
  clearSession();
  window.location.href = "/login";
}

function movieCard(movie, extraHtml = "") {
  const genres = (movie.genres || []).join(", ");
  const score = movie.recommendation_score != null
    ? `<div class="score">Score: ${movie.recommendation_score}</div>`
    : "";
  return `
    <article class="card">
      <img src="${movie.poster_url || "https://picsum.photos/seed/fallback/300/450"}" alt="${movie.title}">
      <div class="card-body">
        <h3>${movie.title}</h3>
        <div class="meta">${movie.release_year || "n/a"} · ${genres || "Uncategorized"}</div>
        ${score}
        <p class="muted">${(movie.description || "").slice(0, 110)}${(movie.description || "").length > 110 ? "…" : ""}</p>
        ${extraHtml}
      </div>
    </article>
  `;
}

window.StreamSphere = {
  api,
  getToken,
  getUser,
  setSession,
  clearSession,
  requireAuth,
  logout,
  movieCard,
};
