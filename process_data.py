# coding: utf-8
import os

import pandas as pd

MANAUS_ESTIMATED_POPULATION = 2219580
VACCINE_TARGET = 70  # %

paths = os.listdir('db')
# Add absolute path to get information about tha last modification to max method
_paths = list(map(lambda x: 'db/{}'.format(x), paths))
input = max(_paths, key=os.path.getctime)

output_path = 'analytics'

df = pd.read_json(input)

# DataFrame definitions


def vaccination_count():
    df_ = pd.DataFrame(data={
        'vaccinated': [len(df)],
        'estimated_non_vaccinated': [int(MANAUS_ESTIMATED_POPULATION*VACCINE_TARGET/100-len(df))]
    })

    return df_


def vaccination_count_statistics():
    df_ = pd.DataFrame(data={
        'vaccinated': [len(df)],
        'estimated_non_vaccinated': [int(MANAUS_ESTIMATED_POPULATION*VACCINE_TARGET/100-len(df))],
        'estimated_population': [MANAUS_ESTIMATED_POPULATION],
    })

    df_['estimated_vaccinated_percentage'] = df_['vaccinated']/df_['estimated_population']*100
    df_['estimated_non_vaccinated_percentage'] = 100 - df_['estimated_vaccinated_percentage']

    return df_


def vaccination_site_count():
    return df[['vaccination_site', 'id']]\
        .groupby('vaccination_site')\
        .count()\
        .rename(columns={'id': 'count'})\
        .sort_values(['count'], ascending=False)


def area_count():
    return df[['area', 'id']]\
        .groupby('area')\
        .count()\
        .rename(columns={'id': 'count'})\
        .sort_values(['count'], ascending=False)


def cpf_count():
    return df[['cpf', 'id']]\
        .groupby('cpf')\
        .count()\
        .rename(columns={'id': 'count'})\
        .sort_values(['count'], ascending=False)


def full_name_count():
    return df[['full_name', 'id']]\
        .groupby('full_name')\
        .count()\
        .rename(columns={'id': 'count'})\
        .sort_values(['count'], ascending=False)


def service_group_count():
    return df[['service_group', 'id']]\
        .groupby('service_group')\
        .count()\
        .rename(columns={'id': 'count'})\
        .sort_values(['count'], ascending=False)


def priority_group_count():
    return df[['priority_group', 'id']]\
        .groupby('priority_group')\
        .count()\
        .rename(columns={'id': 'count'})\
        .sort_values(['count'], ascending=False)


def vaccine_date_count():
    return df[['vaccine_date', 'id']]\
        .groupby('vaccine_date')\
        .count()\
        .rename(columns={'id': 'count'})\
        .sort_values(['vaccine_date'], ascending=True)


def vaccine_by_service_group_and_vaccine_date_count():
    df_ = df[['id', 'service_group', 'vaccine_date']] \
        .groupby(['service_group', 'vaccine_date'], as_index=False) \
        .count() \
        .rename(columns={'id': 'count'})

    df_ = pd.merge(
        df_,
        pd.merge(
            df_[['service_group', 'count']]
            .groupby('service_group', as_index=False)
            .count()
            .assign(count=0)
            .set_index('count'),

            df_[['vaccine_date', 'count']]
            .groupby('vaccine_date', as_index=False)
            .count()
            .assign(count=0)
            .set_index('count'),

            how='cross'
        ).assign(count=0),
        how='outer',
        on=['service_group', 'vaccine_date']
    ).fillna(0)

    df_['count'] = (df_['count_x'] + df_['count_y']).astype(int)

    return df_[['service_group', 'vaccine_date', 'count']] \
        .sort_values(['service_group', 'vaccine_date'])


def vaccine_by_service_group_and_vaccine_date_evolution():
    df_ = pd.merge(
        vaccine_by_service_group_and_vaccine_date_count()[['service_group', 'vaccine_date']],
        vaccine_by_service_group_and_vaccine_date_count()[['service_group', 'vaccine_date', 'count']]
        .rename(columns={'vaccine_date': 'vaccine_date2'}),
        how='inner',
        on=['service_group']
    )

    df_ = df_.loc[df_['vaccine_date'] >= df_['vaccine_date2']] \
        .groupby(['service_group', 'vaccine_date'], as_index=False) \
        .sum('count')

    return df_


def uncategorized_service_group_by_area_count():
    return df.loc[df['service_group'] == 'Outros', ['area', 'id']] \
        .groupby('area') \
        .count() \
        .rename(columns={'id': 'count'}) \
        .sort_values(['count'], ascending=False)


def uncategorized_service_group_by_area_full_data():
    df_ = uncategorized_service_group_by_area_count()\
        .rename(columns={'count': 'uncategorized_count'})\
        .join(area_count().rename(columns={'count': 'total_count'}))

    df_['categorized_count'] = df_['total_count'] - df_['uncategorized_count']
    df_['uncategorized_percent'] = df_['uncategorized_count']/df_['total_count']*100
    df_['categorized_percent'] = df_['categorized_count']/df_['total_count']*100

    return df_


def uncategorized_service_group_by_area_percent():
    return uncategorized_service_group_by_area_full_data()[['uncategorized_percent']]\
        .sort_values(['uncategorized_percent'], ascending=False)


def uncategorized_service_group_by_vaccination_site_count():
    return df.loc[df['service_group'] == 'Outros', ['vaccination_site', 'id']]\
        .groupby('vaccination_site')\
        .count()\
        .rename(columns={'id': 'count'})\
        .sort_values(['count'], ascending=False)


def uncategorized_service_group_by_vaccination_site_full_data():
    df_ = uncategorized_service_group_by_vaccination_site_count()\
        .rename(columns={'count': 'uncategorized_count'})\
        .join(vaccination_site_count().rename(columns={'count': 'total_count'}))

    df_['categorized_count'] = df_['total_count'] - df_['uncategorized_count']
    df_['uncategorized_percent'] = df_['uncategorized_count']/df_['total_count']*100
    df_['categorized_percent'] = df_['categorized_count']/df_['total_count']*100

    return df_


def uncategorized_service_group_by_vaccination_site_percent():
    return uncategorized_service_group_by_vaccination_site_full_data()[['uncategorized_percent']]\
        .sort_values(['uncategorized_percent'], ascending=False)


dfs_to_extract = [
    vaccination_count,
    vaccination_count_statistics,
    vaccination_site_count,
    area_count,
    cpf_count,
    full_name_count,
    service_group_count,
    priority_group_count,
    vaccine_by_service_group_and_vaccine_date_count,
    vaccine_by_service_group_and_vaccine_date_evolution,
    vaccine_date_count,
    uncategorized_service_group_by_area_count,
    uncategorized_service_group_by_area_percent,
    uncategorized_service_group_by_vaccination_site_full_data,
    uncategorized_service_group_by_vaccination_site_percent
]

for df_to_extract in dfs_to_extract:
    df_to_extract().to_csv(''.join(['/'.join([output_path, df_to_extract.__name__]), '.csv']), encoding='utf-8-sig')
