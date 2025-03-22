import matplotlib
import pandas as pd
import pypistats
import matplotlib.pyplot as plt
import json

FONT_SIZE = 16
matplotlib.rcParams.update({'font.size': FONT_SIZE})

# Fetch usage data for a specific package over a time range
data = pypistats.python_minor('pip', format='json', total='monthly')
j = json.loads(data)['data']

recent_data = pd.DataFrame(j)

recent_data = recent_data.dropna()
recent_data = recent_data.dropna(how='any',axis=0)
df = recent_data[recent_data.category != 'null']
df = df[df.date != '2025-03']

# Aggregate total downloads per version
total_downloads = df.groupby('category')['downloads'].sum()

# Select the top 5 most used Python versions
top_versions = total_downloads.nlargest(5).index

df.loc[:, ('date')] = pd.to_datetime(df.loc[:, ('date')], format='%Y-%m')

# Plot
plt.figure(figsize=(12, 6))
for version in top_versions:
    version_data = df[df['category'] == version]
    plt.plot(version_data['date'], version_data['downloads'], label=f'Python {version}')

plt.xlabel('Date')
plt.ylabel('Downloads')
plt.title('Monthly Python Version Usage Statistics (Top 5 Versions)')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('version.png')
plt.show()