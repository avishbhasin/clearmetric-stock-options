"""
Stock Options Calculator (ISO vs NSO) — ClearMetric
https://clearmetric.gumroad.com

Helps tech workers understand and plan their stock option exercises.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Stock Options Calculator (ISO vs NSO) — ClearMetric",
    page_icon="📊",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS (navy theme)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .main .block-container { padding-top: 2rem; max-width: 1200px; }
    .stMetric { background: #f8f9fa; border-radius: 8px; padding: 12px; border-left: 4px solid #2C3E6B; }
    h1 { color: #2C3E6B; }
    h2, h3 { color: #1B2A4A; }
    .cta-box {
        background: linear-gradient(135deg, #1B2A4A 0%, #2C3E6B 100%);
        color: white; padding: 24px; border-radius: 12px; text-align: center;
        margin: 20px 0;
    }
    .cta-box a { color: #D4E6F1; text-decoration: none; font-weight: bold; font-size: 1.1rem; }
    div[data-testid="stSidebar"] { background: #f8f9fa; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tax Constants (2026)
# ---------------------------------------------------------------------------
STANDARD_DEDUCTION = {"Single": 16_100, "Married Filing Jointly": 32_200}

BRACKETS = {
    "Single": [
        (0.10, 0), (0.12, 12_400), (0.22, 50_400), (0.24, 105_700),
        (0.32, 201_775), (0.35, 256_225), (0.37, 640_600),
    ],
    "Married Filing Jointly": [
        (0.10, 0), (0.12, 24_800), (0.22, 100_800), (0.24, 211_400),
        (0.32, 403_550), (0.35, 512_450), (0.37, 768_700),
    ],
}

# LTCG brackets: (rate, upper_bound) — 0% to 49.45K, 15% to 545.5K, 20% above (Single)
LTCG_BRACKETS = {
    "Single": [(0.0, 49_450), (0.15, 545_500), (0.20, 10_000_000)],
    "Married Filing Jointly": [(0.0, 98_900), (0.15, 613_700), (0.20, 10_000_000)],
}

# NIIT: 3.8% on investment income above $200K single / $250K MFJ
NIIT_THRESHOLD = {"Single": 200_000, "Married Filing Jointly": 250_000}

# AMT 2026: 26% up to exemption phase-out, 28% above
AMT_EXEMPTION = {"Single": 90_100, "Married Filing Jointly": 140_200}
AMT_PHASEOUT = {"Single": 500_000, "Married Filing Jointly": 1_000_000}
AMT_RATE_LOW = 0.26
AMT_RATE_HIGH = 0.28

STATE_TAX_RATES = {
    "Alabama": 0.05, "Alaska": 0, "Arizona": 0.025, "Arkansas": 0.045,
    "California": 0.093, "Colorado": 0.0455, "Connecticut": 0.065,
    "Delaware": 0.066, "District of Columbia": 0.0975, "Florida": 0,
    "Georgia": 0.055, "Hawaii": 0.09, "Idaho": 0.058, "Illinois": 0.0495,
    "Indiana": 0.0315, "Iowa": 0.044, "Kansas": 0.057, "Kentucky": 0.045,
    "Louisiana": 0.0425, "Maine": 0.075, "Maryland": 0.0575,
    "Massachusetts": 0.05, "Michigan": 0.0425, "Minnesota": 0.0985,
    "Mississippi": 0.05, "Missouri": 0.045, "Montana": 0.069,
    "Nebraska": 0.0684, "Nevada": 0, "New Hampshire": 0,
    "New Jersey": 0.1075, "New Mexico": 0.059, "New York": 0.109,
    "North Carolina": 0.0475, "North Dakota": 0.029, "Ohio": 0.0395,
    "Oklahoma": 0.0475, "Oregon": 0.099, "Pennsylvania": 0.0307,
    "Rhode Island": 0.0599, "South Carolina": 0.065, "South Dakota": 0,
    "Tennessee": 0, "Texas": 0, "Utah": 0.0485, "Vermont": 0.0875,
    "Virginia": 0.0575, "Washington": 0, "West Virginia": 0.065,
    "Wisconsin": 0.0765, "Wyoming": 0,
}


def federal_income_tax(taxable_income: float, filing_status: str) -> float:
    """Compute federal income tax using 2026 brackets."""
    if taxable_income <= 0:
        return 0.0
    brackets = BRACKETS[filing_status]
    tax = 0.0
    prev = 0
    for rate, thresh in brackets:
        if taxable_income <= thresh:
            tax += (taxable_income - prev) * rate
            break
        tax += (thresh - prev) * rate
        prev = thresh
    else:
        tax += (taxable_income - prev) * brackets[-1][0]
    return max(0, tax)


def ltcg_tax(gain: float, other_income: float, filing_status: str) -> float:
    """LTCG tax using 2026 brackets. other_income = taxable income excluding this gain."""
    if gain <= 0:
        return 0.0
    brackets = LTCG_BRACKETS[filing_status]
    tax = 0.0
    remaining = gain
    income_so_far = other_income
    for rate, thresh in brackets:
        if remaining <= 0:
            break
        space = max(0, thresh - income_so_far)
        taxable_in_bracket = min(remaining, space) if space > 0 else remaining
        if taxable_in_bracket > 0:
            tax += taxable_in_bracket * rate
            remaining -= taxable_in_bracket
            income_so_far += taxable_in_bracket
    if remaining > 0:
        tax += remaining * brackets[-1][0]
    # NIIT: 3.8% on investment income above threshold
    niit_thresh = NIIT_THRESHOLD[filing_status]
    niit_base = max(0, other_income + gain - niit_thresh)
    niit = 0.038 * min(gain, niit_base) if niit_base > 0 else 0
    return max(0, tax) + niit


def stcg_tax(gain: float, other_income: float, filing_status: str) -> float:
    """STCG taxed as ordinary income."""
    if gain <= 0:
        return 0.0
    taxable = other_income + gain
    tax_before = federal_income_tax(other_income, filing_status)
    tax_after = federal_income_tax(taxable, filing_status)
    return tax_after - tax_before


def amt_tax(amt_income: float, filing_status: str, regular_tax: float) -> float:
    """Simplified AMT calculation. amt_income includes ISO spread preference."""
    if amt_income <= 0:
        return 0.0
    exemption = AMT_EXEMPTION[filing_status]
    phaseout = AMT_PHASEOUT[filing_status]
    # Phase-out: 25% of amount over phaseout reduces exemption
    if amt_income > phaseout:
        exemption = max(0, exemption - 0.25 * (amt_income - phaseout))
    amt_base = max(0, amt_income - exemption)
    # Tentative minimum: 26% on first ~$220K, 28% above (simplified)
    amt_tentative = amt_base * AMT_RATE_LOW if amt_base < 220_000 else 220_000 * AMT_RATE_LOW + (amt_base - 220_000) * AMT_RATE_HIGH
    return max(0, amt_tentative - regular_tax)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("# 📊 Stock Options Calculator (ISO vs NSO)")
st.markdown("**Understand and plan your stock option exercises** — ISO vs NSO tax paths.")
st.markdown("---")

# ---------------------------------------------------------------------------
# Sidebar — User inputs
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## Your Options")

    st.markdown("### Grant Details")
    num_options = st.number_input(
        "Number of options",
        value=10_000,
        min_value=1,
        step=1_000,
        format="%d",
    )
    strike_price = st.number_input(
        "Strike price ($)",
        value=5.0,
        min_value=0.01,
        step=0.5,
        format="%.2f",
    )
    fmv = st.number_input(
        "Current / expected FMV ($)",
        value=25.0,
        min_value=0.01,
        step=1.0,
        format="%.2f",
        help="Fair Market Value at exercise",
    )
    option_type = st.selectbox(
        "Option type",
        ["ISO", "NSO"],
    )

    st.markdown("### Vesting")
    st.caption("4-year vesting, 1-year cliff")
    vested_pct = st.slider(
        "Current vesting %",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
        help="After 1 year: 25%, after 2 years: 50%, etc.",
    )
    vested_options = int(num_options * vested_pct / 100)

    st.markdown("### Tax Profile")
    filing_status = st.selectbox(
        "Filing status",
        ["Single", "Married Filing Jointly"],
    )
    w2_salary = st.number_input(
        "W-2 salary ($)",
        value=150_000,
        min_value=0,
        step=5_000,
        format="%d",
    )
    state = st.selectbox(
        "State",
        list(STATE_TAX_RATES.keys()),
        index=list(STATE_TAX_RATES.keys()).index("California"),
    )

    st.markdown("### Exit Assumptions")
    exit_price = st.number_input(
        "Expected exit price ($)",
        value=50.0,
        min_value=0.01,
        step=5.0,
        format="%.2f",
    )
    exit_years = st.number_input(
        "Expected exit timeline (years)",
        value=2,
        min_value=0,
        max_value=10,
        step=1,
        help="Years from today to expected sale",
    )
    amt_already = st.checkbox(
        "AMT already triggered this year?",
        value=False,
        help="If you've already exercised ISO and triggered AMT",
    )

# ---------------------------------------------------------------------------
# Calculations
# ---------------------------------------------------------------------------
spread_per_share = max(0, fmv - strike_price)
total_spread = spread_per_share * vested_options
cash_to_exercise = strike_price * vested_options
state_rate = STATE_TAX_RATES[state]
deduction = STANDARD_DEDUCTION[filing_status]

# Sale proceeds (gross)
gross_sale = exit_price * vested_options
appreciation_from_exercise = max(0, exit_price - fmv) * vested_options

# Regular taxable income (excluding options) for stacking
agi_base = w2_salary - deduction
taxable_base = max(0, agi_base)

# --- ISO path ---
# At exercise: no regular tax. AMT on spread (preference item).
# At sale: LTCG if holding period met (1 yr from exercise, 2 yr from grant).
# Assume qualifying disposition if exit_years >= 1 (simplified: we exercise "now")
holding_period_met = exit_years >= 1  # Simplified: 1 yr from exercise

iso_tax_exercise = 0.0  # No regular tax at exercise
if not amt_already and total_spread > 0:
    amt_income = taxable_base + total_spread
    regular_tax_base = federal_income_tax(taxable_base, filing_status)
    iso_amt = amt_tax(amt_income, filing_status, regular_tax_base)
    iso_tax_exercise = iso_amt
else:
    iso_amt = 0.0

# ISO at sale: LTCG on (exit - strike) if qualifying
iso_gain_at_sale = (exit_price - strike_price) * vested_options
if holding_period_met:
    iso_tax_sale = ltcg_tax(iso_gain_at_sale, taxable_base, filing_status)
    iso_tax_sale += state_rate * iso_gain_at_sale
else:
    # Disqualifying disposition: ordinary income on spread at exercise (already exercised)
    # + STCG on appreciation. Simplified: treat all as ordinary
    iso_tax_sale = stcg_tax(iso_gain_at_sale, taxable_base, filing_status)
    iso_tax_sale += state_rate * iso_gain_at_sale

iso_total_tax = iso_tax_exercise + iso_tax_sale
iso_net_proceeds = gross_sale - iso_total_tax - cash_to_exercise

# --- NSO path ---
# At exercise: ordinary income on spread
nso_income_exercise = total_spread
nso_taxable_with_spread = max(0, taxable_base + nso_income_exercise)
nso_fed_exercise = federal_income_tax(nso_taxable_with_spread, filing_status) - federal_income_tax(taxable_base, filing_status)
nso_state_exercise = state_rate * nso_income_exercise
nso_tax_exercise = nso_fed_exercise + nso_state_exercise

# At sale: capital gains on (exit - FMV at exercise)
nso_gain_at_sale = appreciation_from_exercise
if holding_period_met:
    nso_tax_sale = ltcg_tax(nso_gain_at_sale, nso_taxable_with_spread, filing_status)
    nso_tax_sale += state_rate * nso_gain_at_sale
else:
    nso_tax_sale = stcg_tax(nso_gain_at_sale, nso_taxable_with_spread, filing_status)
    nso_tax_sale += state_rate * nso_gain_at_sale

nso_total_tax = nso_tax_exercise + nso_tax_sale
nso_net_proceeds = gross_sale - nso_total_tax - cash_to_exercise

# Break-even exit price: where net proceeds = 0
# gross_sale - total_tax - cash_to_exercise = 0
# For ISO: sale = P * vested, tax depends on P. Iterative.
def break_even_price(option_type_str: str) -> float:
    """Find exit price where net proceeds = 0."""
    for p in np.arange(strike_price, exit_price * 2, 0.5):
        sale = p * vested_options
        if option_type_str == "ISO":
            gain = (p - strike_price) * vested_options
            if holding_period_met:
                tax_sale = ltcg_tax(gain, taxable_base, filing_status) + state_rate * gain
            else:
                tax_sale = stcg_tax(gain, taxable_base, filing_status) + state_rate * gain
            tax_ex = iso_tax_exercise
        else:
            gain = (p - fmv) * vested_options
            tax_ex = nso_tax_exercise
            if holding_period_met:
                tax_sale = ltcg_tax(gain, taxable_base + total_spread, filing_status) + state_rate * gain
            else:
                tax_sale = stcg_tax(gain, taxable_base + total_spread, filing_status) + state_rate * gain
        net = sale - tax_ex - tax_sale - cash_to_exercise
        if net >= 0:
            return round(p, 2)
    return exit_price * 2  # Not found in range

breakeven_iso = break_even_price("ISO")
breakeven_nso = break_even_price("NSO")

# ---------------------------------------------------------------------------
# Display — Key metrics
# ---------------------------------------------------------------------------
st.markdown("## Key Results")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Net Proceeds (best path)", f"${max(iso_net_proceeds, nso_net_proceeds):,.0f}", "ISO" if iso_net_proceeds >= nso_net_proceeds else "NSO")
m2.metric("Total Tax (selected)", f"${iso_total_tax:,.0f}" if option_type == "ISO" else f"${nso_total_tax:,.0f}", option_type)
m3.metric("Cash to Exercise", f"${cash_to_exercise:,.0f}", f"{vested_options:,} options")
m4.metric("Break-even Exit Price", f"${breakeven_iso:.2f}" if option_type == "ISO" else f"${breakeven_nso:.2f}", option_type)

st.markdown("---")

# ---------------------------------------------------------------------------
# ISO vs NSO comparison chart
# ---------------------------------------------------------------------------
st.markdown("## ISO vs NSO Comparison")

fig_compare = go.Figure(data=[
    go.Bar(name="ISO Net Proceeds", x=["ISO"], y=[iso_net_proceeds], marker_color="#2C3E6B"),
    go.Bar(name="NSO Net Proceeds", x=["NSO"], y=[nso_net_proceeds], marker_color="#1B2A4A"),
])
fig_compare.update_layout(
    barmode="group",
    height=350,
    showlegend=True,
    legend=dict(orientation="h", y=1.02),
    margin=dict(t=40, b=40),
    template="plotly_white",
    yaxis_title="Net Proceeds ($)",
)
st.plotly_chart(fig_compare, use_container_width=True)

# Tax breakdown table
st.markdown("### Tax Breakdown")
breakdown_data = {
    "Component": [
        "Tax at Exercise",
        "Tax at Sale",
        "Total Tax",
        "Cash to Exercise",
        "Gross Sale Proceeds",
        "**Net Proceeds**",
    ],
    "ISO": [
        f"${iso_tax_exercise:,.0f}",
        f"${iso_tax_sale:,.0f}",
        f"${iso_total_tax:,.0f}",
        f"${cash_to_exercise:,.0f}",
        f"${gross_sale:,.0f}",
        f"**${iso_net_proceeds:,.0f}**",
    ],
    "NSO": [
        f"${nso_tax_exercise:,.0f}",
        f"${nso_tax_sale:,.0f}",
        f"${nso_total_tax:,.0f}",
        f"${cash_to_exercise:,.0f}",
        f"${gross_sale:,.0f}",
        f"**${nso_net_proceeds:,.0f}**",
    ],
}
st.dataframe(pd.DataFrame(breakdown_data), use_container_width=True, hide_index=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Waterfall chart
# ---------------------------------------------------------------------------
st.markdown("## Cash Flow Waterfall")

path_label = "ISO" if option_type == "ISO" else "NSO"
tax_ex = iso_tax_exercise if option_type == "ISO" else nso_tax_exercise
tax_sale = iso_tax_sale if option_type == "ISO" else nso_tax_sale
net = iso_net_proceeds if option_type == "ISO" else nso_net_proceeds

fig_waterfall = go.Figure(go.Waterfall(
    name=path_label,
    orientation="v",
    measure=["absolute", "relative", "relative", "relative", "total"],
    x=["Gross Sale", "Exercise Cost", "Tax at Exercise", "Tax at Sale", "Net Proceeds"],
    y=[gross_sale, -cash_to_exercise, -tax_ex, -tax_sale, net],
    connector={"line": {"color": "rgb(63, 63, 63)"}},
    increasing={"marker": {"color": "#27ae60"}},
    decreasing={"marker": {"color": "#e74c3c"}},
    totals={"marker": {"color": "#2C3E6B"}},
))
fig_waterfall.update_layout(
    title=f"{path_label} Path: Sale → Costs → Net",
    showlegend=False,
    height=400,
    template="plotly_white",
    xaxis_title="",
    yaxis_title="Amount ($)",
)
st.plotly_chart(fig_waterfall, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Timeline visualization
# ---------------------------------------------------------------------------
st.markdown("## Exercise & Sale Timeline")

events = ["Grant", "Vest 25%", "Vest 50%", "Vest 75%", "Vest 100%", "Exercise (now)", f"Sale ({exit_years}yr)"]
years = [0, 1, 2, 3, 4, 0, exit_years]
fig_timeline = go.Figure()
fig_timeline.add_trace(go.Scatter(
    x=years,
    y=[1] * len(years),
    mode="markers+text",
    marker=dict(size=14, color="#2C3E6B", symbol="diamond"),
    text=events,
    textposition="top center",
    textfont=dict(size=10),
))
fig_timeline.add_hline(y=1, line_dash="dot", line_color="#1B2A4A", opacity=0.5)
fig_timeline.update_layout(
    title="Vesting & Exit Timeline",
    xaxis_title="Years from grant",
    yaxis=dict(showticklabels=False, range=[0.5, 1.8]),
    height=220,
    template="plotly_white",
    showlegend=False,
)
st.plotly_chart(fig_timeline, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Holding period guide
# ---------------------------------------------------------------------------
st.markdown("## Holding Period Guide")

st.info("""
**ISO qualifying disposition:** Hold at least **1 year from exercise** AND **2 years from grant** to get long-term capital gains treatment.  
**NSO:** Hold at least **1 year from exercise** for LTCG on appreciation (spread is always ordinary income at exercise).

