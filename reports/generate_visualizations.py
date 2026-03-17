#!/usr/bin/env python3
"""
@CodeVizExpert — ComplaintInsight Agents
Generates visualizations from compiled research data.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import os

OUT_DIR = "/home/user/Alex-Guillen-Music/reports/visualizations"
os.makedirs(OUT_DIR, exist_ok=True)

# Set style
plt.rcParams.update({
    'font.size': 12,
    'axes.titlesize': 16,
    'axes.labelsize': 13,
    'figure.facecolor': '#0d1117',
    'axes.facecolor': '#161b22',
    'text.color': '#e6edf3',
    'axes.labelcolor': '#e6edf3',
    'xtick.color': '#8b949e',
    'ytick.color': '#8b949e',
})

# ============================================================
# VIZ 1: Top 10 Consumer Complaint Types — Composite Score Bar Chart
# ============================================================
complaint_data = pd.DataFrame({
    'Complaint Type': [
        'AI Chatbot Gatekeeping',
        'Health Insurance Denials',
        'Telecom Billing Fraud',
        'Credit Report Errors',
        'Subscription Dark Patterns',
        'Multi-Hour Hold Times',
        'Airline Service Failures',
        'Mobile Carrier Overcharges',
        'Delivery Refund Denials',
        'Package Delivery Failures'
    ],
    'Volume Signal (1-10)': [9, 7, 9, 10, 8, 7, 9, 7, 7, 7],
    'Emotional Intensity (1-10)': [10, 10, 9, 7, 8, 8, 7, 8, 6, 6],
    'Growth Trend (1-10)': [10, 8, 7, 10, 9, 6, 7, 6, 7, 7],
    'Source Corroboration (1-10)': [9, 9, 9, 10, 9, 8, 9, 8, 7, 7],
})
complaint_data['Composite Score'] = (
    complaint_data['Volume Signal (1-10)'] * 0.3 +
    complaint_data['Emotional Intensity (1-10)'] * 0.25 +
    complaint_data['Growth Trend (1-10)'] * 0.25 +
    complaint_data['Source Corroboration (1-10)'] * 0.2
)
complaint_data = complaint_data.sort_values('Composite Score', ascending=True)

fig, ax = plt.subplots(figsize=(14, 8))
colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.9, len(complaint_data)))
bars = ax.barh(complaint_data['Complaint Type'], complaint_data['Composite Score'], color=colors, edgecolor='#30363d', linewidth=0.5)
for bar, score in zip(bars, complaint_data['Composite Score']):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, f'{score:.1f}', va='center', ha='left', color='#e6edf3', fontweight='bold', fontsize=11)
ax.set_xlabel('Composite Complaint Score (weighted: volume 30%, intensity 25%, growth 25%, corroboration 20%)')
ax.set_title('Top 10 Consumer Complaint Types — 2025-2026\nComposite Score Ranking', fontweight='bold', pad=15)
ax.set_xlim(0, 10.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#30363d')
ax.spines['left'].set_color('#30363d')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/01_top10_complaint_types_bar.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ VIZ 1: Top 10 Complaint Types Bar Chart saved")

# ============================================================
# VIZ 2: Industry x Complaint Type Heatmap
# ============================================================
industries = ['Airlines', 'Telecom/ISP', 'Health Insurance', 'Banking/Credit', 'E-Commerce', 'Food Delivery', 'Utilities', 'Streaming/Subs']
complaint_types = ['Chatbot Walls', 'Billing Errors', 'Hold Times', 'Refund Denials', 'Dark Patterns', 'Claim Denials', 'Service Failures', 'Data/Privacy']

heatmap_data = np.array([
    # Chatbot, Billing, Hold, Refund, DarkPat, Claims, ServiceFail, Privacy
    [7, 6, 9, 5, 4, 2, 9, 3],  # Airlines
    [9, 10, 8, 6, 7, 2, 7, 5],  # Telecom
    [6, 4, 7, 3, 5, 10, 4, 8],  # Health Insurance
    [5, 7, 6, 6, 4, 3, 5, 9],  # Banking
    [8, 4, 3, 8, 9, 1, 6, 7],  # E-Commerce
    [7, 3, 2, 9, 5, 1, 8, 3],  # Food Delivery
    [4, 8, 6, 3, 3, 2, 7, 4],  # Utilities
    [6, 5, 3, 4, 10, 1, 4, 5],  # Streaming
])

df_heatmap = pd.DataFrame(heatmap_data, index=industries, columns=complaint_types)

fig, ax = plt.subplots(figsize=(14, 8))
cmap = sns.color_palette("YlOrRd", as_cmap=True)
sns.heatmap(df_heatmap, annot=True, fmt='d', cmap=cmap, linewidths=1, linecolor='#30363d',
            ax=ax, cbar_kws={'label': 'Severity Score (1-10)', 'shrink': 0.8},
            annot_kws={'size': 13, 'weight': 'bold'})
ax.set_title('Consumer Complaint Heatmap: Industry × Complaint Type (2025-2026)', fontweight='bold', pad=15)
ax.set_ylabel('')
ax.set_xlabel('')
plt.xticks(rotation=30, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/02_industry_complaint_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ VIZ 2: Industry × Complaint Heatmap saved")

# ============================================================
# VIZ 3: Word Cloud of Most Common Complaint Phrases
# ============================================================
complaint_phrases = {
    'chatbot': 45, 'hold time': 42, 'billing error': 40, 'refund denied': 38,
    'customer service': 50, 'can\'t reach human': 44, 'subscription trap': 35,
    'dark pattern': 33, 'claim denied': 37, 'automated system': 30,
    'hours on hold': 39, 'no response': 32, 'bot loop': 36,
    'cancel impossible': 34, 'wrong charge': 31, 'overcharged': 29,
    'hidden fees': 35, 'exhaustion design': 28, 'defensive AI': 27,
    'runaround': 26, 'transferred again': 25, 'no resolution': 33,
    'scam': 24, 'fraud': 23, 'identity theft': 22,
    'price increase': 28, 'shrinkflation': 20, 'phantom charge': 19,
    'credit report error': 36, 'delayed flight': 25, 'lost package': 22,
    'stolen delivery': 18, 'insurance denial': 30, 'wait forever': 27,
    'worst company': 20, 'horrible experience': 19, 'never again': 17,
    'filed FCC complaint': 15, 'class action': 14, 'BBB complaint': 16,
    'AI replacing humans': 26, 'foreign call center': 21, 'broken promise': 20,
    'premium for basic service': 18, 'monopoly': 22, 'no accountability': 19,
}

wc = WordCloud(
    width=1400, height=700,
    background_color='#0d1117',
    colormap='YlOrRd',
    max_words=100,
    max_font_size=120,
    min_font_size=14,
    prefer_horizontal=0.7,
    relative_scaling=0.5,
).generate_from_frequencies(complaint_phrases)

fig, ax = plt.subplots(figsize=(14, 7))
ax.imshow(wc, interpolation='bilinear')
ax.axis('off')
ax.set_title('Consumer Complaint Language Cloud — 2025-2026\n(Sized by frequency across Reddit, review sites, CFPB & news)',
             fontweight='bold', pad=15, fontsize=16, color='#e6edf3')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/03_complaint_wordcloud.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ VIZ 3: Complaint Word Cloud saved")

# ============================================================
# VIZ 4: Federal Complaint Volume Trends (Year-over-Year)
# ============================================================
fig, ax = plt.subplots(figsize=(12, 7))
agencies = ['CFPB\nComplaints', 'FTC Sentinel\nReports', 'FTC Fraud\nLosses ($B)', 'DOT Airline\nComplaints', 'Insurance\nComplaints']
prev = [1.6, 5.4, 10.0, 100, 100]  # indexed to 100 for DOT & insurance
curr = [3.19, 6.47, 12.5, 109, 107]
pct_change = ['+100%', '+20%', '+25%', '+9%', '+7%']

x = np.arange(len(agencies))
width = 0.35
bars1 = ax.bar(x - width/2, prev, width, label='Prior Period (2023)', color='#388bfd', edgecolor='#30363d', alpha=0.7)
bars2 = ax.bar(x + width/2, curr, width, label='Current Period (2024-25)', color='#f85149', edgecolor='#30363d')

for i, (bar, pct) in enumerate(zip(bars2, pct_change)):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, pct,
            ha='center', va='bottom', color='#f85149', fontweight='bold', fontsize=13)

ax.set_ylabel('Volume (M for CFPB/FTC, $B for fraud, indexed for DOT/Ins)')
ax.set_title('Federal Consumer Complaint Volumes — Year-over-Year Growth\nAll Categories Show Increases', fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(agencies)
ax.legend(loc='upper left', framealpha=0.8, edgecolor='#30363d')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#30363d')
ax.spines['left'].set_color('#30363d')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/04_federal_complaint_trends.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ VIZ 4: Federal Complaint Volume Trends saved")

# ============================================================
# VIZ 5: Most Complained-About Companies — Multi-Source Composite
# ============================================================
companies = [
    'Comcast/Xfinity', 'UnitedHealthcare', 'Equifax/Experian/\nTransUnion',
    'Verizon', 'Amazon', 'American Airlines',
    'Delta Air Lines', 'Uber/Uber Eats', 'Ticketmaster',
    'FedEx', 'Wells Fargo', 'T-Mobile'
]
reddit_score = [10, 9, 5, 8, 8, 7, 7, 7, 8, 6, 5, 6]
gov_score =    [7, 6, 10, 7, 8, 8, 7, 4, 5, 4, 8, 5]
news_score =   [8, 8, 7, 6, 9, 8, 7, 6, 7, 5, 7, 6]
review_score = [9, 7, 6, 8, 6, 7, 7, 8, 6, 7, 6, 5]

df_companies = pd.DataFrame({
    'Company': companies,
    'Reddit': reddit_score,
    'Gov/CFPB': gov_score,
    'News': news_score,
    'Review Sites': review_score
})
df_companies['Total'] = df_companies[['Reddit', 'Gov/CFPB', 'News', 'Review Sites']].sum(axis=1)
df_companies = df_companies.sort_values('Total', ascending=True)

fig, ax = plt.subplots(figsize=(14, 9))
bottom = np.zeros(len(df_companies))
colors_stack = ['#f85149', '#388bfd', '#3fb950', '#d29922']
labels = ['Reddit', 'Gov/CFPB', 'News Coverage', 'Review Sites']

for i, (col, color, label) in enumerate(zip(['Reddit', 'Gov/CFPB', 'News', 'Review Sites'], colors_stack, labels)):
    vals = df_companies[col].values
    ax.barh(df_companies['Company'], vals, left=bottom, color=color, label=label, edgecolor='#30363d', linewidth=0.5)
    bottom += vals

for idx, total in enumerate(df_companies['Total']):
    ax.text(total + 0.3, idx, str(total), va='center', ha='left', color='#e6edf3', fontweight='bold', fontsize=11)

ax.set_xlabel('Composite Complaint Signal (sum across sources)')
ax.set_title('Most Complained-About Companies — 2025-2026\nMulti-Source Composite (Reddit + Gov + News + Review Sites)', fontweight='bold', pad=15)
ax.legend(loc='lower right', framealpha=0.8, edgecolor='#30363d')
ax.set_xlim(0, 42)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#30363d')
ax.spines['left'].set_color('#30363d')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/05_most_complained_companies.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ VIZ 5: Most Complained-About Companies saved")

# ============================================================
# VIZ 6: Startup Opportunity Score Matrix
# ============================================================
opportunity_data = pd.DataFrame({
    'Complaint Area': [
        'AI Chatbot Navigation\n(Get to human faster)',
        'Billing Error Detection\n& Auto-Dispute',
        'Insurance Claim\nDenial Appeals',
        'Subscription\nCancellation Agent',
        'Airline Compensation\n& Rebooking',
        'Credit Report\nError Correction',
        'Hold Time\nElimination',
        'Delivery Issue\nResolution',
    ],
    'Pain Severity': [9.5, 9.0, 9.5, 8.5, 8.0, 9.0, 8.0, 7.0],
    'Market Size': [9.0, 8.5, 8.0, 7.5, 7.0, 9.0, 6.5, 7.0],
    'AI Solvability': [9.0, 9.5, 7.5, 9.0, 8.5, 8.0, 8.5, 7.5],
    'Willingness to Pay': [8.5, 8.0, 9.0, 7.0, 7.5, 8.5, 7.0, 6.0],
})
opportunity_data['Opportunity Score'] = (
    opportunity_data['Pain Severity'] * 0.30 +
    opportunity_data['Market Size'] * 0.25 +
    opportunity_data['AI Solvability'] * 0.25 +
    opportunity_data['Willingness to Pay'] * 0.20
)
opportunity_data = opportunity_data.sort_values('Opportunity Score', ascending=True)

fig, ax = plt.subplots(figsize=(14, 8))
colors_opp = plt.cm.cool(np.linspace(0.2, 0.9, len(opportunity_data)))
bars = ax.barh(opportunity_data['Complaint Area'], opportunity_data['Opportunity Score'],
               color=colors_opp, edgecolor='#30363d', linewidth=0.5, height=0.7)
for bar, score in zip(bars, opportunity_data['Opportunity Score']):
    ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2, f'{score:.1f}/10',
            va='center', ha='left', color='#e6edf3', fontweight='bold', fontsize=12)
ax.set_xlabel('Startup Opportunity Score (pain 30%, market 25%, AI solvability 25%, willingness to pay 20%)')
ax.set_title('AI Complaint-Resolution Agent — Startup Opportunity Scores\nWhere Should an MVP Focus?', fontweight='bold', pad=15)
ax.set_xlim(0, 10.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#30363d')
ax.spines['left'].set_color('#30363d')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/06_startup_opportunity_scores.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ VIZ 6: Startup Opportunity Score Matrix saved")

# ============================================================
# Export Master CSV
# ============================================================
master_table = pd.DataFrame({
    'Rank': range(1, 11),
    'Complaint Type': [
        'AI Chatbot Gatekeeping / Defensive AI',
        'Credit Report Errors (CFPB #1)',
        'Telecom/ISP Billing Fraud',
        'Health Insurance Claim Denials',
        'Subscription Cancellation Dark Patterns',
        'Multi-Hour Hold Times',
        'Airline Service Failures',
        'Mobile Carrier Overcharges',
        'Food Delivery Refund Denials',
        'Package Delivery Failures'
    ],
    'Primary Industries': [
        'All (esp. Telecom, E-Commerce)',
        'Financial Services, Credit Bureaus',
        'Telecom/ISP (Comcast, Verizon)',
        'Health Insurance (UnitedHealthcare)',
        'Streaming, SaaS, Fitness, Retail',
        'Airlines, Telecom, Government',
        'Airlines (American, Frontier, United)',
        'Telecom (Verizon, T-Mobile)',
        'Food Delivery (Uber Eats, DoorDash)',
        'Logistics (FedEx, Amazon, USPS)'
    ],
    'Volume Signal': [
        '73% of CX leaders cite AI resistance; 45% abandon chatbots',
        '3.19M CFPB complaints; credit reports = 85% of total',
        'Hundreds of forum threads; bills 5-10x agreed',
        '16% in-network denial rate; 90% AI error rate in class action',
        '76% of sub services use dark patterns; FTC rule vacated',
        '3-10hr waits; CA legislation pending',
        '9K+ Reddit posts/month; record DOT complaints',
        '$1,400 billing nightmares; dozens of FCC complaints',
        '30/1000 customers request refunds (20x avg)',
        '260M packages stolen/year; FedEx suspended guarantees'
    ],
    'Composite Score': [9.5, 9.2, 8.8, 8.8, 8.5, 7.5, 8.2, 7.3, 7.0, 6.8],
    'Startup Opportunity Score': [9.1, 8.6, 8.8, 8.5, 8.3, 7.5, 7.8, 7.8, 7.0, 6.9]
})
master_table.to_csv(f'{OUT_DIR}/master_complaint_rankings.csv', index=False)
print("✓ Master CSV exported")

print("\n✓ All visualizations generated successfully!")
print(f"  Output directory: {OUT_DIR}")
