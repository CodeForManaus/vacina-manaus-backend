# coding: utf-8

import pandas as pd

input = "db/007_Vacinados_2021_01_23_17_17_00.json"
output_path = 'analytics'

df = pd.read_json(input)

queries = {
    'vaccination_site_count': df[['vaccination_site', 'id']].groupby('vaccination_site').count().rename(columns={'id': 'count'}).sort_values(['count'], ascending=False),
    'area_count': df[['area', 'id']].groupby('area').count().rename(columns={'id': 'count'}).sort_values(['count'], ascending=False),
    'cpf_count': df[['cpf', 'id']].groupby('cpf').count().rename(columns={'id': 'count'}).sort_values(['count'], ascending=False),
    'full_name_count': df[['full_name', 'id']].groupby('full_name').count().rename(columns={'id': 'count'}).sort_values(['count'], ascending=False),
    'service_group_count': df[['service_group', 'id']].groupby('service_group').count().rename(columns={'id': 'count'}).sort_values(['count'], ascending=False),
    'priority_group_count': df[['priority_group', 'id']].groupby('priority_group').count().rename(columns={'id': 'count'}).sort_values(['count'], ascending=False),
    'vaccine_date_count': df[['vaccine_date', 'id']].groupby('vaccine_date').count().rename(columns={'id': 'count'}).sort_values(['count'], ascending=False),
}

query_results = {}

for query_name, query in queries.items():
    query.to_csv(''.join(['/'.join([output_path, query_name]), '.csv']), encoding='utf-8-sig')