With your exit in **{} year(s)**, you {} qualify for LTCG treatment.
""".format(exit_years, "**do**" if holding_period_met else "**do not**"))

st.markdown("---")

# ---------------------------------------------------------------------------
# 83(b) election (if applicable)
# ---------------------------------------------------------------------------
st.markdown("## 83(b) Election")

st.markdown("""
**83(b) election** applies when you receive **restricted stock** (not options) and elect to be taxed at grant rather than vesting.  
For **stock options**, 83(b) does not apply — you're taxed at exercise (NSO) or at sale (ISO, with AMT at exercise).

If you have **early-exercise ISO** with a vesting schedule, some companies allow 83(b) at exercise to start the holding period early. Consult your tax advisor.
""")

st.markdown("---")

# ---------------------------------------------------------------------------
# CTA — Excel
# ---------------------------------------------------------------------------
st.markdown("""
<div class="cta-box">
    <h3 style="color: white; margin: 0 0 8px 0;">Get the Full Excel Calculator</h3>
    <p style="margin: 0 0 16px 0;">
        <strong>ClearMetric Stock Options Calculator</strong> — $16.99<br>
        ✓ ISO vs NSO comparison with your numbers<br>
        ✓ Exercise scenarios at different prices/times<br>
        ✓ Holding period & AMT basics explained<br>
        ✓ All inputs editable, formulas included
    </p>
    <a href="https://clearmetric.gumroad.com/l/stock-options" target="_blank">
        Get It on Gumroad — $16.99 →
    </a>
</div>
""", unsafe_allow_html=True)

# Cross-sell
st.markdown("### More from ClearMetric")
cx1, cx2, cx3 = st.columns(3)
with cx1:
    st.markdown("""
    **🔥 FIRE Calculator** — Plan early retirement
    [Get it →](https://clearmetric.gumroad.com/l/fire-calculator)
    """)
with cx2:
    st.markdown("""
    **📈 Stock Portfolio Tracker** — $17.99
    Track dividends, performance, rebalancing.
    [Get it →](https://clearmetric.gumroad.com/l/stock-portfolio-tracker)
    """)
with cx3:
    st.markdown("""
    **🏢 LLC vs S-Corp Calculator** — $16.99
    Compare taxation, find your break-even.
    [Get it →](https://clearmetric.gumroad.com/l/llc-vs-scorp)
    """)

# Footer
st.markdown("---")
st.caption(
    "© 2026 ClearMetric | [clearmetric.gumroad.com](https://clearmetric.gumroad.com) | "
    "This tool is for educational purposes only. Not financial or tax advice. Consult a CPA."
)
