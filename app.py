import asyncio
import html
import json
from pathlib import Path

import streamlit as st

from agents.agent_orchestrator import AgentOrchestrator
from agents.deal_historian import DealHistorian


st.set_page_config(
    page_title="Deal Oracle · Deal Intelligence",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# Visual system
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600&display=swap');

:root {
  --bg: #0b0b0d;
  --panel: #101013;
  --panel-2: #141417;
  --line: #242428;
  --text: #f2f0eb;
  --muted: #949196;
  --muted-2: #68666c;
  --gold: #f3b83f;
  --gold-2: #ffc85b;
  --green: #77c96b;
  --red: #e96a61;
  --blue: #80a9d6;
}

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: var(--bg); color: var(--text); }
.block-container { max-width: 1420px; padding: 0 42px 70px; }
[data-testid="stHeader"] { background: rgba(11,11,13,.96); }
[data-testid="stSidebar"] { display: none; }
footer { visibility: hidden; }

/* remove Streamlit chrome that creates accidental spacing */
[data-testid="stToolbar"], [data-testid="stDecoration"] { display:none; }
.element-container { margin-bottom: 0 !important; }

.topbar {
  height: 78px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  border-bottom:1px solid var(--line);
  margin-bottom: 56px;
}
.brand { display:flex; align-items:center; gap:11px; }
.brand-dot { width:12px; height:12px; border-radius:50%; background:var(--gold); box-shadow:0 0 0 5px rgba(243,184,63,.08); }
.brand-name { font-family:'Playfair Display', Georgia, serif; font-size:25px; color:var(--text); }
.brand-tag { font-family:'DM Mono', monospace; font-size:11px; letter-spacing:2px; color:#77747a; margin-left:4px; }

.nav-caption { font-family:'DM Mono',monospace; text-transform:uppercase; letter-spacing:1.6px; font-size:11px; color:#6e6c71; margin-bottom:10px; }
.hero-kicker { font-family:'DM Mono',monospace; text-transform:uppercase; letter-spacing:4px; font-size:11px; color:#8e8b90; margin-bottom:17px; }
.hero-kicker span { color:var(--gold); }
h1, h2, h3, h4 { font-family:'Playfair Display', Georgia, serif !important; color:var(--text) !important; font-weight:500 !important; }
.hero-title { font-family:'Playfair Display', Georgia, serif; font-size:64px; line-height:1.02; letter-spacing:-2.8px; margin:0; color:var(--text); }
.hero-copy { color:#969399; font-size:16px; margin-top:15px; max-width:780px; }
.hero-copy strong { color:var(--gold); }

/* Streamlit buttons as nav / actions */
.stButton > button {
  background: transparent !important;
  border: 1px solid transparent !important;
  color:#89868c !important;
  font-family:'DM Mono',monospace !important;
  text-transform:uppercase !important;
  letter-spacing:1.4px !important;
  font-size:10px !important;
  border-radius: 999px !important;
  padding: 7px 13px !important;
  min-height: 34px !important;
  box-shadow:none !important;
}
.stButton > button:hover { color:var(--text) !important; border-color:#35353a !important; }
.action-button .stButton > button,
.stButton > button[kind="primary"] {
  background:var(--gold) !important; color:#111 !important; border-color:var(--gold) !important;
  font-family:'DM Sans',sans-serif !important; text-transform:none !important; letter-spacing:0 !important;
  font-size:14px !important; font-weight:700 !important; padding:10px 18px !important;
}

.metric-card, .panel, .table-shell {
  background:linear-gradient(180deg, #111114 0%, #0f0f12 100%);
  border:1px solid var(--line);
  border-radius:3px;
}
.metric-card { padding:25px 26px 22px; min-height:138px; }
.metric-label { font-family:'DM Mono',monospace; font-size:10px; letter-spacing:1.7px; text-transform:uppercase; color:#77747b; }
.metric-value { font-family:'Playfair Display',Georgia,serif; font-size:43px; line-height:1; margin-top:14px; color:var(--text); }
.metric-value.gold { color:var(--gold); }
.metric-sub { color:#7c7980; font-size:12px; margin-top:11px; }

.section-label { font-family:'DM Mono',monospace; text-transform:uppercase; letter-spacing:2px; color:#747177; font-size:10px; margin:42px 0 14px; }
.panel { padding:28px; }
.panel-title { font-family:'Playfair Display',Georgia,serif; color:var(--text); font-size:25px; }
.panel-subtitle { color:#77747a; font-size:13px; margin-top:5px; }
.big-number { font-family:'Playfair Display',Georgia,serif; color:var(--gold); font-size:48px; }

.bar-wrap { margin-top:18px; }
.bar-row { display:flex; align-items:center; gap:13px; margin:13px 0; }
.bar-name { width:105px; color:#b0adb2; font-size:13px; }
.bar-track { flex:1; height:5px; background:#242428; border-radius:5px; overflow:hidden; }
.bar-fill { height:100%; background:var(--gold); border-radius:5px; }
.bar-value { width:40px; text-align:right; color:#c6c2c8; font-size:12px; font-family:'DM Mono',monospace; }

.signal { border-top:1px solid var(--line); padding:17px 0; }
.signal:first-child { border-top:0; }
.signal-title { color:#ddd9dd; font-weight:600; font-size:14px; }
.signal-copy { color:#77747b; font-size:12px; margin-top:4px; }
.dot { display:inline-block; width:7px; height:7px; border-radius:50%; margin-right:8px; }
.dot.gold { background:var(--gold); } .dot.red { background:var(--red); } .dot.green { background:var(--green); }

.badge { display:inline-block; padding:5px 9px; border:1px solid #35353a; border-radius:999px; font-family:'DM Mono',monospace; font-size:9px; letter-spacing:1px; text-transform:uppercase; color:#aaa7ad; }
.badge.gold { color:var(--gold); border-color:#5a4826; }
.badge.red { color:#f08a82; border-color:#59312e; }
.badge.green { color:#8ad47e; border-color:#2e4e2a; }

.quote { border-left:2px solid var(--gold); padding:5px 0 5px 18px; color:#c8c4c8; font-size:15px; line-height:1.7; }

.table-shell { overflow:hidden; }
.table-head, .table-row { display:grid; grid-template-columns:2fr 1fr 1fr .8fr .7fr .7fr; gap:20px; align-items:center; padding:17px 20px; }
.table-head { color:#6e6b71; font-family:'DM Mono',monospace; text-transform:uppercase; letter-spacing:1.4px; font-size:9px; border-bottom:1px solid var(--line); }
.table-row { border-bottom:1px solid #1c1c20; color:#c8c5c9; font-size:13px; }
.table-row:last-child { border-bottom:0; }
.table-row strong { color:#eee; font-size:14px; }
.table-row small { display:block; color:#68666c; margin-top:3px; }

.timeline { border-left:1px solid #35353a; margin-left:7px; padding-left:23px; }
.timeline-item { position:relative; padding-bottom:24px; }
.timeline-item:before { content:''; position:absolute; left:-28px; top:5px; width:8px; height:8px; border-radius:50%; background:var(--gold); box-shadow:0 0 0 4px var(--bg); }
.timeline-time { font-family:'DM Mono',monospace; color:#66636a; font-size:10px; letter-spacing:1px; text-transform:uppercase; }
.timeline-title { color:#e6e2e6; font-size:14px; margin-top:5px; }
.timeline-copy { color:#77747a; font-size:12px; margin-top:4px; line-height:1.55; }

input, textarea, [data-baseweb="select"] > div {
  background:#101013 !important; border-color:#2b2b30 !important; color:#eee !important;
}
[data-baseweb="select"] * { color:#eee !important; }
.stTextInput label, .stTextArea label, .stSelectbox label { color:#77747a !important; font-family:'DM Mono',monospace !important; text-transform:uppercase; letter-spacing:1.3px; font-size:10px !important; }
.stChatInputContainer { background:#101013 !important; border-color:#303036 !important; }

.footer-note { color:#57545a; font-size:11px; line-height:1.6; margin-top:45px; border-top:1px solid var(--line); padding-top:18px; }

@media (max-width: 900px) {
  .block-container { padding:0 18px 50px; }
  .hero-title { font-size:45px; }
  .topbar { margin-bottom:35px; }
}
</style>
""",
    unsafe_allow_html=True,
)


DEALS = {
    "DL001": {
        "account": "Acme Health", "industry": "Healthcare", "stage": "Negotiation", "value": 125000,
        "probability": 72, "owner": "Sarah Mitchell", "health": 78, "last_activity": "2 hours ago",
        "next_step": "Pricing & ROI review",
        "notes": [
            "Budget approved in Q4.", "HubSpot is the primary competitor.", "Sarah Johnson is the internal champion.",
            "Executive sponsor is involved.", "Customer says pricing is high and requested ROI justification.", "Security review is complete.",
        ],
    },
    "DL002": {
        "account": "Northstar Retail", "industry": "Retail", "stage": "Evaluation", "value": 84000,
        "probability": 48, "owner": "Daniel Kumar", "health": 54, "last_activity": "Yesterday",
        "next_step": "Technical validation",
        "notes": [
            "Budget is still pending approval.", "Two vendors are being evaluated.", "Technical team requested a security review.",
            "Timeline may slip beyond the current quarter.", "No executive sponsor has been identified.",
        ],
    },
    "DL003": {
        "account": "Vertex Logistics", "industry": "Logistics", "stage": "Proposal", "value": 210000,
        "probability": 61, "owner": "Ananya Rao", "health": 69, "last_activity": "3 days ago",
        "next_step": "Proposal review",
        "notes": [
            "Budget is approved.", "VP Operations is the executive sponsor.", "Champion requested implementation timeline.",
            "No active competitor has been reported.",
        ],
    },
    "DL004": {
        "account": "Nimbus Systems", "industry": "SaaS", "stage": "Discovery", "value": 165000,
        "probability": 39, "owner": "Priya Shah", "health": 43, "last_activity": "5 days ago",
        "next_step": "Executive discovery call",
        "notes": [
            "Business case is still being formed.", "Procurement requested pricing ranges.", "No executive sponsor has been identified.",
            "A competitor is already an incumbent vendor.",
        ],
    },
}


def run(coro):
    return asyncio.run(coro)


def esc(value):
    return html.escape(str(value))


def money(value):
    return f"₹{value:,.0f}"


def seed_memory(deal_id):
    key = f"seeded_{deal_id}"
    if st.session_state.get(key):
        return
    deal = DEALS[deal_id]
    historian = DealHistorian()
    base = f"Deal ID {deal_id} | Account: {deal['account']} | Industry: {deal['industry']} | Stage: {deal['stage']} | "
    run(historian.store_memory(base + " ".join(deal["notes"])))
    objection_notes = [n for n in deal["notes"] if any(w in n.lower() for w in ["pricing", "price", "roi", "objection"])]
    if objection_notes:
        run(historian.store_memory(base + "Customer objection context: " + " ".join(objection_notes)))
    st.session_state[key] = True


def nav():
    st.markdown(
        """
        <div class="topbar">
          <div class="brand"><span class="brand-dot"></span><span class="brand-name">Deal Oracle</span><span class="brand-tag">UNIFIED</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    current = st.session_state.get("page", "Command Center")
    labels = ["Command Center", "Portfolio", "Deal Brief", "Reflect Insights"]
    cols = st.columns([1.2, 1.1, 1.1, 1.25, 1.1])
    with cols[0]:
        st.markdown('<div class="nav-caption">Workspace</div>', unsafe_allow_html=True)
    for i, label in enumerate(labels, start=1):
        with cols[i]:
            if st.button(label, key=f"nav_{label}"):
                st.session_state.page = label
                st.rerun()
    return current


orchestrator = AgentOrchestrator()
page = nav()

# Deal selection is shared across pages.
select_cols = st.columns([1.7, 1, 1, 1.1])
with select_cols[0]:
    selected = st.selectbox(
        "ACTIVE DEAL",
        list(DEALS),
        format_func=lambda x: f"{DEALS[x]['account']}  ·  {x}",
        label_visibility="visible",
    )
with select_cols[1]:
    deal = DEALS[selected]
    st.markdown(f'<div class="metric-card"><div class="metric-label">Deal value</div><div class="metric-value gold">{money(deal["value"])}</div><div class="metric-sub">Current opportunity</div></div>', unsafe_allow_html=True)
with select_cols[2]:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Win probability</div><div class="metric-value">{deal["probability"]}%</div><div class="metric-sub">CRM estimate</div></div>', unsafe_allow_html=True)
with select_cols[3]:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Health signal</div><div class="metric-value">{deal["health"]}</div><div class="metric-sub">Out of 100 · {deal["stage"]}</div></div>', unsafe_allow_html=True)

seed_memory(selected)


# -----------------------------------------------------------------------------
# Command Center
# -----------------------------------------------------------------------------
if page == "Command Center":
    st.markdown('<div class="section-label">Command center</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-kicker"><span>●</span> LIVE DEAL INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Deal Intelligence</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-copy"><strong>{esc(deal["account"])}</strong> is a {esc(deal["stage"])} opportunity worth <strong>{money(deal["value"])}</strong>. The agent combines deal memory, transparent risk signals and objection coaching into one workspace.</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Portfolio pulse</div>', unsafe_allow_html=True)
    total = sum(d["value"] for d in DEALS.values())
    active = sum(1 for d in DEALS.values() if d["stage"] not in {"Closed Won", "Closed Lost"})
    avg_prob = round(sum(d["probability"] for d in DEALS.values()) / len(DEALS))
    won = 1
    m = st.columns(4)
    cards = [
        ("ACTIVE DEALS", str(active), "Across the demo portfolio", False),
        ("PIPELINE VALUE", money(total), "Current modeled pipeline", True),
        ("AVG WIN SIGNAL", f"{avg_prob}%", "CRM probability average", False),
        ("MEMORY BANK", "LIVE", "Local fallback + optional Hindsight", False),
    ]
    for col, (label, value, sub, gold) in zip(m, cards):
        with col:
            cls = "gold" if gold else ""
            st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value {cls}">{value}</div><div class="metric-sub">{sub}</div></div>', unsafe_allow_html=True)

    left, right = st.columns([1.45, 1])
    with left:
        st.markdown('<div class="section-label">Pipeline by account</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel"><div class="panel-title">Where the money lives</div><div class="panel-subtitle">Current demo opportunities by account value</div>', unsafe_allow_html=True)
        max_v = max(d["value"] for d in DEALS.values())
        for d in DEALS.values():
            pct = int(d["value"] / max_v * 100)
            st.markdown(f'<div class="bar-row"><div class="bar-name">{esc(d["account"])}</div><div class="bar-track"><div class="bar-fill" style="width:{pct}%"></div></div><div class="bar-value">{money(d["value"]).replace("₹", "")}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="section-label">Stage distribution</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel"><div class="panel-title">Where deals live</div><div class="panel-subtitle">Current stage mix</div>', unsafe_allow_html=True)
        stages = {}
        for d in DEALS.values(): stages[d["stage"]] = stages.get(d["stage"], 0) + 1
        for stage, count in stages.items():
            pct = int(count / len(DEALS) * 100)
            st.markdown(f'<div class="bar-row"><div class="bar-name">{esc(stage)}</div><div class="bar-track"><div class="bar-fill" style="width:{pct}%"></div></div><div class="bar-value">{count}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown('<div class="section-label">AI executive brief</div>', unsafe_allow_html=True)
        brief = run(orchestrator.executive_briefer.generate_brief(selected))
        memories = brief.get("brief", [])
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        if memories:
            text = memories[0].get("content", str(memories[0])) if isinstance(memories[0], dict) else str(memories[0])
            st.markdown(f'<div class="quote">{esc(text)}</div>', unsafe_allow_html=True)
        else:
            st.info("No memory recorded for this deal yet.")
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="section-label">Key signals</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        for note in deal["notes"][:4]:
            st.markdown(f'<div class="signal"><div class="signal-title"><span class="dot gold"></span>{esc(note)}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Portfolio
# -----------------------------------------------------------------------------
elif page == "Portfolio":
    st.markdown('<div class="section-label">Portfolio</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Every deal, one memory away</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-copy">Open an opportunity to inspect its health, history and agent-generated brief.</div>', unsafe_allow_html=True)
    st.write("")

    rows = []
    for deal_id, d in DEALS.items():
        rows.append(f'''<div class="table-row"><div><strong>{esc(d["account"])}</strong><small>{esc(d["owner"])} · {esc(d["industry"])}</small></div><div>{esc(d["stage"])}</div><div>{money(d["value"])}</div><div>{d["health"]}</div><div>{d["probability"]}%</div><div><span class="badge gold">OPEN →</span></div></div>''')
    st.markdown('<div class="section-label">Showing 4 / 4</div>', unsafe_allow_html=True)
    st.markdown('<div class="table-shell"><div class="table-head"><div>Deal</div><div>Stage</div><div>Value</div><div>Health</div><div>Win %</div><div>Status</div></div>' + ''.join(rows) + '</div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Deal Brief
# -----------------------------------------------------------------------------
elif page == "Deal Brief":
    st.markdown('<div class="section-label">Deal brief</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">A memory-powered briefing</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-copy">The Briefer recalls stored interactions, then surfaces the context, risks and next action for the selected opportunity.</div>', unsafe_allow_html=True)
    st.write("")

    left, right = st.columns([1.45, .85])
    with left:
        brief = run(orchestrator.executive_briefer.generate_brief(selected))
        risk = run(orchestrator.risk_predictor.run(selected))
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(f'<div class="panel-title">{esc(deal["account"])}</div><div class="panel-subtitle">{esc(deal["stage"])} · {money(deal["value"])} · {deal["health"]}/100 health</div><br>', unsafe_allow_html=True)
        summary = f"{deal['account']} is currently in {deal['stage']} with a CRM win probability of {deal['probability']}%. The next action is {deal['next_step'].lower()}."
        st.markdown(f'<div class="quote">{esc(summary)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Next best action</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="big-number" style="font-size:30px;color:#f3b83f">{esc(deal["next_step"])}</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Risks recalled</div>', unsafe_allow_html=True)
        if risk["risks"]:
            for item in risk["risks"]:
                st.markdown(f'<div class="signal"><div class="signal-title"><span class="dot red"></span>{esc(item["risk"])}</div><div class="signal-copy">Rule-based signal from recorded deal context.</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="signal"><div class="signal-title"><span class="dot green"></span>No active risk signals</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Retain into memory</div><div class="panel-subtitle">Save a new interaction so it can surface on the next recall.</div><br>', unsafe_allow_html=True)
        interaction = st.text_area("Interaction", placeholder="Log a stakeholder move, objection or breakthrough...", height=130, label_visibility="collapsed")
        if st.button("Retain memory", type="primary", use_container_width=True):
            if interaction.strip():
                run(orchestrator.deal_historian.capture_interaction(f"Deal ID {selected}: {interaction.strip()}"))
                st.success("Memory retained.")
                st.rerun()
            else:
                st.warning("Enter an interaction first.")
        st.markdown('<div class="section-label">Memory stream</div>', unsafe_allow_html=True)
        memories = run(orchestrator.deal_historian.retrieve_history(selected))
        for item in memories[:4]:
            content = item.get("content", str(item)) if isinstance(item, dict) else str(item)
            st.markdown(f'<div class="signal"><div class="signal-title">{esc(content[:115])}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Reflect Insights
# -----------------------------------------------------------------------------
elif page == "Reflect Insights":
    st.markdown('<div class="section-label">Reflect insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Patterns from the memory bank</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-copy">Lightweight pattern discovery across the recorded portfolio. These signals are exploratory and should not be treated as validated sales forecasts.</div>', unsafe_allow_html=True)

    risk_values = [d["health"] for d in DEALS.values()]
    won_avg = max(risk_values)
    lost_avg = min(risk_values)
    m = st.columns(4)
    cards = [("DEALS", len(DEALS), "Demo portfolio", False), ("MEMORIES", "LIVE", "Local memory bank", True), ("HEALTH RANGE", f"{min(risk_values)}–{max(risk_values)}", "Current demo deals", False), ("MODEL TYPE", "RULES", "Transparent detector", False)]
    for col, (label, value, sub, gold) in zip(m, cards):
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value {"gold" if gold else ""}">{value}</div><div class="metric-sub">{sub}</div></div>', unsafe_allow_html=True)

    result = run(orchestrator.pattern_miner.run())
    patterns = result.get("patterns", [])
    st.markdown('<div class="section-label">Patterns from memory</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    insights = [
        ("Health signals need context", "The risk detector combines explicit memory keywords with a transparent score. Treat the score as an attention signal, not a probability."),
        ("Objections can become reusable playbook entries", "Captured pricing, security and timeline concerns can be retrieved by the Objection Coach for future conversations."),
        ("Executive sponsorship matters to monitoring", "The current rules explicitly look for executive-sponsor language and flag deals where it is absent."),
        ("Memory capture compounds value", "The more deal-specific notes you retain, the more useful the historian, briefer and coach become."),
    ]
    for col, (title, body) in zip(cols, insights):
        with col:
            st.markdown(f'<div class="panel" style="margin-bottom:18px"><div class="panel-title" style="font-size:21px">{esc(title)}</div><div class="panel-subtitle" style="line-height:1.65;margin-top:10px">{esc(body)}</div></div>', unsafe_allow_html=True)
    if patterns:
        st.markdown(f'<div class="panel"><div class="panel-title" style="font-size:20px">Shared terms</div><div class="panel-subtitle" style="margin-top:9px">{esc(" · ".join(patterns))}</div></div>', unsafe_allow_html=True)


st.markdown('<div class="footer-note">Deal Oracle is a hackathon-ready MVP. Memory can run locally or through an optional Hindsight-compatible service. Risk and pattern modules are deterministic prototypes rather than validated predictive models.</div>', unsafe_allow_html=True)
