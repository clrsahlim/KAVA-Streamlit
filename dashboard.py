import re
import ast
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st
from collections import Counter

from themes import THEMES
from styles import load_css

st.set_page_config(
    page_title="KAVA - Resume Analytics Dashboard",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container {
        max-width: 900px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Relevance logic 

CATEGORY_KEYWORDS = {
    'ACCOUNTANT':                ['accounting', 'accountancy', 'finance', 'audit', 'tax', 'cpa', 'commerce', 'economics', 'financial'],
    'ADVOCATE':                  ['law', 'legal', 'juris', 'llb', 'llm', 'attorney', 'barrister', 'jurisprudence', 'j.d.'],
    'AGRICULTURE':               ['agriculture', 'agronomy', 'farming', 'botany', 'horticulture', 'soil', 'crop', 'plant science', 'agricultural science'],
    'APPAREL':                   ['fashion', 'textile', 'apparel', 'clothing', 'garment', 'costume', 'fashion design'],
    'ARCHITECTURE':              ['architecture', 'urban planning', 'urban design', 'structural design', 'interior design'],
    'ARTS':                      ['fine arts', 'visual arts', 'painting', 'sculpture', 'music', 'drama', 'creative arts', 'performing arts'],
    'AUTOMOBILE':                ['automotive', 'mechanical engineering', 'automobile', 'vehicle engineering', 'motor', 'automotive engineering'],
    'AVIATION':                  ['aviation', 'aeronautics', 'aerospace', 'pilot', 'flight', 'aircraft', 'aeronautical'],
    'BANKING':                   ['banking', 'finance', 'economics', 'commerce', 'accounting', 'financial management', 'investment'],
    'BLOCKCHAIN':                ['blockchain', 'computer science', 'software engineering', 'cryptography', 'information technology', 'distributed systems'],
    'BPO':                       ['business', 'communication', 'management', 'information technology', 'commerce', 'customer service'],
    'BUILDING AND CONSTRUCTION': ['civil engineering', 'construction management', 'architecture', 'structural engineering', 'building technology'],
    'BUSINESS ANALYST':          ['business', 'management', 'analytics', 'information systems', 'economics', 'mba', 'business analysis'],
    'CIVIL ENGINEER':            ['civil engineering', 'structural engineering', 'geotechnical', 'construction engineering', 'environmental engineering'],
    'CONSULTANT':                ['business', 'management', 'mba', 'economics', 'consulting', 'strategy', 'business administration'],
    'DATA SCIENCE':              ['data science', 'statistics', 'machine learning', 'computer science', 'mathematics', 'analytics', 'data analytics', 'artificial intelligence'],
    'DATABASE':                  ['computer science', 'information technology', 'database', 'software engineering', 'data management'],
    'DESIGNER':                  ['graphic design', 'visual design', 'ux', 'ui', 'multimedia', 'web design', 'industrial design', 'product design', 'fine arts'],
    'DEVOPS':                    ['computer science', 'information technology', 'software engineering', 'systems engineering', 'network engineering'],
    'DIGITAL MEDIA':             ['media', 'communication', 'journalism', 'digital media', 'marketing', 'graphic design', 'broadcasting'],
    'DOTNET DEVELOPER':          ['computer science', 'software engineering', 'information technology', 'programming', 'engineering'],
    'EDUCATION':                 ['education', 'teaching', 'pedagogy', 'curriculum', 'instructional design', 'educational psychology'],
    'ELECTRICAL ENGINEERING':    ['electrical engineering', 'electronics engineering', 'power systems', 'circuit design', 'instrumentation'],
    'ENGINEERING':               ['engineering', 'mechanical engineering', 'electrical engineering', 'civil engineering', 'chemical engineering', 'industrial engineering'],
    'ETL DEVELOPER':             ['computer science', 'information technology', 'software engineering', 'data engineering', 'database engineering'],
    'FINANCE':                   ['finance', 'accounting', 'economics', 'commerce', 'financial management', 'banking', 'investment', 'cfa'],
    'FOOD AND BEVERAGES':        ['food science', 'nutrition', 'culinary arts', 'hospitality', 'dietetics', 'food technology', 'food and beverage'],
    'HEALTH AND FITNESS':        ['physical education', 'kinesiology', 'sports science', 'nutrition', 'exercise science', 'health science', 'fitness', 'sports medicine'],
    'HUMAN RESOURCES':           ['human resources', 'hr management', 'management', 'psychology', 'organizational psychology', 'industrial psychology', 'business'],
    'INFORMATION TECHNOLOGY':    ['computer science', 'information technology', 'software engineering', 'network engineering', 'it management'],
    'JAVA DEVELOPER':            ['computer science', 'software engineering', 'information technology', 'programming', 'engineering'],
    'MANAGEMENT':                ['business administration', 'management', 'mba', 'economics', 'commerce', 'operations management'],
    'MECHANICAL ENGINEER':       ['mechanical engineering', 'manufacturing engineering', 'industrial engineering', 'automotive engineering', 'aerospace engineering'],
    'NETWORK SECURITY ENGINEER': ['computer science', 'information technology', 'network engineering', 'cybersecurity', 'information security'],
    'OPERATIONS MANAGER':        ['business administration', 'management', 'operations management', 'mba', 'industrial engineering', 'supply chain'],
    'PMO':                       ['business', 'management', 'project management', 'mba', 'pmp', 'operations management'],
    'PUBLIC RELATIONS':          ['communication', 'public relations', 'journalism', 'media studies', 'marketing', 'mass communication'],
    'PYTHON DEVELOPER':          ['computer science', 'software engineering', 'information technology', 'programming', 'data science'],
    'REACT DEVELOPER':           ['computer science', 'software engineering', 'information technology', 'programming', 'web development'],
    'SAP DEVELOPER':             ['computer science', 'software engineering', 'information technology', 'programming', 'engineering'],
    'SALES':                     ['sales', 'marketing', 'business', 'commerce', 'management', 'economics', 'business administration'],
    'SQL DEVELOPER':             ['computer science', 'software engineering', 'information technology', 'database', 'data management'],
    'TESTING':                   ['computer science', 'software engineering', 'information technology', 'quality assurance', 'software testing'],
    'WEB DESIGNING':             ['computer science', 'software engineering', 'information technology', 'graphic design', 'multimedia', 'web development'],
}

def check_relevance(edu_text, category):
    if pd.isna(edu_text) or str(edu_text).strip().lower() in [
        '', 'n/a', 'none', 'null', '-', 'not specified',
        'not found', 'not found in the cv.', 'not found.',
        'no education background found', 'no education information found'
    ]:
        return 'Career Switcher'
    edu_lower = str(edu_text).lower()
    keywords = CATEGORY_KEYWORDS.get(category, [])
    matches = sum(1 for kw in keywords if kw in edu_lower)
    if matches >= 2:   return 'Relevant'
    elif matches == 1: return 'Partially Relevant'
    else:              return 'Career Switcher'

# Education field 

EDU_FIELD_PATTERNS = [
    ('Data Science / AI',        r'data science|machine learning|artificial intelligence|deep learning|data mining'),
    ('Computer Science',         r'computer science|computer engineering|computing|software engineering|bscs|b\.s\.c\.s'),
    ('Information Technology',   r'information technology|information systems|information & communication|ict\b'),
    ('Electrical Engineering',   r'electrical engineering|electronics engineering|eee\b|bsee\b'),
    ('Mechanical Engineering',   r'mechanical engineering|bsme\b|meng.*mechanical|mechanical.*meng'),
    ('Civil Engineering',        r'civil engineering|structural engineering'),
    ('Chemical Engineering',     r'chemical engineering|chemistry.*engineering'),
    ('Telecom Engineering',      r'telecommunication|electronics.*communication|communication.*engineering'),
    ('Engineering (General)',    r'\bengineering\b'),
    ('Accounting / Finance',     r'accounting|accountancy|finance\b|financial\b|cpa\b|taxation'),
    ('Business Administration',  r'business administration|bba\b|bsba\b|mba\b|business management'),
    ('Economics / Commerce',     r'economics\b|commerce\b|economic studies'),
    ('Marketing',                r'marketing\b|marketing communications|digital marketing'),
    ('Management',               r'\bmanagement\b'),
    ('Law / Legal',              r'\blaw\b|legal studies|juris|llb\b|llm\b|j\.d\.|attorney'),
    ('Psychology',               r'psychology\b|counseling\b|counselling\b'),
    ('Public Health / Medicine', r'public health|medicine\b|medical\b|nursing\b|pharmacy\b|clinical'),
    ('Biology / Life Science',   r'biology\b|life science|biochemistry|microbiology'),
    ('Communication / PR',       r'communication\b|public relations\b|journalism\b|mass communication'),
    ('Media / Film',             r'\bmedia\b|film\b|radio|television|broadcasting'),
    ('Design / Visual Arts',     r'graphic design|visual design|ux\b|ui\b|multimedia\b|web design'),
    ('Fine Arts',                r'fine arts|visual arts|painting|sculpture|music\b|drama\b'),
    ('Education / Teaching',     r'education\b(?!.*computer|.*business|.*engineering)|teaching\b|pedagogy\b|curriculum'),
    ('Mathematics / Statistics', r'mathematics\b|statistics\b|math\b|quantitative'),
    ('Physics',                  r'physics\b|applied physics'),
    ('Chemistry',                r'chemistry\b(?!.*engineering)'),
    ('Architecture',             r'architecture\b|urban planning'),
    ('Agriculture',              r'agriculture\b|agronomy\b|horticulture\b|botany\b'),
    ('Culinary / Hospitality',   r'culinary\b|hospitality\b|hotel management|food science|gastronomy'),
    ('Fashion / Textile',        r'fashion\b|textile\b|apparel\b|clothing\b|garment'),
    ('Aviation / Aerospace',     r'aviation\b|aeronautics\b|aerospace\b|pilot\b'),
    ('Human Resources',          r'human resources\b|industrial relations\b|organizational behavior'),
    ('Environmental Science',    r'environmental\b|ecology\b|geology\b|earth science'),
    ('Liberal Arts / General',   r'liberal arts|general studies|social science|sociology|philosophy|history\b|political science'),
]

JUNK_PATTERNS = r'not found|no education|not specified|high school diploma|high school\b|senior high|secondary school|^\s*$|^\d{4}|^[a-z]{1,4}$'

def extract_edu_background(edu_text):
    edu_str = str(edu_text)
    if re.search(JUNK_PATTERNS, edu_str.lower()):
        return 'Unidentified'
    edu_lower = edu_str.lower()
    for label, pattern in EDU_FIELD_PATTERNS:
        if re.search(pattern, edu_lower):
            return label
    return 'Other'

# Parse skills 

def parse_skills(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return []
    try:
        parsed = ast.literal_eval(x)
        if not isinstance(parsed, list):
            return []
        return [i.strip().lower() for i in parsed if str(i).strip()]
    except:
        return [i.strip().lower() for i in str(x).split(',') if str(i).strip()]

# Certification helpers 

def has_cert(x):
    return isinstance(x, str) and x.strip() not in ['', 'None', 'none', '[]']

def count_certs(x):
    if not isinstance(x, str) or x.strip() in ['', 'None', 'none']:
        return 0
    try:
        parsed = ast.literal_eval(x)
        if isinstance(parsed, list):
            valid = [i for i in parsed if isinstance(i, str) and i.strip()]
            return len(valid)
    except (ValueError, SyntaxError):
        pass
    items = [i.strip() for i in x.split(',') if i.strip()]
    return len(items) if items else 0

def extract_certification(text):
    if pd.isna(text) or (isinstance(text, str) and text.strip() in [
        '', '[]', "['certification']", "['certificate']",
        "['certificate of completion']", "['and certification']",
        "['of completion and compliance certification']", 'not found', ','
    ]):
        return 'No Certification'

    text_lower = text.lower()

    def has(keywords):
        return any(k in text_lower for k in keywords)

    def has_word(word):
        return bool(re.search(rf'\b{re.escape(word)}\b', text_lower))

    if has(['cpa', 'certified public accountant']):         return 'CPA'
    elif has(['six sigma', 'lean six sigma']):              return 'Six Sigma'
    elif has(['pmp', 'project management professional']):   return 'PMP'
    elif has(['aws', 'amazon web services']):               return 'AWS'
    elif has(['azure']):                                    return 'Azure'
    elif has(['phr', 'sphr', 'shrm']):                     return 'HR Certification'
    elif has(['cma', 'certified management accountant']):   return 'CMA'
    elif has(['gcp', 'google cloud']):                      return 'GCP'
    elif has(['eit', 'engineer in training', 'professional engineer']) or has_word('pe'):
        return 'Engineering License'
    elif has(['teaching cert', 'teacher cert', 'teaching license',
              'certified teacher', 'early childhood education']):
        return 'Teaching Certification'
    elif has(['cpr', 'first aid', 'bls', 'acls']):         return 'CPR/First Aid'
    elif has(['driving license', "driver's license", 'cdl']): return 'Driving License'
    elif has(['acca', 'cfa', 'aca', 'cima', 'series 6', 'series 63', 'series 7']):
        return 'Finance/Accounting'
    elif has(['cissp', 'cisa', 'ceh', 'security clearance', 'top secret', 'trusecure']):
        return 'Cybersecurity'
    elif has(['scrum', 'agile', 'csm']):                   return 'Agile/Scrum'
    elif has(['oracle', 'oca', 'ocp']):                    return 'Oracle Certification'
    elif has(['microsoft certified', 'mcsa', 'mcse', 'mcp']): return 'Microsoft Certification'
    elif has(['salesforce']):                               return 'Salesforce Certification'
    elif has(['cisco', 'ccna', 'ccnp', 'ccie']):           return 'Cisco/Network Certification'
    elif has(['google certified', 'google data', 'google professional']):
        return 'Google Certification'
    elif has(['adobe certified', 'ciw', 'awwwards']):      return 'Design/Web Certification'
    elif has(['osha', 'safety']):                          return 'OSHA/Safety Certification'
    elif has(['nursing assistant', 'certified nurse', 'cnpr', 'pharma',
              'medical', 'health coach', 'fitness instructor',
              'personal trainer', 'group fitness']) or has_word('cna'):
        return 'Healthcare/Fitness Certification'
    elif has(['architect', 'aia', 'ncbdc', 'leed', 'ncidq', 'building designer']):
        return 'Architecture/Construction Certification'
    elif has(['ase', 'mechanic', 'automotive', 'forklift', 'technician']):
        return 'Automotive/Technical Certification'
    elif has(['faa', 'atp', 'aviation', 'pilot']):         return 'Aviation Certification'
    elif has(['mulesoft', 'jenkins', 'python programming', 'selenium', 'ctfl', 'astqb']):
        return 'Software/Dev Certification'
    elif has(['realtor', 'real estate']):                   return 'Real Estate Certification'
    elif has(['iso', 'apm', 'management consultant', 'business analysis', 'planning engineer']):
        return 'Management/Business Certification'
    elif has(['welding', 'master builder']):                return 'Trades Certification'
    elif has(['certificate', 'certification', 'certified', 'license', 'licence']):
        return 'Other Certification'
    else:
        return 'Other Certification'

# Truncate cert label 

def truncate_cert_label(label: str, max_words: int = 6) -> str:
    words = label.split()
    if len(words) <= max_words:
        return label
    return ' '.join(words[:max_words]) + '...'

# Blues gradient helper 

def make_blues_cmap(light='#c8dff7', dark='#1a3a5c'):
    return mcolors.LinearSegmentedColormap.from_list("blues_custom", [light, dark])

def blues_colors(values, light='#c8dff7', dark='#1a3a5c'):
    """Return list of hex colors scaled from light→dark based on values."""
    cmap = make_blues_cmap(light, dark)
    norm = plt.Normalize(min(values), max(values))
    return [mcolors.to_hex(cmap(norm(v))) for v in values]

# Session state 

if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Light Mode"

# Load data 

JUNK_VALUES = [
    '', 'n/a', 'none', 'null', '-', 'not specified',
    'not found', 'not found in the cv.', 'not found.',
    'no education background found', 'no education information found'
]

@st.cache_data
def load_data():
    df = pd.read_csv("resume_features.csv")
    df['education'] = df['education'].apply(
        lambda x: np.nan if (x is None or str(x).strip().lower() in JUNK_VALUES) else x
    )
    df['cert_count'] = df['certifications'].apply(count_certs)
    df['certification_category'] = df['certifications'].apply(extract_certification)
    return df

resume_data = load_data()
ALL_CATEGORIES = sorted(resume_data['category'].unique().tolist())

# Sidebar 

with st.sidebar:
    st.markdown("### Display Settings")

    def toggle_theme():
        st.session_state.theme_name = "Dark Mode" if st.session_state.dark_toggle else "Light Mode"

    st.toggle(
        "Dark Mode",
        value=st.session_state.theme_name == "Dark Mode",
        key="dark_toggle",
        on_change=toggle_theme,
    )

    st.markdown("---")
    st.markdown("### Category Filter")

    col_sa, col_da = st.columns(2)
    if col_sa.button("Select All", use_container_width=True):
        for cat in ALL_CATEGORIES:
            st.session_state[f"cat_{cat}"] = True
    if col_da.button("Clear All", use_container_width=True):
        for cat in ALL_CATEGORIES:
            st.session_state[f"cat_{cat}"] = False

    st.markdown("")

    selected_categories = []
    for cat in ALL_CATEGORIES:
        key = f"cat_{cat}"
        if key not in st.session_state:
            st.session_state[key] = False
        val = st.checkbox(cat, key=key)
        if val:
            selected_categories.append(cat)

    st.markdown("---")
    st.caption(f"{len(selected_categories)} / {len(ALL_CATEGORIES)} categories selected")

# Theme 

T = THEMES[st.session_state.theme_name]

BLUES_LIGHT = T['blues_light']
BLUES_DARK  = T['blues_dark']

st.markdown(load_css(T), unsafe_allow_html=True)

# No selection state 

if not selected_categories:
    st.markdown(f"""
    <div style="
        background: {T['card_bg']};
        border: 1px solid {T['card_border']};
        border-left: 5px solid {T['accent']};
        border-radius: 14px;
        padding: 2rem 2.5rem;
        margin-top: 2rem;
        text-align: center;
    ">
        <div style="font-size:2.5rem;margin-bottom:0.75rem;"></div>
        <h3 style="color:{T['text']};margin:0 0 0.5rem 0;font-family:'Space Grotesk',sans-serif;">
            No category selected
        </h3>
        <p style="color:{T['subtext']};margin:0;">
            Please select at least one category from the sidebar, or click <strong>Select All</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

main_df = resume_data[resume_data['category'].isin(selected_categories)].copy()
main_df['relevance'] = main_df.apply(
    lambda r: check_relevance(r['education'], r['category']), axis=1
)
main_df['skills_parsed'] = main_df['skills_list'].apply(parse_skills)

# Header 

st.markdown(f"""
<div class="dashboard-header" style="
    background: linear-gradient(180deg, {T['accent2']} 0%, {T['accent3']} 100%);
    border-radius: 16px 16px 0 0;
    padding: 1.5rem 2.5rem 0.7rem 2.5rem;
">
    <h3 style="color:#fff !important;font-family:'Space Grotesk',sans-serif !important;font-size:1rem !important;font-weight:500 !important;margin:0 !important;line-height:1 !important;">KAVA - Resume Analytics Dashboard</h3>
    <p style="color:rgba(255,255,255,0.82) !important;margin:0 !important;padding-top:0 !important;font-size:1rem !important;">Exploring candidate profiles across education, skills &amp; certifications</p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="
    background: {T['accent3']};
    border-radius: 0 0 16px 16px;
    padding: 0rem 2.5rem 1.2rem 2.5rem;
    margin-bottom: 1.15rem;
">
    <div style="border-top:2px solid rgba(255,255,255,0.6) ;margin-bottom:1.25rem;"></div>
    <div style="display:flex;gap:0.9rem;">
        <div style="flex:1;text-align:center;border-right:1.5px solid rgba(255,255,255,0.6);padding-right:1rem;">
            <div style="color:rgba(255,255,255,0.75);font-size:0.9rem;font-weight:600;text-transform:uppercase;margin-bottom:0;">Total Candidates</div>
            <div style="color:#fff;font-family:'Space Grotesk',sans-serif;font-size:1.3rem;font-weight:700;">{len(main_df):,}</div>
        </div>
        <div style="flex:1;text-align:center;">
            <div style="color:rgba(255,255,255,0.75);font-size:0.9rem;font-weight:600;text-transform:uppercase;margin-bottom:0;">Total Categories Selected</div>
            <div style="color:#fff;font-family:'Space Grotesk',sans-serif;font-size:1.3rem;font-weight:700;">{len(selected_categories):,}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Metric card helper 

edu_filled = main_df['education'].notna().sum()
avg_exp    = main_df['experience_years'].mean() if 'experience_years' in main_df.columns else 0
edu_pct    = (edu_filled / len(main_df) * 100) if len(main_df) > 0 else 0

def metric_card(col, label, value):
    col.markdown(f"""
    <div style="
        background-color: {T['metric_bg']};
        border: 1px solid {T['card_border']};
        border-left: 4px solid {T['accent']};
        border-radius: 12px;
        padding: 0.8rem 1rem;
        text-align: center;
    ">
        <div style="color:{T['subtext']};font-size:0.75rem;font-weight:600;
                    letter-spacing:0.05em;text-transform:uppercase;margin-bottom:0.2rem;">{label}</div>
        <div style="color:{T['text']};font-family:'Space Grotesk',sans-serif;
                    font-size:1.2rem;font-weight:700;line-height:1;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1: EDUCATION RELEVANCE
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"""
<div style="background:{T['card_bg']};border:1px solid {T['card_border']};
    border-radius:16px;padding:0.8rem 1rem 1rem 1.5rem;margin-bottom:1.5rem;">
    <div style="color:{T['text']};font-family:'Space Grotesk',sans-serif;font-weight:600;
        font-size:1.5rem;letter-spacing:-0.01em;margin:0;">Education Relevance by Job Category</div>
    <div style="color:{T['subtext']};font-size:1rem;margin:0;">
        Distribution of education background relevance among candidates</div>
""", unsafe_allow_html=True)

col2, col3, col4 = st.columns(3)
metric_card(col2, "Education Filled", f"{edu_filled:,}")
metric_card(col3, "Avg. Experience", f"{avg_exp:.1f} yrs")
metric_card(col4, "Education Fill Rate", f"{edu_pct:.1f}%")
st.markdown("<br>", unsafe_allow_html=True)

# Donut Chart 

edu_df = main_df.dropna(subset=['education']).copy()

rel_counts = edu_df['relevance'].value_counts().reindex(
    ['Relevant', 'Partially Relevant', 'Career Switcher'], fill_value=0
)
rel_pct = rel_counts / rel_counts.sum() * 100 if rel_counts.sum() > 0 else rel_counts * 0


donut_colors = T['donut_colors']
labels = rel_counts.index.tolist()
sizes  = rel_counts.values

fig, ax = plt.subplots(figsize=(4, 4), facecolor='none')
ax.set_facecolor('none')

if sizes.sum() > 0:
    wedges, _ = ax.pie(
        sizes,
        colors=donut_colors,
        startangle=90,
        wedgeprops=dict(width=0.45, linewidth=2)
    )
    ax.text(0, 0, f'{len(edu_df):,}\nCandidates',
            ha='center', va='center', fontsize=11, fontweight='bold', color=T['fig_text'])
    legend_labels = [f'{l}  –  {rel_pct.values[i]:.1f}%  ({sizes[i]:,})' for i, l in enumerate(labels)]
    ax.legend(wedges, legend_labels, loc='lower center', bbox_to_anchor=(0.5, -0.15),
              fontsize=8, frameon=False, labelcolor=T['fig_text'])
    ax.set_title('Education Relevance Distribution', fontsize=11, fontweight='bold',
                 pad=9, color=T['fig_text'])

plt.tight_layout()
col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    st.pyplot(fig, use_container_width=False, transparent=True)
plt.close(fig)

## Top 5 Career Switcher 

st.markdown(f"""
<h4 style="color:{T['text']} !important;font-family:'Space Grotesk',sans-serif !important;
    font-weight:600 !important;margin:1.25rem 0 0.25rem 0 !important;font-size:1rem !important;">
    Top 5 Categories with Most Career Switchers</h4>
<p style="color:{T['subtext']} !important;font-size:1rem !important;margin:0 0 1rem 0 !important;">
    Click a category to view the most common education backgrounds</p>
""", unsafe_allow_html=True)

switcher_count = edu_df[edu_df['relevance'] == 'Career Switcher'].groupby('category').size()
total_per_cat  = edu_df.groupby('category').size()
top5 = (
    (switcher_count / total_per_cat * 100)
    .round(1).sort_values(ascending=False).head(5).reset_index()
)
top5.columns = ['Category', 'Switcher %']
top5['Career Switcher Count'] = top5['Category'].map(switcher_count).fillna(0).astype(int)
top5['% of Category'] = top5['Switcher %'].astype(str) + '%'

cs_df = edu_df[edu_df['relevance'] == 'Career Switcher'].copy()
cs_df['edu_bg'] = cs_df['education'].apply(extract_edu_background)

medals = ['1.', '2.', '3.', '4.', '5.']

for i, row in top5.iterrows():
    cat   = row['Category']
    label = (f"{medals[i]} **{cat}** — {row['% of Category']} of candidates are career switchers "
            f"({row['Career Switcher Count']:,} people)")
    with st.expander(label):
        cat_cs  = cs_df[cs_df['category'] == cat]
        top_edu = (
            cat_cs[~cat_cs['edu_bg'].isin(['Unidentified', 'Other'])]['edu_bg']
            .value_counts().head(3).reset_index()
        )
        top_edu.columns = ['Education Background', 'Count']
        total_cs = len(cat_cs)
        sub_medals = ['1.', '2.', '3.']
        for j, edu_row in top_edu.iterrows():
            pct = edu_row['Count'] / total_cs * 100
            bar_width = int(pct * 2)
            st.markdown(
                f"{sub_medals[j]} **{edu_row['Education Background']}** "
                f"— {edu_row['Count']} people ({pct:.1f}%)"
            )
            st.markdown(f"""
            <div style="height:6px;width:{bar_width}%;
                background:linear-gradient(90deg,{T['accent3']} 0%,{T['accent3']} 100%);
                border-radius:3px;margin:-8px 0 8px 0;opacity:0.85;"></div>
            """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2: SKILL DISTRIBUTION
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"""
<div style="background:{T['card_bg']};border:1px solid {T['card_border']};
    border-radius:16px;padding:0.8rem 1rem 1rem 1.5rem;margin-bottom:1.5rem;">
    <div style="color:{T['text']};font-family:'Space Grotesk',sans-serif;font-weight:600;
        font-size:1.5rem;letter-spacing:-0.01em;margin:0;">Skill Distribution</div>
    <div style="color:{T['subtext']};font-size:1rem;margin:0;">
        Top technical skills and distributions for each job category</div>
""", unsafe_allow_html=True)

all_skills        = [s for skills in main_df['skills_parsed'] for s in skills]
skill_counts_series = pd.Series(Counter(all_skills))
top20_skills_list = skill_counts_series.nlargest(20).index.tolist()

if len(selected_categories) == len(ALL_CATEGORIES):
    cat_label = "All categories"
elif len(selected_categories) <= 5:
    cat_label = ", ".join(selected_categories)
else:
    cat_label = ", ".join(selected_categories[:5]) + f" +{len(selected_categories)-5} others"

tab1, tab2 = st.tabs(["Top 20 Skills", "Category Heatmap"])

with tab1:
    top20_counts = skill_counts_series[top20_skills_list].sort_values()
    bar_colors   = blues_colors(top20_counts.values, BLUES_LIGHT, BLUES_DARK)

    fig, ax = plt.subplots(figsize=(4, 3.3), facecolor='none')
    ax.set_facecolor('none')

    bars = ax.barh(
        [s.title() for s in top20_counts.index],
        top20_counts.values,
        color=bar_colors,
        edgecolor='none',
        height=0.6
    )

    max_val = top20_counts.max()
    for bar in bars:
        val = bar.get_width()
        ax.text(val + max_val * 0.01, bar.get_y() + bar.get_height() / 2,
                f'{int(val):,}', va='center', fontsize=4.7, color=T['fig_text'])

    ax.set_title('Top 20 Common Skills', fontsize=7, fontweight='bold', color=T['fig_text'], pad=13)
    ax.text(0.5, 1.02, f"Category: {cat_label}", transform=ax.transAxes,
            ha='center', va='bottom', fontsize=5, color=T['fig_text'],
            alpha=0.6, style='italic', fontweight='bold')
    ax.set_xlabel('Frequency', fontsize=5, color=T['fig_text'])
    ax.tick_params(colors=T['fig_text'], labelsize=4.7)
    ax.xaxis.label.set_color(T['fig_text'])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis='x', alpha=0.2, color=T['fig_text'])
    plt.tight_layout(pad=0.3)
    st.pyplot(fig, transparent=True, use_container_width=False)
    plt.close(fig)

with tab2:
    rows = {}
    for category, group in main_df.groupby('category'):
        n = len(group)
        rows[category] = {
            skill: round(
                sum(skill in skills for skills in group['skills_parsed']) / n * 100, 1
            )
            for skill in top20_skills_list
        }

    heatmap_df = pd.DataFrame(rows).T[top20_skills_list]

    n_cats   = len(heatmap_df)
    n_skills = len(top20_skills_list)
    fig_w = max(14, n_skills * 0.75)
    fig_h = max(6,  n_cats   * 0.42)

    fig2, ax2 = plt.subplots(figsize=(fig_w, fig_h), facecolor='none')
    ax2.set_facecolor('none')

    sns.heatmap(
        heatmap_df,
        cmap='Blues',
        annot=True,
        fmt='.0f',
        linewidths=0.4,
        linecolor='white',
        annot_kws={'size': 9.5},
        ax=ax2,
        cbar_kws={'shrink': 0.6}
    )

    ax2.set_title('Skill Distribution for Each Category (%)', fontsize=15,
                  fontweight='bold', color=T['fig_text'], pad=14)
    ax2.tick_params(colors=T['fig_text'], labelsize=11)
    ax2.set_xticklabels(
        [t.get_text().title() for t in ax2.get_xticklabels()],
        rotation=40, ha='right', fontsize=11.5
    )
    ax2.set_yticklabels(ax2.get_yticklabels(), rotation=0, fontsize=9.5)

    plt.tight_layout()
    st.pyplot(fig2, transparent=True)
    plt.close(fig2)

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3: CERTIFICATION INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"""
<div style="background:{T['card_bg']};border:1px solid {T['card_border']};
    border-radius:16px;padding:0.8rem 1rem 1rem 1.5rem;margin-bottom:1.5rem;">
    <div style="color:{T['text']};font-family:'Space Grotesk',sans-serif;font-weight:600;
        font-size:1.5rem;letter-spacing:-0.01em;margin:0;">Certification Insights</div>
    <div style="color:{T['subtext']};font-size:1rem;margin:0;">
        Professional certifications held by candidates across job categories</div>
""", unsafe_allow_html=True)

cert_holders = main_df['certifications'].apply(has_cert).sum()
multi_cert   = (main_df['cert_count'] > 1).sum()
pct_cert     = cert_holders / len(main_df) * 100 if len(main_df) > 0 else 0
pct_multi    = multi_cert / cert_holders * 100 if cert_holders > 0 else 0

cm1, cm2, cm3 = st.columns(3)
metric_card(cm1, "Candidates with Certs", f"{cert_holders:,}")
metric_card(cm2, "Cert Holders Rate", f"{pct_cert:.1f}%")
metric_card(cm3, "Multiple Certs Rate", f"{pct_multi:.1f}%")
st.markdown("<br>", unsafe_allow_html=True)

tab3, tab4, tab5 = st.tabs(["Top Certifications", "Count Distribution", "By Category"])

# TAB 3: Bubble chart 
with tab3:
    cert_counts = main_df[
        (main_df['certification_category'] != 'No Certification') &
        (main_df['certification_category'] != 'Other Certification')
    ]['certification_category'].value_counts()

    top_certs = cert_counts.head(15).reset_index()
    top_certs.columns = ['cert', 'count']

    if top_certs.empty:
        st.info("No valid certifications found for the selected categories.")
    else:
        top_certs['pct']   = (top_certs['count'] / cert_holders * 100).round(1) if cert_holders > 0 else 0
        top_certs['label'] = top_certs['cert'].apply(lambda x: truncate_cert_label(x, 6))

        fig3, ax3 = plt.subplots(figsize=(13, 7), facecolor='none')
        ax3.set_facecolor('none')

        blues_cmap2 = make_blues_cmap(BLUES_LIGHT, BLUES_DARK)
        norm        = plt.Normalize(top_certs['count'].min(), top_certs['count'].max())
        rgba_colors = [blues_cmap2(norm(v)) for v in top_certs['count']]
        sizes       = (top_certs['count'] / top_certs['count'].max() * 3500) + 500

        x_pos = np.arange(len(top_certs))
        ax3.scatter(x_pos, top_certs['count'], s=sizes, c=rgba_colors,
                    linewidths=1.5, zorder=3, alpha=0.92)

        for xi, (_, row), rgba in zip(x_pos, top_certs.iterrows(), rgba_colors):
            brightness = rgba[0] * 0.299 + rgba[1] * 0.587 + rgba[2] * 0.114
            txt_color  = 'white' if brightness < 0.55 else '#1a3a5c'
            ax3.text(xi, row['count'], f"{row['count']}",
                     ha='center', va='center', fontsize=12, fontweight='bold',
                     color=txt_color, zorder=4)

        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(top_certs['label'], rotation=40, ha='right',
                             fontsize=12, color=T['fig_text'])
        ax3.tick_params(axis='y', colors=T['fig_text'], labelsize=12)
        ax3.set_ylabel('Number of Candidates', fontsize=10, color=T['fig_text'])
        ax3.set_title('Top 15 Most Common Certifications', fontsize=18,
                      fontweight='bold', color=T['fig_text'], pad=26)
        ax3.text(0.5, 1.02, f"Category: {cat_label}", transform=ax3.transAxes,
                 ha='center', va='bottom', fontsize=13, color=T['fig_text'],
                 alpha=0.6, style='italic', fontweight='bold')
        ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
        for spine in ax3.spines.values():
            spine.set_visible(False)
        ax3.grid(axis='y', alpha=0.15, color=T['fig_text'], linestyle='--')
        ax3.set_ylim(0, top_certs['count'].max() * 1.3)
        plt.tight_layout()
        st.pyplot(fig3, transparent=True, use_container_width=True)
        plt.close(fig3)

# TAB 4: Count distribution bar chart 
with tab4:
    THRESHOLD  = 20
    cert_dist  = main_df['cert_count'].value_counts().sort_index()
    cert_below = cert_dist[cert_dist.index < THRESHOLD]
    cert_above = cert_dist[cert_dist.index >= THRESHOLD].sum()
    cert_plot  = pd.concat([cert_below, pd.Series({THRESHOLD: cert_above})]) if cert_above > 0 else cert_below
    xlabels    = [str(int(i)) if i < THRESHOLD else f'≥{THRESHOLD}' for i in cert_plot.index]

    bar_colors2 = blues_colors(cert_plot.values, BLUES_LIGHT, BLUES_DARK)

    fig4, ax4 = plt.subplots(figsize=(9, 4), facecolor='none')
    ax4.set_facecolor('none')

    x_pos = np.arange(len(cert_plot))
    bars  = ax4.bar(x_pos, cert_plot.values, color=bar_colors2, edgecolor='none', width=0.6)

    for bar, val in zip(bars, cert_plot.values):
        ax4.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + cert_plot.max() * 0.01,
                 f'{val:,}', ha='center', va='bottom', fontsize=9, color=T['fig_text'])

    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(xlabels, fontsize=9, color=T['fig_text'])
    ax4.tick_params(axis='y', colors=T['fig_text'], labelsize=8)
    ax4.set_xlabel('Number of Certifications per Candidate', fontsize=8, color=T['fig_text'])
    ax4.set_ylabel('Number of Candidates', fontsize=8, color=T['fig_text'])
    ax4.set_title('Distribution of Certifications per Candidate', fontsize=12,
                  fontweight='bold', color=T['fig_text'], pad=20)
    ax4.text(0.5, 1.02, f"Category: {cat_label}", transform=ax4.transAxes,
             ha='center', va='bottom', fontsize=9, color=T['fig_text'],
             alpha=0.6, style='italic', fontweight='bold')
    ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax4.set_ylim(0, cert_plot.max() * 1.18)
    for spine in ax4.spines.values():
        spine.set_visible(False)
    ax4.grid(axis='y', alpha=0.15, color=T['fig_text'], linestyle='--')
    plt.tight_layout()
    st.pyplot(fig4, transparent=True, use_container_width=False)
    plt.close(fig4)

# TAB 5: By category dot plot 
with tab5:
    total_per_cat2 = main_df.groupby('category').size()
    cert_per_cat   = main_df[main_df['cert_count'] > 0].groupby('category').size()
    pct_by_cat     = (cert_per_cat / total_per_cat2 * 100).round(1).sort_values(ascending=True).dropna()

    dot_colors = blues_colors(pct_by_cat.values, BLUES_LIGHT, BLUES_DARK)

    fig5, ax5 = plt.subplots(figsize=(9, 10.5), facecolor='none')
    ax5.set_facecolor('none')

    y_pos = np.arange(len(pct_by_cat))
    ax5.hlines(y_pos, 0, pct_by_cat.values, color='#cccccc', linewidth=1, alpha=0.6)
    ax5.scatter(pct_by_cat.values, y_pos, color=dot_colors, s=75, zorder=5)

    med = pct_by_cat.median()
    ax5.axvline(med, color=BLUES_DARK, linewidth=1.2, linestyle='--', alpha=0.6)
    ax5.text(med + 0.3, len(pct_by_cat) - 0.5, f'Median\n{med:.1f}%',
             fontsize=8, color=BLUES_DARK, va='top')

    for xi, yi, val in zip(pct_by_cat.values, y_pos, pct_by_cat.values):
        ax5.text(xi + 1.5, yi, f'{val:.1f}%', va='center', fontsize=8, color=T['fig_text'])

    ax5.set_yticks(y_pos)
    ax5.set_yticklabels(pct_by_cat.index, fontsize=9, color=T['fig_text'])
    ax5.tick_params(axis='x', colors=T['fig_text'], labelsize=8)
    ax5.set_xlabel('% of Candidates with Certifications', fontsize=9, color=T['fig_text'])
    ax5.set_title('Certification Rate by Job Category', fontsize=12,
                  fontweight='bold', color=T['fig_text'], pad=20)
    ax5.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}%'))
    ax5.set_xlim(0, pct_by_cat.max() * 1.2)
    for spine in ax5.spines.values():
        spine.set_visible(False)
    ax5.grid(axis='x', alpha=0.12, color=T['fig_text'], linestyle='--')
    plt.tight_layout()
    st.pyplot(fig5, transparent=True, use_container_width=True)
    plt.close(fig5)

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align:center;padding:1rem;border-top:1px solid {T['divider']};margin-top:1rem;">
    <span style="color:{T['subtext']};font-size:0.8rem;">
        Copyright © KAVA · Coding Camp 2026
    </span>
</div>
""", unsafe_allow_html=True)