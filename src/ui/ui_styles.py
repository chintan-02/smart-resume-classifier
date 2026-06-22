import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --riq-bg: #070b14;
            --riq-surface: rgba(15, 23, 42, 0.74);
            --riq-surface-strong: rgba(15, 23, 42, 0.92);
            --riq-border: rgba(148, 163, 184, 0.18);
            --riq-border-strong: rgba(125, 211, 252, 0.34);
            --riq-text: #f8fafc;
            --riq-muted: #aab7cf;
            --riq-soft: #cbd5e1;
            --riq-blue: #60a5fa;
            --riq-cyan: #67e8f9;
            --riq-green: #34d399;
            --riq-amber: #fbbf24;
            --riq-red: #f87171;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        [data-testid="collapsedControl"] {
            display: flex !important;
            opacity: 1 !important;
            visibility: visible !important;
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 0%, rgba(37, 99, 235, 0.22), transparent 32%),
                radial-gradient(circle at 88% 3%, rgba(20, 184, 166, 0.16), transparent 30%),
                radial-gradient(circle at 52% 100%, rgba(99, 102, 241, 0.12), transparent 34%),
                linear-gradient(180deg, #070b14 0%, #0b1120 45%, #070b14 100%);
            color: var(--riq-text);
        }

        .block-container {
            padding-top: 1.05rem !important;
            padding-bottom: 2.7rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1320px;
        }

        [data-testid="stAppViewContainer"] {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1.1rem !important;
            background:
                linear-gradient(180deg, rgba(7, 11, 20, 0.98), rgba(15, 23, 42, 0.98)),
                radial-gradient(circle at 30% 0%, rgba(37, 99, 235, 0.16), transparent 28%);
            border-right: 1px solid rgba(148, 163, 184, 0.16);
        }

        body,
        .stApp,
        section[data-testid="stSidebar"] {
            color: var(--riq-text);
        }

        section[data-testid="stSidebar"] * {
            color: #e5e7eb !important;
        }

        div[data-testid="stMarkdownContainer"],
        div[data-testid="stMarkdownContainer"] p {
            color: var(--riq-soft);
        }

        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"],
        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
            color: var(--riq-soft) !important;
        }

        section[data-testid="stSidebar"] hr {
            border-color: rgba(148, 163, 184, 0.18) !important;
        }

        h1, h2, h3, h4, h5, h6, p, li, label, span {
            color: inherit;
        }

        .resumeiq-hero {
            position: relative;
            overflow: hidden;
            background:
                linear-gradient(135deg, rgba(37, 99, 235, 0.26), rgba(20, 184, 166, 0.16)),
                linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(15, 23, 42, 0.76));
            border: 1px solid rgba(226, 232, 240, 0.14);
            padding: 1.7rem;
            border-radius: 24px;
            box-shadow: 0 24px 70px rgba(0, 0, 0, 0.34);
            margin-bottom: 1.35rem;
        }

        .resumeiq-hero::before {
            content: "";
            position: absolute;
            width: 280px;
            height: 280px;
            top: -150px;
            right: -90px;
            background: radial-gradient(circle, rgba(103, 232, 249, 0.22), transparent 66%);
            pointer-events: none;
        }

        .resumeiq-hero::after {
            content: "";
            position: absolute;
            inset: 0;
            background-image:
                linear-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
            background-size: 28px 28px;
            mask-image: linear-gradient(90deg, rgba(0,0,0,0.42), transparent 78%);
            pointer-events: none;
        }

        .resumeiq-hero-grid {
            position: relative;
            z-index: 1;
            display: grid;
            grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.65fr);
            gap: 1.35rem;
            align-items: stretch;
        }

        .resumeiq-kicker {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            color: #bfdbfe;
            background: rgba(37, 99, 235, 0.18);
            border: 1px solid rgba(147, 197, 253, 0.24);
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            padding: 0.35rem 0.64rem;
            margin-bottom: 0.75rem;
        }

        .resumeiq-title {
            margin: 0;
            color: #ffffff;
            font-size: clamp(2.15rem, 4vw, 3.5rem);
            line-height: 1.02;
            font-weight: 900;
            letter-spacing: -0.045em;
        }

        .resumeiq-subtitle {
            color: #dbeafe;
            font-size: 1.08rem;
            font-weight: 720;
            margin-top: 0.55rem;
        }

        .resumeiq-description {
            color: var(--riq-soft);
            font-size: 0.98rem;
            line-height: 1.75;
            margin-top: 0.8rem;
            margin-bottom: 1.05rem;
            max-width: 880px;
        }

        .resumeiq-hero-panel {
            background: rgba(2, 6, 23, 0.38);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 18px;
            padding: 1rem;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
        }

        .hero-panel-title {
            color: #f8fafc;
            font-size: 0.92rem;
            font-weight: 850;
            margin-bottom: 0.75rem;
        }

        .hero-panel-row {
            display: flex;
            justify-content: space-between;
            gap: 0.75rem;
            align-items: center;
            padding: 0.7rem 0;
            border-top: 1px solid rgba(148, 163, 184, 0.13);
        }

        .hero-panel-row:first-of-type {
            border-top: 0;
            padding-top: 0;
        }

        .hero-panel-label {
            color: #b8c1d9;
            font-size: 0.82rem;
            line-height: 1.35;
        }

        .hero-panel-value {
            color: #ffffff;
            font-size: 0.82rem;
            font-weight: 800;
            white-space: nowrap;
        }

        .hero-disclaimer {
            display: inline-flex;
            margin-top: 0.75rem;
            color: #d1fae5;
            background: rgba(16,185,129,0.12);
            border: 1px solid rgba(52,211,153,0.28);
            border-radius: 999px;
            padding: 0.42rem 0.72rem;
            font-size: 0.86rem;
            font-weight: 760;
        }

        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.48rem;
        }

        .ui-badge,
        .hero-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            background: rgba(15, 23, 42, 0.66);
            border: 1px solid rgba(148, 163, 184, 0.28);
            color: #e0f2fe;
            padding: 0.39rem 0.68rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 680;
            margin: 0.16rem 0.2rem 0.16rem 0;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
        }

        .ui-card,
        .panel-card,
        .empty-state-card {
            background:
                linear-gradient(180deg, rgba(15, 23, 42, 0.78), rgba(15, 23, 42, 0.62));
            border: 1px solid var(--riq-border);
            border-radius: 18px;
            padding: 1.08rem;
            box-shadow: 0 16px 38px rgba(0, 0, 0, 0.20);
            margin-bottom: 1rem;
        }

        .input-card {
            background:
                linear-gradient(180deg, rgba(15, 23, 42, 0.82), rgba(15, 23, 42, 0.66));
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 18px;
            padding: 1.08rem;
            box-shadow: 0 16px 38px rgba(0, 0, 0, 0.20);
            margin-bottom: 1rem;
        }

        .metric-card,
        .score-card {
            position: relative;
            overflow: hidden;
            background:
                linear-gradient(180deg, rgba(30, 41, 59, 0.82), rgba(15, 23, 42, 0.72));
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 18px;
            padding: 1rem;
            min-height: 118px;
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.17);
        }

        .metric-card::before,
        .score-card::before {
            content: "";
            position: absolute;
            inset: 0 0 auto 0;
            height: 3px;
            background: linear-gradient(90deg, rgba(96, 165, 250, 0.86), rgba(52, 211, 153, 0.86));
        }

        .metric-label,
        .score-label {
            color: #b8c1d9;
            font-size: 0.76rem;
            margin-bottom: 0.45rem;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            font-weight: 800;
        }

        .metric-value,
        .score-value {
            color: #ffffff;
            font-size: 1.58rem;
            font-weight: 900;
            line-height: 1.15;
            letter-spacing: -0.03em;
        }

        .metric-subtext,
        .score-helper,
        .subtle {
            color: #b8c1d9;
            font-size: 0.9rem;
            line-height: 1.65;
            margin-top: 0.4rem;
        }

        .score-grade {
            color: var(--riq-cyan);
            font-size: 0.9rem;
            font-weight: 780;
            margin-top: 0.35rem;
        }

        .section-title {
            color: #f8fafc;
            font-size: 1.1rem;
            margin: 0 0 0.2rem 0;
            font-weight: 880;
            letter-spacing: -0.015em;
        }

        .section-subtitle {
            color: #aab7cf;
            font-size: 0.92rem;
            line-height: 1.62;
            margin-bottom: 0.85rem;
        }

        .section-label {
            color: #f8fafc;
            font-size: 1.02rem;
            margin-bottom: 0.65rem;
            font-weight: 820;
            letter-spacing: -0.01em;
        }

        .nav-section-header {
            border-top: 1px solid rgba(148, 163, 184, 0.18);
            padding-top: 1rem;
            margin-top: 0.8rem;
            margin-bottom: 0.7rem;
        }

        .nav-section-title {
            color: #f8fafc;
            font-size: 1.22rem;
            font-weight: 900;
            letter-spacing: -0.02em;
        }

        .nav-section-subtitle {
            color: #aab7cf;
            font-size: 0.92rem;
            line-height: 1.6;
            margin-top: 0.25rem;
        }

        .status-badge {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.65rem;
            border-radius: 13px;
            padding: 0.64rem 0.74rem;
            margin-bottom: 0.45rem;
            font-size: 0.86rem;
            border: 1px solid rgba(148, 163, 184, 0.18);
            background: rgba(15, 23, 42, 0.58);
        }

        .status-badge strong {
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.045em;
        }

        .status-ready {
            color: #d1fae5;
            border-color: rgba(52, 211, 153, 0.32);
            background: rgba(16, 185, 129, 0.11);
        }

        .status-muted {
            color: #cbd5e1;
            border-color: rgba(148, 163, 184, 0.18);
        }

        .feature-placeholder-card {
            background: rgba(15, 23, 42, 0.62);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 16px;
            padding: 1rem;
            min-height: 132px;
            margin-bottom: 0.85rem;
        }

        .feature-placeholder-title {
            color: #f8fafc;
            font-size: 1rem;
            font-weight: 850;
            margin-bottom: 0.45rem;
        }

        .feature-placeholder-copy {
            color: #b8c1d9;
            font-size: 0.9rem;
            line-height: 1.6;
        }

        .disclaimer-box {
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(251, 191, 36, 0.28);
            border-radius: 13px;
            padding: 0.85rem 0.95rem;
            color: #fef3c7;
            line-height: 1.55;
            margin: 0.65rem 0 0.9rem 0;
        }

        .alert-banner {
            border-radius: 13px;
            padding: 0.85rem 0.95rem;
            margin: 0.65rem 0 0.9rem 0;
            line-height: 1.55;
            border: 1px solid rgba(148, 163, 184, 0.18);
        }

        .alert-info {
            background: rgba(59, 130, 246, 0.13);
            color: #dbeafe;
            border-color: rgba(96, 165, 250, 0.34);
        }

        .alert-success {
            background: rgba(16, 185, 129, 0.13);
            color: #d1fae5;
            border-color: rgba(52, 211, 153, 0.34);
        }

        .alert-warning {
            background: rgba(245, 158, 11, 0.14);
            color: #fef3c7;
            border-color: rgba(251, 191, 36, 0.34);
        }

        .alert-danger {
            background: rgba(239, 68, 68, 0.14);
            color: #fee2e2;
            border-color: rgba(248, 113, 113, 0.34);
        }

        .empty-state-title {
            color: #f8fafc;
            font-size: 1.08rem;
            font-weight: 850;
            margin-bottom: 0.35rem;
        }

        .empty-state-message {
            color: #b8c1d9;
            line-height: 1.65;
            font-size: 0.94rem;
        }

        .insight-box {
            background: rgba(59, 130, 246, 0.11);
            border-left: 4px solid rgba(96, 165, 250, 0.86);
            padding: 0.9rem 1rem;
            border-radius: 13px;
            color: #dbeafe;
            margin-top: 0.65rem;
            margin-bottom: 0.8rem;
            line-height: 1.65;
        }

        div[data-testid="stTextArea"] textarea,
        div[data-testid="stTextInput"] input {
            background: rgba(15, 23, 42, 0.72) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(148, 163, 184, 0.22) !important;
            border-radius: 13px !important;
            caret-color: var(--riq-cyan) !important;
        }

        div[data-testid="stTextArea"] textarea:focus,
        div[data-testid="stTextInput"] input:focus {
            border-color: rgba(103, 232, 249, 0.76) !important;
            box-shadow: 0 0 0 3px rgba(103, 232, 249, 0.08) !important;
            outline: none !important;
        }

        div[data-testid="stTextArea"] textarea::placeholder,
        div[data-testid="stTextInput"] input::placeholder {
            color: #94a3b8 !important;
            opacity: 1 !important;
        }

        div[data-testid="stFileUploader"] {
            background: rgba(15, 23, 42, 0.38);
            border: 1px dashed rgba(148, 163, 184, 0.28);
            border-radius: 16px;
            padding: 0.75rem;
        }

        div[data-testid="stButton"] button {
            background: rgba(30, 41, 59, 0.88) !important;
            border: 1px solid rgba(148, 163, 184, 0.30) !important;
            color: #e5e7eb !important;
            border-radius: 11px !important;
            font-weight: 720 !important;
            transition: transform 120ms ease, border-color 120ms ease, background 120ms ease;
        }

        div[data-testid="stButton"] button:hover {
            transform: translateY(-1px);
            border-color: rgba(125, 211, 252, 0.52) !important;
            background: rgba(30, 41, 59, 1) !important;
        }

        div[data-testid="stButton"] button[kind="primary"] {
            background: linear-gradient(135deg, #2563eb, #0f766e) !important;
            border-color: rgba(125, 211, 252, 0.52) !important;
            color: #ffffff !important;
        }

        div[data-testid="stButton"] button:disabled {
            background: rgba(30, 41, 59, 0.48) !important;
            border-color: rgba(148, 163, 184, 0.16) !important;
            color: #94a3b8 !important;
            opacity: 0.78 !important;
            transform: none;
        }

        div[data-testid="stMetric"] {
            background: rgba(15, 23, 42, 0.62);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 14px;
            padding: 0.8rem;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.18);
        }

        .stTabs [data-baseweb="tab"] {
            background: rgba(15, 23, 42, 0.54);
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-bottom: none;
            border-radius: 11px 11px 0 0;
            color: #cbd5e1;
            font-weight: 700;
            padding: 0.55rem 0.85rem;
        }

        .stTabs [aria-selected="true"] {
            color: #ffffff !important;
            background: rgba(37, 99, 235, 0.24) !important;
        }

        hr {
            margin-top: 0.7rem !important;
            margin-bottom: 0.7rem !important;
            border-color: rgba(148, 163, 184, 0.16) !important;
        }

        .footer-note {
            color: #94a3b8;
            font-size: 0.88rem;
            margin-top: 1.1rem;
        }

        @media (max-width: 900px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .resumeiq-hero {
                padding: 1.2rem;
                border-radius: 20px;
            }

            .resumeiq-hero-grid {
                grid-template-columns: 1fr;
            }

            .resumeiq-title {
                font-size: 2.3rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
