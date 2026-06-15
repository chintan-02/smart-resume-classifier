import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
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
                radial-gradient(circle at 8% 0%, rgba(59,130,246,0.18), transparent 30%),
                radial-gradient(circle at 92% 8%, rgba(20,184,166,0.12), transparent 28%),
                linear-gradient(180deg, #07111f 0%, #0b1220 48%, #07111f 100%);
            color: #e5e7eb;
        }

        .block-container {
            padding-top: 1.05rem !important;
            padding-bottom: 2.5rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1280px;
        }

        [data-testid="stAppViewContainer"] {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1.2rem !important;
            background: linear-gradient(180deg, rgba(9,15,27,0.98), rgba(15,23,42,0.97));
            border-right: 1px solid rgba(148,163,184,0.14);
        }

        section[data-testid="stSidebar"] {
            color: #e5e7eb;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {
            color: #e5e7eb;
        }

        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
        section[data-testid="stSidebar"] .subtle {
            color: #aab6c5 !important;
        }

        section[data-testid="stSidebar"] hr {
            border-color: rgba(148,163,184,0.18) !important;
        }

        section[data-testid="stSidebar"] [data-testid="stAlert"] {
            color: #e5e7eb;
            background: rgba(30,41,59,0.72);
            border: 1px solid rgba(148,163,184,0.2);
        }

        h1, h2, h3, h4, h5, h6, p, li, label, span {
            color: inherit;
        }

        .resumeiq-hero {
            background: linear-gradient(135deg, rgba(37,99,235,0.24), rgba(13,148,136,0.18));
            border: 1px solid rgba(226,232,240,0.12);
            padding: 1.7rem 1.7rem 1.35rem 1.7rem;
            border-radius: 18px;
            box-shadow: 0 18px 45px rgba(0,0,0,0.26);
            margin-bottom: 1.3rem;
        }

        .resumeiq-kicker {
            color: #93c5fd;
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.55rem;
        }

        .resumeiq-title {
            margin: 0;
            color: #f8fafc;
            font-size: 2.35rem;
            line-height: 1.1;
            font-weight: 800;
            letter-spacing: 0;
        }

        .resumeiq-subtitle {
            color: #dbeafe;
            font-size: 1.04rem;
            font-weight: 650;
            margin-top: 0.45rem;
        }

        .resumeiq-description {
            color: #cbd5e1;
            font-size: 0.96rem;
            line-height: 1.7;
            margin-top: 0.8rem;
            margin-bottom: 1rem;
            max-width: 980px;
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
            font-weight: 700;
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
            background: rgba(15,23,42,0.58);
            border: 1px solid rgba(148,163,184,0.28);
            color: #e0f2fe;
            padding: 0.39rem 0.68rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 650;
            margin: 0.16rem 0.2rem 0.16rem 0;
        }

        .ui-card,
        .panel-card,
        .empty-state-card {
            background: rgba(15,23,42,0.68);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 14px;
            padding: 1.05rem;
            box-shadow: 0 12px 30px rgba(0,0,0,0.18);
            margin-bottom: 1rem;
        }

        .input-card {
            background: rgba(15,23,42,0.68);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 14px;
            padding: 1.05rem;
            box-shadow: 0 12px 30px rgba(0,0,0,0.18);
            margin-bottom: 1rem;
        }

        .metric-card,
        .score-card {
            background: linear-gradient(180deg, rgba(30,41,59,0.78), rgba(15,23,42,0.72));
            border: 1px solid rgba(148,163,184,0.18);
            border-radius: 14px;
            padding: 1rem;
            min-height: 118px;
            box-shadow: 0 10px 24px rgba(0,0,0,0.14);
        }

        .metric-label,
        .score-label {
            color: #b8c1d9;
            font-size: 0.78rem;
            margin-bottom: 0.45rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-weight: 700;
        }

        .metric-value,
        .score-value {
            color: #ffffff;
            font-size: 1.65rem;
            font-weight: 800;
            line-height: 1.15;
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
            color: #67e8f9;
            font-size: 0.9rem;
            font-weight: 700;
            margin-top: 0.35rem;
        }

        .section-title {
            color: #f8fafc;
            font-size: 1.08rem;
            margin: 0 0 0.2rem 0;
            font-weight: 800;
            letter-spacing: 0;
        }

        .section-subtitle {
            color: #aab7cf;
            font-size: 0.92rem;
            line-height: 1.6;
            margin-bottom: 0.85rem;
        }

        .section-label {
            color: #f8fafc;
            font-size: 1.02rem;
            margin-bottom: 0.65rem;
            font-weight: 760;
        }

        .nav-section-header {
            border-top: 1px solid rgba(148,163,184,0.18);
            padding-top: 1rem;
            margin-top: 0.8rem;
            margin-bottom: 0.7rem;
        }

        .nav-section-title {
            color: #f8fafc;
            font-size: 1.22rem;
            font-weight: 850;
            letter-spacing: 0;
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
            border-radius: 12px;
            padding: 0.62rem 0.72rem;
            margin-bottom: 0.45rem;
            font-size: 0.86rem;
            border: 1px solid rgba(148,163,184,0.18);
            background: rgba(15,23,42,0.58);
        }

        .status-badge strong {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .status-ready {
            color: #d1fae5;
            border-color: rgba(52,211,153,0.32);
            background: rgba(16,185,129,0.11);
        }

        .status-muted {
            color: #cbd5e1;
            border-color: rgba(148,163,184,0.18);
        }

        .feature-placeholder-card {
            background: rgba(15,23,42,0.62);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 14px;
            padding: 1rem;
            min-height: 132px;
            margin-bottom: 0.85rem;
        }

        .feature-placeholder-title {
            color: #f8fafc;
            font-size: 1rem;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }

        .feature-placeholder-copy {
            color: #b8c1d9;
            font-size: 0.9rem;
            line-height: 1.6;
        }

        .disclaimer-box {
            background: rgba(245,158,11,0.12);
            border: 1px solid rgba(251,191,36,0.28);
            border-radius: 12px;
            padding: 0.85rem 0.95rem;
            color: #fef3c7;
            line-height: 1.55;
            margin: 0.65rem 0 0.9rem 0;
        }

        .alert-banner {
            border-radius: 12px;
            padding: 0.85rem 0.95rem;
            margin: 0.65rem 0 0.9rem 0;
            line-height: 1.55;
            border: 1px solid rgba(148,163,184,0.18);
        }

        .alert-info {
            background: rgba(59,130,246,0.13);
            color: #dbeafe;
            border-color: rgba(96,165,250,0.34);
        }

        .alert-success {
            background: rgba(16,185,129,0.13);
            color: #d1fae5;
            border-color: rgba(52,211,153,0.34);
        }

        .alert-warning {
            background: rgba(245,158,11,0.14);
            color: #fef3c7;
            border-color: rgba(251,191,36,0.34);
        }

        .alert-danger {
            background: rgba(239,68,68,0.14);
            color: #fee2e2;
            border-color: rgba(248,113,113,0.34);
        }

        .empty-state-title {
            color: #f8fafc;
            font-size: 1.08rem;
            font-weight: 800;
            margin-bottom: 0.35rem;
        }

        .empty-state-message {
            color: #b8c1d9;
            line-height: 1.65;
            font-size: 0.94rem;
        }

        .insight-box {
            background: rgba(59,130,246,0.11);
            border-left: 4px solid rgba(96,165,250,0.86);
            padding: 0.9rem 1rem;
            border-radius: 12px;
            color: #dbeafe;
            margin-top: 0.65rem;
            margin-bottom: 0.8rem;
            line-height: 1.65;
        }

        div[data-testid="stFileUploader"],
        section[data-testid="stSidebar"] div[data-testid="stFileUploader"] {
            background: rgba(15,23,42,0.74) !important;
            border: 1px solid rgba(148,163,184,0.22) !important;
            border-radius: 14px;
            padding: 0.7rem;
            color: #e5e7eb !important;
        }

        div[data-testid="stFileUploaderDropzone"] {
            background: linear-gradient(145deg, rgba(2,6,23,0.96), rgba(15,23,42,0.92)) !important;
            border: 1px dashed rgba(96,165,250,0.46) !important;
            border-radius: 12px !important;
            color: #e5e7eb !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
            transition: border-color 160ms ease, background 160ms ease, box-shadow 160ms ease;
        }

        div[data-testid="stFileUploaderDropzone"]:hover {
            background: linear-gradient(145deg, rgba(15,23,42,0.98), rgba(30,58,95,0.82)) !important;
            border-color: rgba(103,232,249,0.72) !important;
            box-shadow: 0 10px 28px rgba(2,132,199,0.12);
        }

        div[data-testid="stFileUploader"] label,
        div[data-testid="stFileUploader"] p,
        div[data-testid="stFileUploader"] span,
        div[data-testid="stFileUploaderDropzone"] span,
        div[data-testid="stFileUploaderDropzone"] small,
        div[data-testid="stFileUploaderDropzone"] svg {
            color: #cbd5e1 !important;
            fill: currentColor !important;
        }

        div[data-testid="stFileUploaderDropzone"] button,
        div[data-testid="stFileUploaderDeleteBtn"] button {
            background: rgba(37,99,235,0.22) !important;
            border: 1px solid rgba(96,165,250,0.5) !important;
            color: #eff6ff !important;
        }

        div[data-testid="stFileUploaderDropzone"] button:hover,
        div[data-testid="stFileUploaderDeleteBtn"] button:hover {
            background: rgba(37,99,235,0.34) !important;
            border-color: rgba(125,211,252,0.72) !important;
        }

        div[data-testid="stFileUploaderFile"] {
            background: rgba(30,41,59,0.82) !important;
            border: 1px solid rgba(148,163,184,0.24) !important;
            border-radius: 10px !important;
            color: #e5e7eb !important;
        }

        div[data-testid="stFileUploaderFile"] span,
        div[data-testid="stFileUploaderFile"] small,
        div[data-testid="stFileUploaderFile"] svg {
            color: #e5e7eb !important;
            fill: currentColor !important;
        }

        textarea,
        input,
        [data-testid="stTextArea"] textarea,
        .stTextArea textarea,
        .stTextInput input,
        div[data-baseweb="textarea"] textarea,
        div[data-baseweb="input"] input {
            background-color: rgba(2,6,23,0.92) !important;
            color: #e5e7eb !important;
            border: 1px solid rgba(148,163,184,0.28) !important;
            border-radius: 12px !important;
            caret-color: #67e8f9 !important;
            box-shadow: none !important;
        }

        div[data-baseweb="textarea"],
        div[data-baseweb="input"] {
            background-color: rgba(2,6,23,0.92) !important;
            border: 1px solid rgba(148,163,184,0.18) !important;
            border-radius: 12px !important;
        }

        textarea:hover,
        input:hover,
        [data-testid="stTextArea"] textarea:focus,
        .stTextInput input:focus,
        div[data-baseweb="textarea"] textarea:focus,
        div[data-baseweb="input"] input:focus {
            border-color: rgba(103,232,249,0.76) !important;
            box-shadow: 0 0 0 2px rgba(34,211,238,0.12) !important;
            outline: none !important;
        }

        textarea::placeholder,
        input::placeholder {
            color: #94a3b8 !important;
            opacity: 1 !important;
        }

        button,
        div[data-testid="stButton"] button,
        .stButton > button,
        .stDownloadButton > button,
        button[kind="secondary"] {
            background: rgba(30,41,59,0.86) !important;
            border: 1px solid rgba(148,163,184,0.3) !important;
            color: #e5e7eb !important;
            border-radius: 10px !important;
        }

        button:hover,
        div[data-testid="stButton"] button:hover,
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        button[kind="secondary"]:hover {
            background: rgba(51,65,85,0.92) !important;
            border-color: rgba(96,165,250,0.56) !important;
            color: #ffffff !important;
        }

        div[data-testid="stButton"] button[kind="primary"],
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #2563eb, #0f766e) !important;
            border-color: rgba(125,211,252,0.5) !important;
            color: #ffffff !important;
        }

        button:disabled,
        div[data-testid="stButton"] button:disabled,
        .stButton > button:disabled,
        .stDownloadButton > button:disabled {
            background: rgba(30,41,59,0.48) !important;
            border-color: rgba(148,163,184,0.16) !important;
            color: #94a3b8 !important;
            opacity: 0.78 !important;
        }

        div[data-testid="stMetric"] {
            background: rgba(15,23,42,0.62);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 12px;
            padding: 0.8rem;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem;
            border-bottom: 1px solid rgba(148,163,184,0.18);
        }

        .stTabs [data-baseweb="tab"] {
            background: rgba(15,23,42,0.54);
            border: 1px solid rgba(148,163,184,0.14);
            border-bottom: none;
            border-radius: 10px 10px 0 0;
            color: #cbd5e1;
            font-weight: 650;
            padding: 0.55rem 0.85rem;
        }

        .stTabs [aria-selected="true"] {
            color: #ffffff !important;
            background: rgba(37,99,235,0.24) !important;
        }

        div[data-testid="stExpander"],
        details {
            background: rgba(15,23,42,0.72) !important;
            border: 1px solid rgba(148,163,184,0.22) !important;
            border-radius: 12px !important;
            color: #e5e7eb !important;
            overflow: hidden;
        }

        div[data-testid="stExpander"] summary,
        details summary {
            background: rgba(15,23,42,0.82) !important;
            color: #e5e7eb !important;
            border-radius: 12px !important;
        }

        div[data-testid="stExpander"] summary:hover,
        details summary:hover {
            background: rgba(30,41,59,0.92) !important;
        }

        div[data-testid="stExpander"] summary span,
        details summary span,
        div[data-testid="stExpander"] p,
        div[data-testid="stExpander"] span {
            color: #e5e7eb !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stExpander"] {
            background: rgba(15,23,42,0.78) !important;
            border-color: rgba(148,163,184,0.24) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stExpander"] summary,
        section[data-testid="stSidebar"] div[data-testid="stExpander"] summary span {
            color: #e5e7eb !important;
            font-weight: 650;
        }

        .version-panel {
            display: grid;
            gap: 0.48rem;
            padding: 0.15rem 0.1rem 0.25rem;
        }

        .version-app-name {
            color: #f8fafc;
            font-size: 0.98rem;
            font-weight: 800;
            padding-bottom: 0.4rem;
            border-bottom: 1px solid rgba(148,163,184,0.18);
        }

        .version-row {
            display: grid;
            grid-template-columns: minmax(5.4rem, auto) 1fr;
            gap: 0.65rem;
            align-items: start;
            font-size: 0.82rem;
            line-height: 1.4;
        }

        .version-label {
            color: #cbd5e1 !important;
            font-weight: 700;
        }

        .version-value {
            color: #e5e7eb !important;
            overflow-wrap: anywhere;
        }

        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            background: rgba(15,23,42,0.78) !important;
            border: 1px solid rgba(148,163,184,0.22) !important;
            border-radius: 12px !important;
            overflow: hidden;
            color: #e5e7eb !important;
        }

        div[data-testid="stDataFrame"] div,
        div[data-testid="stTable"] div,
        div[data-testid="stDataFrame"] span,
        div[data-testid="stTable"] span {
            color: #e5e7eb !important;
        }

        div[data-testid="stDataFrame"] [role="grid"],
        div[data-testid="stDataFrame"] [role="row"],
        div[data-testid="stDataFrame"] [role="columnheader"],
        div[data-testid="stDataFrame"] [role="gridcell"] {
            background-color: rgba(15,23,42,0.88) !important;
            color: #e5e7eb !important;
            border-color: rgba(148,163,184,0.16) !important;
        }

        table {
            width: 100%;
            background: rgba(15,23,42,0.86) !important;
            color: #e5e7eb !important;
            border-collapse: collapse;
        }

        thead,
        thead tr,
        th {
            background: rgba(30,41,59,0.96) !important;
            color: #f8fafc !important;
            border-color: rgba(148,163,184,0.22) !important;
        }

        tbody,
        tbody tr,
        td {
            background: rgba(15,23,42,0.86) !important;
            color: #e5e7eb !important;
            border-color: rgba(148,163,184,0.16) !important;
        }

        tbody tr:nth-child(even),
        tbody tr:nth-child(even) td {
            background: rgba(30,41,59,0.62) !important;
        }

        th,
        td {
            padding: 0.55rem 0.7rem !important;
        }

        hr {
            margin-top: 0.7rem !important;
            margin-bottom: 0.7rem !important;
            border-color: rgba(148,163,184,0.16) !important;
        }

        .footer-note {
            color: #94a3b8;
            font-size: 0.88rem;
            margin-top: 1.1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
