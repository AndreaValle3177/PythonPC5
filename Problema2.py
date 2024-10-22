import pandas as pd
import sqlite3
from pymongo import MongoClient

df = pd.read_csv('winemag-data-130k-v2.csv')

print("Exploración del DataFrame:")
print(df.head())
print(df.info())
print(df.describe())

df.rename(columns={
    'country': 'Country',
    'points': 'Points',
    'price': 'Price',
    'variety': 'Variety'
}, inplace=True)

df['Continent'] = df['Country'].map({
    'France': 'Europe',
    'Italy': 'Europe',
    'Spain': 'Europe',
    'USA': 'North America',
    'Argentina': 'South America',
    'Chile': 'South America',
    'Australia': 'Oceania',
    'South Africa': 'Africa'
}).fillna('Other')

df['Price_per_point'] = df['Price'] / df['Points']
df['High_Score'] = df['Points'] >= 90

best_wines = df.groupby('Continent').agg({'Points': 'max'}).reset_index()

avg_price_reviews = df.groupby('Country').agg({'Price': 'mean', 'review_count': 'count'}).reset_index()
avg_price_reviews = avg_price_reviews.sort_values(by='Price', ascending=False)

high_score_wines = df[df['High_Score']][['Country', 'Variety', 'Points', 'Price']]

wine_count_by_country = df['Country'].value_counts().reset_index()
wine_count_by_country.columns = ['Country', 'Wine_Count']

best_wines.to_csv('best_wines.csv', index=False)
avg_price_reviews.to_excel('avg_price_reviews.xlsx', index=False)
high_score_wines.to_sql('high_score_wines', sqlite3.connect('winedata.db'), index=False, if_exists='replace')
wine_count_by_country.to_json('wine_count_by_country.json', orient='records')

client = MongoClient('mongodb://localhost:27017/')
db = client['wine_db']
db['wine_count_by_country'].insert_many(wine_count_by_country.to_dict('records'))

print("Reportes generados y exportados.")

