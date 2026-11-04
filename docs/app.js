/* GVL Events — single-file app logic. */
const sb = supabase.createClient(CONFIG.SUPABASE_URL, CONFIG.SUPABASE_ANON_KEY, {
  auth: { persistSession: true, autoRefreshToken: true },
});

const $ = (s) => document.querySelector(s);
const state = { tab: "new", events: [], deck: [], last: null };

// ---------- helpers ----------
function fmtWhen(e) {
  if (e.is_series) return e.recurrence || "Recurring";
  if (!e.start_at) return "";
  const d = new Date(e.start_at);
  const day = d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
  const time = d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
  return `${day} · ${time}`;
}
function fmtDayHead(e) {
  if (e.is_series) return "Weekly / recurring";
  const d = new Date(e.start_at);
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const diff = Math.round((new Date(d.getFullYear(), d.getMonth(), d.getDate()) - today) / 864e5);
  if (diff === 0) return "Today";
  if (diff === 1) return "Tomorrow";
  return d.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" });
}
function esc(s) { return (s || "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
function toast(msg) { const t = $("#toast"); t.textContent = msg; t.classList.add("show"); setTimeout(() => t.classList.remove("show"), 1400); }

function icsFor(e) {
  const pad = (n) => String(n).padStart(2, "0");
  const stamp = (d) => `${d.getUTCFullYear()}${pad(d.getUTCMonth() + 1)}${pad(d.getUTCDate())}T${pad(d.getUTCHours())}${pad(d.getUTCMinutes())}00Z`;
  const start = new Date(e.start_at);
  const end = e.end_at ? new Date(e.end_at) : new Date(start.getTime() + 2 * 3600e3);
  const lines = [
    "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//GVL Events//EN", "BEGIN:VEVENT",
    `UID:${e.id}@gvl-events`, `DTSTAMP:${stamp(new Date())}`, `DTSTART:${stamp(start)}`, `DTEND:${stamp(end)}`,
    `SUMMARY:${e.title.replace(/,/g, "\\,")}`,
    `LOCATION:${[e.venue, e.address].filter(Boolean).join(", ").replace(/,/g, "\\,")}`,
    `DESCRIPTION:${(e.register_url || e.url || "").replace(/,/g, "\\,")}`,
    `URL:${e.register_url || e.url || ""}`, "END:VEVENT", "END:VCALENDAR",
  ];
  return "data:text/calendar;charset=utf8," + encodeURIComponent(lines.join("\r\n"));
}

function linksHtml(e) {
  const reg = e.register_url || "";
  const url = e.url || "";
  let h = "";
  if (reg) h += `<a class="reg" href="${esc(reg)}" target="_blank" rel="noopener">Register / Tickets</a>`;
  if (url && url !== reg) h += `<a href="${esc(url)}" target="_blank" rel="noopener">Details</a>`;
  if (!reg && !url) h += `<span class="muted">No link found — search the title</span>`;
  if (!e.is_series && e.start_at) h += `<a href="${icsFor(e)}" download="${esc(e.id)}.ics">＋ Calendar</a>`;
  return `<div class="links">${h}</div>`;
}

// ---------- data ----------
async function load() {
  const { data, error } = await sb.from("events").select("*").neq("status", "no")
    .order("start_at", { ascending: true, nullsFirst: false });
  if (error) { toast(error.message); return; }
  const now = Date.now();
  state.events = data.filter((e) => e.is_series || !e.start_at || new Date(e.start_at).getTime() > now - 3600e3);
  render();
}

async function decide(e, status) {
  const { error } = await sb.from("events").update({ status, decided_at: new Date().toISOString() }).eq("id", e.id);
  if (error) { toast("Save failed: " + error.message); return false; }
  e.status = status;
  return true;
}

// ---------- rendering ----------
function counts() {
  const n = state.events.filter((e) => e.status === "new").length;
  const y = state.events.filter((e) => e.status === "yes" && !e.is_series).length;
  const w = state.events.filter((e) => e.status === "yes" && e.is_series).length;
  $("#count-new").textContent = n || "";
  $("#count-yes").textContent = y || "";
  $("#count-weekly").textContent = w || "";
}

function render() {
  counts();
  ["#deck", "#list", "#empty", "#actions"].forEach((s) => $(s).classList.add("hidden"));
  $("#undo").classList.toggle("hidden", !state.last);
  document.querySelectorAll("#tabs button").forEach((b) => b.classList.toggle("active", b.dataset.tab === state.tab));
  if (state.tab === "new") renderDeck();
  else renderList(state.tab);
}

function cardHtml(e, cls) {
  const where = [e.venue, e.city].filter(Boolean).join(" · ");
  const long = (e.description || "").length > 320;
  return `<article class="card ${cls}" data-id="${esc(e.id)}">
    <span class="cat ${esc(e.category)}">${esc(e.category)}${e.is_series ? " · recurring" : ""}${e.social_score >= 5 ? " · ★ high social" : ""}</span>
    <h2>${esc(e.title)}</h2>
    <div class="when">${esc(fmtWhen(e))}</div>
    <div class="where">${esc(where)}</div>
    ${e.description ? `<div class="desc">${esc(e.description)}</div>${long ? `<button class="more">more</button>` : ""}` : ""}
    ${linksHtml(e)}
    <div class="src">via ${esc((e.sources || [e.source]).join(", "))}</div>
  </article>`;
}

function renderDeck() {
  // Soonest first (true date comparison, not string); recurring cards come last.
  const ts = (e) => (e.is_series || !e.start_at) ? Infinity : new Date(e.start_at).getTime();
  state.deck = state.events.filter((e) => e.status === "new").sort((a, b) => ts(a) - ts(b));
  if (!state.deck.length) { $("#empty").classList.remove("hidden"); return; }
  const [top, next] = state.deck;
  $("#deck").innerHTML = (next ? cardHtml(next, "behind") : "") + cardHtml(top, "top");
  $("#deck").classList.remove("hidden");
  $("#actions").classList.remove("hidden");
  const more = $("#deck .card.top .more");
  if (more) more.onclick = () => { $("#deck .card.top .desc").classList.toggle("open"); more.textContent = more.textContent === "more" ? "less" : "more"; };
  attachSwipe($("#deck .card.top"));
}

async function act(status) {
  const e = state.deck[0];
  if (!e) return;
  const card = $("#deck .card.top");
  card.classList.add(status === "yes" ? "out-right" : "out-left");
  const ok = await decide(e, status);
  if (!ok) { card.classList.remove("out-right", "out-left"); return; }
  state.last = { e, prev: "new" };
  $("#undo").classList.remove("hidden");
  toast(status === "yes" ? (e.is_series ? "Added to Weekly" : "Going!") : "Gone forever");
  setTimeout(render, 220);
}

async function undo() {
  if (!state.last) return;
  const { e, prev } = state.last;
  if (await decide(e, prev)) {
    toast("Undone");
    state.last = null;
    $("#undo").classList.add("hidden");
    state.tab = "new";
    render();
  }
}

function attachSwipe(card) {
  let x0 = null, dx = 0;
  card.addEventListener("touchstart", (ev) => { x0 = ev.touches[0].clientX; dx = 0; card.style.transition = "none"; }, { passive: true });
  card.addEventListener("touchmove", (ev) => {
    if (x0 === null) return; dx = ev.touches[0].clientX - x0;
    card.style.transform = `translateX(${dx}px) rotate(${dx / 25}deg)`;
  }, { passive: true });
  card.addEventListener("touchend", () => {
    card.style.transition = ""; x0 = null;
    if (dx > 110) act("yes"); else if (dx < -110) act("no"); else card.style.transform = "";
  });
}

function renderList(which) {
  const items = state.events.filter((e) => e.status === "yes" && (which === "weekly" ? e.is_series : !e.is_series))
    .sort((a, b) => (a.start_at ? new Date(a.start_at).getTime() : Infinity) - (b.start_at ? new Date(b.start_at).getTime() : Infinity));
  if (!items.length) {
    $("#list").innerHTML = `<p class="big">${which === "weekly" ? "No weekly routines yet" : "Nothing on the calendar"}</p><p class="muted" style="text-align:center">Say yes to something in New.</p>`;
    $("#list").classList.remove("hidden"); return;
  }
  let html = "", lastHead = "";
  for (const e of items) {
    const head = fmtDayHead(e);
    if (head !== lastHead) { html += `<div class="day-head">${esc(head)}</div>`; lastHead = head; }
    html += `<div class="item" data-id="${esc(e.id)}">
      <h3>${esc(e.title)}</h3>
      <div class="when">${esc(fmtWhen(e))}</div>
      <div class="where">${esc([e.venue, e.address].filter(Boolean).join(" · "))}</div>
      ${linksHtml(e)}
      <button class="undo">Remove</button>
    </div>`;
  }
  $("#list").innerHTML = html;
  $("#list").classList.remove("hidden");
  $("#list").querySelectorAll(".undo").forEach((b) => b.onclick = async () => {
    const e = items.find((x) => x.id === b.closest(".item").dataset.id);
    if (await decide(e, "no")) { state.last = { e, prev: "yes" }; toast("Removed"); render(); }
  });
}

// ---------- auth + boot ----------
async function showLoginOrApp() {
  const { data: { session } } = await sb.auth.getSession();
  if (!session) {
    $("#login").classList.remove("hidden"); $("#tabs").classList.add("hidden");
    return;
  }
  $("#login").classList.add("hidden"); $("#tabs").classList.remove("hidden");
  await load();
}

$("#login-btn").onclick = async () => {
  const { error } = await sb.auth.signInWithPassword({ email: $("#email").value.trim(), password: $("#password").value });
  $("#login-err").textContent = error ? error.message : "";
  if (!error) showLoginOrApp();
};
$("#yes").onclick = () => act("yes");
$("#no").onclick = () => act("no");
$("#undo").onclick = undo;
document.querySelectorAll("#tabs button").forEach((b) => b.onclick = () => { state.tab = b.dataset.tab; render(); });
document.addEventListener("visibilitychange", () => { if (!document.hidden) load(); });

if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
showLoginOrApp();
