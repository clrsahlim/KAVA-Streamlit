def load_css(T):
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    background-color: {T['bg']} !important;
    color: {T['text']} !important;
}}

[data-testid="stSidebar"] {{
    background-color: {T['sidebar_bg']} !important;
    border-right: 1px solid {T['card_border']};
}}

[data-testid="stSidebar"] * {{
    color: {T['text']} !important;
}}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stCheckbox label p,
[data-testid="stSidebar"] .stCaption p,
[data-testid="stSidebar"] span {{
    font-size: 0.9rem !important;
    color: {T['text']} !important;
}}

[data-testid="stSidebar"] .stCaption p {{
    font-size: 0.9rem !important;
}}

[data-testid="stSidebar"] input[type="checkbox"] {{
    accent-color: {T['accent']} !important;
}}

.dashboard-header p {{
    font-size: 1.05rem !important;
    font-weight: 400 !important;
}}

.dashboard-header h3 {{
    margin: 0 !important;
    padding: 0 !important;
    font-size: 1.9rem !important;
    font-weight: 700;
    line-height: 1.5 !important;
}}

[data-testid="stAppViewContainer"] > .main {{
    background-color: {T['bg']} !important;
}}

[data-testid="stAppViewContainer"] {{
    background-color: {T['bg']} !important;
}}

.block-container {{
    background-color: {T['bg']} !important;
    padding-top: 2rem !important;
}}

[data-testid="stExpander"] {{
    background-color: {T['metric_bg']} !important;
    border: 1px solid {T['card_border']} !important;
    border-radius: 12px !important;
    margin-bottom: 0.5rem !important;
}}

[data-testid="stExpander"] summary {{
    color: {T['text']} !important;
    font-weight: 700 !important;
    background-color: {T['metric_bg']} !important;
}}

[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {{
    font-size: 0.95rem !important;
    color: {T['text']} !important;
}}

[data-testid="stExpander"] > div,
[data-testid="stExpander"] > div > div,
[data-testid="stExpanderDetails"],
[data-testid="stExpanderDetails"] > div {{
    background-color: {T['metric_bg']} !important;
}}

[data-testid="stExpander"] p,
[data-testid="stExpander"] span,
[data-testid="stExpander"] div,
[data-testid="stExpander"] strong,
[data-testid="stExpander"] * {{
    color: {T['text']} !important;
    background-color: transparent !important;
}}

[data-testid="stExpanderDetails"] {{
    background-color: {T['metric_bg']} !important;
}}

[data-testid="stExpanderDetails"] * {{
    color: {T['text']} !important;
    background-color: transparent !important;
}}

details > div {{
    background-color: {T['metric_bg']} !important;
    color: {T['text']} !important;
}}

details > div * {{
    color: {T['text']} !important;
    background-color: transparent !important;
}}

[data-testid="stButton"] button {{
    background-color: {T['metric_bg']} !important;
    border: 1px solid {T['card_border']} !important;
    border-radius: 8px !important;
    color: {T['text']} !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
}}

[data-testid="stButton"] button:hover {{
    background-color: {T['accent']} !important;
    border-color: {T['accent']} !important;
    color: #fff !important;
    font-weight: 800 !important;
}}

hr {{
    border-color: {T['divider']} !important;
}}

[data-testid="stInfo"] {{
    background-color: {T['metric_bg']} !important;
    border-color: {T['accent']} !important;
    color: {T['text']} !important;
    border-radius: 10px !important;
}}

h1, h2, h3, h4 {{
    color: {T['text']} !important;
    font-family: 'Space Grotesk', sans-serif !important;
}}

p, span, div, label {{
    color: {T['text']} !important;
}}

[data-testid="stImage"] img {{
    background: transparent !important;
}}

.stTabs [data-baseweb="tab"][aria-selected="true"] p {{
    font-weight: 600 !important;
    font-size: 1.1rem !important;
}}
.stTabs [data-baseweb="tab"][aria-selected="false"] p {{
    font-weight: 400 !important;
    font-size: 1.02rem !important;
}}
.stTabs [data-baseweb="tab-highlight"] {{
    background-color: {T['accent']} !important;
}}

</style>
"""