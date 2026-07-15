/* Renderer isolato della sessione AGENT; usa il contratto agent_view del backend. */
// Aggiorna lo stato sintetico mostrato nella testata della modalita AGENT.
function updateAgentHeader(view) {
  if (!agentHeaderStatus) return;
  const tone = view && view.statusTone ? view.statusTone : "neutral";
  const label = view && view.statusLabel ? view.statusLabel : "Pronto";
  agentHeaderStatus.className = "agent-header-status " + tone;
  const labelNode = agentHeaderStatus.querySelector("span");
  if (labelNode) labelNode.textContent = label;
}

// Converte il contratto snake_case del backend in un oggetto comodo per la UI.
function normalizeAgentView(payload) {
  const raw = payload && payload.agent_view ? payload.agent_view : (payload || {});
  return {
    raw,
    status: raw.status || "idle",
    statusLabel: raw.status_label || "Pronto",
    statusTone: raw.status_tone || "neutral",
    symptom: raw.symptom || "",
    model: raw.model || "",
    activeRun: raw.active_run || "base",
    counters: raw.counters || {},
    steps: Array.isArray(raw.steps) ? raw.steps : [],
    capabilities: Array.isArray(raw.capabilities) ? raw.capabilities : [],
    iterations: Array.isArray(raw.iterations) ? raw.iterations : [],
    currentDiagnosis: raw.current_diagnosis || "",
    final: raw.final || null,
    lastError: raw.last_error || ""
  };
}

// Disegna il piano operativo usando soltanto gli stati calcolati dal backend.
function renderAgentPlan(steps) {
  if (!steps.length) return "";
  const labels = {completed: "Completato", active: "In corso", waiting: "In attesa"};
  const rows = steps.map((step, index) => {
    const status = step.status || "waiting";
    const marker = status === "completed" ? "&#10003;" : String(index + 1);
    return '<div class="agent-plan-step ' + escapeHtml(status) + '">' +
      '<span class="agent-step-marker">' + marker + '</span>' +
      '<span>' + escapeHtml(step.label || "Passaggio") + '</span>' +
      '<span class="agent-step-state">' + escapeHtml(labels[status] || status) + '</span>' +
      '</div>';
  }).join("");
  return '<section class="agent-section">' +
    '<div class="agent-section-heading"><h3>Piano dell\'agente</h3></div>' +
    '<div class="agent-plan">' + rows + '</div></section>';
}

// Mostra gli strumenti realmente disponibili per la sessione corrente.
function renderAgentCapabilities(capabilities) {
  if (!capabilities.length) return "";
  const chips = capabilities.map((item) =>
    '<span class="agent-tool">' + escapeHtml(item.label || item.id || "Strumento") + '</span>'
  ).join("");
  return '<section class="agent-section">' +
    '<div class="agent-section-heading"><h3>Strumenti e artefatti</h3></div>' +
    '<div class="agent-tools">' + chips + '</div></section>';
}

// Renderizza le differenze OP o TRAN con lo stesso formato compatto.
function renderAgentEvidence(evidence) {
  if (!Array.isArray(evidence) || !evidence.length) return "";
  const rows = evidence.map((item) => {
    const analysis = item.analysis === "tran" ? "TRAN" : "OP";
    let expectation = "";
    if (item.expectation_label) {
      const state = item.expectation_met === true ? "OK" :
        (item.expectation_met === false ? "non verificato" : "misura assente");
      const tone = item.expectation_met === true ? "met" :
        (item.expectation_met === false ? "failed" : "missing");
      expectation = '<small class="agent-expectation ' + tone + '">Atteso: ' +
        escapeHtml(item.expectation_label) + ' &middot; ' + state + '</small>';
    }
    return '<div class="agent-evidence-row">' +
      '<strong>' + escapeHtml(item.quantity || item.metric || "Grandezza") + '</strong>' +
      '<em>' + escapeHtml(item.base_display || "n/d") + ' &rarr; ' +
      escapeHtml(item.scenario_display || "n/d") + ' &middot; ' + analysis + '</em>' +
      expectation +
      '</div>';
  }).join("");
  return '<div class="agent-evidence-list">' + rows + '</div>';
}

