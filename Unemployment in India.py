import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Basic plot styling ---
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (12, 6)
sns.set_palette("husl")

# --- Load the data ---
csv_path = "C:\\Users\\Shagun Singh\\Desktop\\Python\\Unemployment in India.csv"

try:
    data = pd.read_csv(csv_path).dropna(how='all')
except FileNotFoundError:
    print(f"Could not find the file at: {csv_path}")
    exit()

# --- Clean and prepare ---
data.columns = data.columns.str.strip()
data['Date'] = data['Date'].astype(str).str.strip()
data['Date'] = pd.to_datetime(data['Date'], format='%d-%m-%Y', errors='coerce')
data.dropna(subset=['Date'], inplace=True)

data['Year'] = data['Date'].dt.year
data['Month_Year'] = data['Date'].dt.to_period('M')

data.rename(columns={
    'Estimated Unemployment Rate (%)': 'Unemployment_Rate',
    'Estimated Employed': 'Employed',
    'Estimated Labour Participation Rate (%)': 'Labour_Participation_Rate',
    'Region': 'State'
}, inplace=True)

for col in ['Unemployment_Rate', 'Employed', 'Labour_Participation_Rate']:
    data[col] = pd.to_numeric(data[col], errors='coerce')

data['COVID'] = data['Date'] >= '2020-04-01'


# --- Visualisations ---
def overall_trend():
    monthly_avg = data.groupby('Month_Year')['Unemployment_Rate'].mean().reset_index()
    monthly_avg['Month_Year'] = monthly_avg['Month_Year'].astype(str)

    colors = ['red' if '2020-04' <= m <= '2020-06' else 'blue'
              for m in monthly_avg['Month_Year']]

    plt.figure()
    sns.barplot(x='Month_Year', y='Unemployment_Rate',
                data=monthly_avg, palette=colors)
    plt.xticks(rotation=45, ha='right')
    plt.title('Monthly Average Unemployment Rate (2019–2020)')

    pre_covid_avg = monthly_avg[monthly_avg['Month_Year'] < '2020-04']['Unemployment_Rate'].mean()
    covid_peak_avg = monthly_avg[(monthly_avg['Month_Year'] >= '2020-04') &
                                 (monthly_avg['Month_Year'] <= '2020-06')]['Unemployment_Rate'].mean()

    plt.axhline(pre_covid_avg, color='green', ls='--', label=f'Pre-COVID Avg: {pre_covid_avg:.1f}%')
    plt.axhline(covid_peak_avg, color='red', ls='--', label=f'COVID Peak Avg: {covid_peak_avg:.1f}%')

    plt.legend()
    plt.tight_layout()
    plt.show()


def state_comparison():
    covid_avg = (data[data['COVID']]
                 .groupby('State')['Unemployment_Rate']
                 .mean()
                 .sort_values(ascending=False))

    plt.figure()
    sns.barplot(x=covid_avg.values, y=covid_avg.index, palette='viridis')
    plt.xlabel('Unemployment Rate (%)')
    plt.title('State-wise Average Unemployment (Apr–Jun 2020)')
    plt.tight_layout()
    plt.show()


def rural_vs_urban():
    trend = (data.groupby(['Area', 'Month_Year'])['Unemployment_Rate']
             .mean()
             .unstack(level=0))

    trend.plot(marker='o')
    plt.title('Rural vs Urban Unemployment Trend')
    plt.xlabel('Month–Year')
    plt.ylabel('Unemployment Rate (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def covid_impact():
    pre_covid = data[~data['COVID']].groupby('State')['Unemployment_Rate'].mean()
    during_covid = data[data['COVID']].groupby('State')['Unemployment_Rate'].mean()
    change = (during_covid - pre_covid).sort_values()

    plt.figure()
    change.plot(kind='barh', color='purple')
    plt.xlabel('Change (%)')
    plt.title('Change in Unemployment: Pre vs During COVID')
    plt.tight_layout()
    plt.show()


def participation_relation():
    plt.figure()
    sns.scatterplot(x='Labour_Participation_Rate',
                    y='Unemployment_Rate',
                    hue='COVID', data=data, alpha=0.7)
    plt.title('Unemployment vs Labour Participation')
    plt.tight_layout()
    plt.show()


def employment_loss():
    pre_covid = data[~data['COVID']].groupby('State')['Employed'].mean()
    during_covid = data[data['COVID']].groupby('State')['Employed'].mean()
    change_percent = ((during_covid - pre_covid) / pre_covid * 100).sort_values()

    plt.figure()
    change_percent.plot(kind='barh', color='orange')
    plt.title('Employment Change During COVID (%)')
    plt.tight_layout()
    plt.show()


# --- Run the dashboard ---
if __name__ == '__main__':
    print("\n=== Unemployment Analysis Dashboard ===\n")
    overall_trend()
    state_comparison()
    rural_vs_urban()
    covid_impact()
    participation_relation()
    employment_loss()

