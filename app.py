import matplotlib
matplotlib.use('TkAgg')  

import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('dark_background')

# ==========================================
# 1. DOWNLOAD & LOAD DATA
# ==========================================
print("Fetching official COVID-19 data...")
data_url = "https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv"
df = pd.read_csv(data_url)
df['date'] = pd.to_datetime(df['date'])
print("Data loaded successfully!")

# ==========================================
# 2. FILTER GLOBAL LEADERBOARD DATA
# ==========================================
latest_date = df['date'].max()
clean_df = df[
    (df['date'] == latest_date) & 
    (df['code'].str.len() == 3) & 
    (~df['country'].str.contains('World|income|High|Middle|Low|Union|Europe|Asia|Africa|America', na=False, case=False))
]
top_10_countries = clean_df.nlargest(10, 'total_cases').copy()

# ==========================================
# 3. BUILD INTERACTIVE LAYOUT
# ==========================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), facecolor='#121212')
ax1.set_facecolor('#1e1e1e')
ax2.set_facecolor('#1e1e1e')

vibrant_colors = ['#FF4136', '#FF851B', '#FFDC00', '#2ECC40', '#0074D9', '#B10DC9', '#FF007F', '#01FF70', '#7FDBFF', '#E0115F']

# CRITICAL CHANGE: added picker=True so the bars detect clicks
bars = ax1.bar(top_10_countries['country'], top_10_countries['total_cases'] / 1e6, 
              color=vibrant_colors, edgecolor='white', linewidth=0.7, picker=True)

# Static values over bars
for bar in bars:
    height = bar.get_height()
    ax1.annotate(f'{height:.1f}M',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4), textcoords="offset points",
                ha='center', va='bottom', fontsize=9, color='white', fontweight='bold')

ax1.set_title("Global Leaderboard: Click a Bar to Switch Country", fontsize=13, fontweight='bold', color='#00FFCC', pad=15)
ax1.set_ylabel("Total Cases (In Millions)", fontsize=11, color='#AAAAAA')
ax1.tick_params(colors='white', labelsize=9)
ax1.set_xticklabels(top_10_countries['country'], rotation=35, ha='right')
ax1.grid(axis='y', linestyle=':', alpha=0.15, color='white')
ax1.set_axisbelow(True)

# Draw an initial default line plot (United States)
initial_country = "United States"
country_df = df[df['country'] == initial_country].sort_values('date')
line, = ax2.plot(country_df['date'], country_df['total_cases'] / 1e6, color='#FF007F', linewidth=3)

ax2.set_title(f"Pandemic Timeline: {initial_country}", fontsize=14, fontweight='bold', color='#00FFCC', pad=15)
ax2.set_ylabel("Total Cases (In Millions)", fontsize=11, color='#AAAAAA')
ax2.set_xlabel("Year", fontsize=11, color='#AAAAAA')
ax2.grid(True, linestyle='--', alpha=0.15, color='white')

# ==========================================
# 4. INTERACTION LOGIC (The Click Event)
# ==========================================
def on_click(event):
    # Find out which bar index number was clicked
    bar_index = event.ind[0]
    
    # Extract the matching country string identifier
    clicked_country = top_10_countries['country'].iloc[bar_index]
    
    # Filter fresh timeline metrics for that specific country
    new_country_df = df[df['country'] == clicked_country].sort_values('date')
    
    # Redraw the line graph with the new data vectors
    line.set_data(new_country_df['date'], new_country_df['total_cases'] / 1e6)
    
    # Adjust the Y-axis scale so it fits the new country perfectly
    ax2.set_ylim(0, (new_country_df['total_cases'].max() / 1e6) * 1.05)
    ax2.set_xlim(new_country_df['date'].min(), new_country_df['date'].max())
    
    # Refresh the label header text dynamically
    ax2.set_title(f"Pandemic Timeline: {clicked_country}", fontsize=14, fontweight='bold', color='#00FFCC', pad=15)
    
    # Force layout redraw
    fig.canvas.draw_idle()

# Hook the click engine directly into the application window UI
fig.canvas.mpl_connect('pick_event', on_click)

plt.tight_layout()
plt.show()