// Costruisce una scheda test collegata alla run e ai suoi artefatti centrali.
function renderAgentScenario(scenario, testIndex) {
  const tone = scenario.tone || "neutral";
  const statusLabels = {
    spice_success: "SPICE success",
    spice_failed: "SPICE failed",
    rejected: "Rifiutato",
    completed: "Completato"
  };
  const actionChips = (scenario.actions || []).map((action) =>
    '<span class="agent-action-chip" title="' + escapeHtml(action.type || "") + '">' +
    escapeHtml(action.label || action.type || "Azione") +
    (action.detail ? ': ' + escapeHtml(action.detail) : '') + '</span>'
  ).join("");
  const technicalActions = (scenario.actions || []).map((action) =>
    escapeHtml(action.type || "unknown") + (action.detail ? ': ' + escapeHtml(action.detail) : '')
  ).join("<br>");
  const compare = (scenario.compare || []).map((item) => escapeHtml(item)).join(", ");
  const openLabel = scenario.has_transient ? "Apri viewer e grafici" : "Apri viewer";
  const openButton = scenario.viewer_available
    ? '<button type="button" class="agent-run-button" data-agent-run="' +
      escapeHtml(scenario.scenario_id || "base") + '">' + openLabel + '</button>'
    : '';
  const outcome = scenario.error || scenario.outcome_reason || "";

  return '<article class="agent-test ' + escapeHtml(tone) + '">' +
    '<div class="agent-test-header"><strong>Test ' + testIndex + ' &middot; ' +
    escapeHtml(scenario.title || scenario.scenario_id || "Scenario") + '</strong>' +
    '<span class="agent-test-status">' + escapeHtml(statusLabels[scenario.status] || scenario.status || "Preparato") + '</span></div>' +
    '<div class="agent-test-body">' +
    (scenario.hypothesis ? '<p><strong>Ipotesi:</strong> ' + escapeHtml(scenario.hypothesis) + '</p>' : '') +
    (actionChips ? '<div class="agent-action-list">' + actionChips + '</div>' : '') +
    renderAgentEvidence(scenario.evidence || []) +
    (scenario.outcome_label ? '<p><strong>Esito:</strong> ' + escapeHtml(scenario.outcome_label) + '</p>' : '') +
    '<div class="agent-test-footer">' + openButton +
    '<details><summary>Dettagli tecnici</summary><div class="agent-technical">' +
    'ID: ' + escapeHtml(scenario.scenario_id || "n/d") + '<br>' +
    'Azioni:<br>' + (technicalActions || "n/d") + '<br>' +
    'Confronto: ' + (compare || "n/d") + '<br>' +
    'Exit code: ' + escapeHtml(scenario.spice_exit_code ?? "n/d") +
    (outcome ? '<br>Valutazione: ' + escapeHtml(outcome) : '') +
    '</div></details></div></div></article>';
}

// Raggruppa uno o piu test indipendenti sotto la decisione che li ha prodotti.
function renderAgentIteration(iteration) {
  const scenarios = Array.isArray(iteration.scenarios) ? iteration.scenarios : [];
  const tests = scenarios.map((scenario, index) => renderAgentScenario(scenario, index + 1)).join("");
  return '<section class="agent-iteration">' +
    '<span class="agent-iteration-marker" aria-hidden="true"></span>' +
    '<h4 class="agent-iteration-title">Iterazione ' + escapeHtml(iteration.decision_number || "") + '</h4>' +
    tests +
    (iteration.reason ? '<details><summary class="agent-step-state">Motivo della decisione</summary>' +
      '<p class="agent-diagnosis">' + escapeHtml(iteration.reason) + '</p></details>' : '') +
    '</section>';
}

// Disegna la conclusione finale tenendo separate risposta AI ed evidenze SPICE.
function renderAgentFinal(finalView) {
  if (!finalView) return "";
  const openButton = finalView.last_run
    ? '<button type="button" class="agent-run-button" data-agent-run="' +
      escapeHtml(finalView.last_run) + '">Apri ultima evidenza</button>'
    : '';
  const answer = renderMarkdown(cleanupAgentText(finalView.answer || "Diagnosi autonoma completata."));
  const structured = (finalView.cause ? '<p><strong>Causa</strong><br>' + escapeHtml(finalView.cause) + '</p>' : '') +
    (finalView.verified_correction ? '<p><strong>Correzione verificata</strong><br>' +
      escapeHtml(finalView.verified_correction) + '</p>' : '');
  return '<section class="agent-section"><div class="agent-section-heading"><h3>Diagnosi finale</h3></div>' +
    '<div class="agent-final ' + escapeHtml(finalView.tone || "neutral") + '">' +
    '<span class="agent-final-label">' + escapeHtml(finalView.label || finalView.status || "Completata") + '</span>' +
    '<div class="agent-final-answer">' + structured + answer + '</div>' +
    renderAgentEvidence(finalView.evidence || []) +
    (openButton ? '<div class="agent-test-footer">' + openButton + '</div>' : '') +
    '</div></section>';
}

// Sostituisce le bolle con la vista persistente della sessione autonoma.
function renderAgentState(payload) {
  const view = normalizeAgentView(payload);
  updateAgentHeader(view);
  if (!view.symptom && view.status === "idle") {
    messages.innerHTML = '<div class="agent-empty"><div><strong>Nessuna diagnosi avviata</strong>' +
      '<span>Descrivi il comportamento desiderato. L\'agente analizzera la base run ed eseguira soltanto test controllati.</span></div></div>';
    return;
  }

  const counters = view.counters;
  const overview = '<div class="agent-overview">' +
      '<div class="agent-overview-item"><span>Run corrente</span><strong title="' + escapeHtml(view.activeRun) + '">' + escapeHtml(view.activeRun) + '</strong></div>' +
      '<div class="agent-overview-item"><span><abbr title="Run SPICE scenario realmente eseguite rispetto al limite massimo della diagnosi.">Scenari eseguiti</abbr></span><strong>' +
      escapeHtml(counters.scenarios || 0) + ' / ' + escapeHtml(counters.max_scenarios || 5) + '</strong></div>' +
      '<div class="agent-overview-item"><span><abbr title="Cicli decisionali usati dal modello: ogni ciclo sceglie nuovi test oppure conclude la diagnosi.">Decisioni agente</abbr></span><strong>' +
      escapeHtml(counters.decisions || 0) + ' / ' + escapeHtml(counters.max_decisions || 6) + '</strong></div></div>';
  const objective = '<section class="agent-section"><div class="agent-section-heading"><h3>Obiettivo diagnostico</h3>' +
    (view.model ? '<small>' + escapeHtml(view.model) + '</small>' : '') + '</div>' +
    '<p class="agent-objective">' + escapeHtml(view.symptom) + '</p></section>';
  const diagnosis = view.currentDiagnosis
    ? '<section class="agent-section"><div class="agent-section-heading"><h3>Valutazione corrente</h3></div>' +
      '<p class="agent-diagnosis">' + escapeHtml(view.currentDiagnosis) + '</p></section>'
    : '';
  const timeline = view.iterations.length
    ? '<section class="agent-section"><div class="agent-section-heading"><h3>Test ed evidenze</h3>' +
      '<small>' + escapeHtml(view.iterations.length) + ' iterazioni</small></div>' +
      '<div class="agent-timeline">' + view.iterations.map(renderAgentIteration).join("") + '</div></section>'
    : '';
  const error = view.lastError ? '<div class="agent-error">' + escapeHtml(view.lastError) + '</div>' : '';

  messages.innerHTML = '<div class="agent-dashboard">' + overview + objective +
    renderAgentPlan(view.steps) + renderAgentCapabilities(view.capabilities) +
    timeline + diagnosis + renderAgentFinal(view.final) + error + '</div>';
  messages.scrollTop = 0;
}

// Comunica l'operazione sincrona in corso senza creare messaggi persistenti.
function showAgentActivity(label) {
  updateAgentHeader({statusTone: "running", statusLabel: "In esecuzione"});
  const dashboard = messages.querySelector(".agent-dashboard");
  const live = document.createElement("div");
  live.className = "agent-live-state";
  live.textContent = label;
  if (dashboard) {
    const previous = dashboard.querySelector(".agent-live-state");
    if (previous) previous.remove();
    dashboard.prepend(live);
  } else {
    messages.innerHTML = "";
    messages.appendChild(live);
  }
}

// Mostra un errore operativo senza contaminare la cronologia CHAT.
function showAgentError(message) {
  updateAgentHeader({statusTone: "danger", statusLabel: "Errore"});
  const dashboard = messages.querySelector(".agent-dashboard");
  const node = document.createElement("div");
  node.className = "agent-error";
  node.textContent = message || "Operazione AGENT non riuscita.";
  if (dashboard) dashboard.prepend(node);
  else {
    messages.innerHTML = "";
    messages.appendChild(node);
  }
}

// Collega i pulsanti della timeline alla run gia renderizzata dalla pagina centrale.
messages.addEventListener("click", (event) => {
  if (activeWorkspaceMode !== "agent") return;
  const button = event.target.closest("[data-agent-run]");
  if (!button) return;
  const runId = button.dataset.agentRun || "base";
  window.location.href = workspaceUrl("/?run=" + encodeURIComponent(runId));
});
