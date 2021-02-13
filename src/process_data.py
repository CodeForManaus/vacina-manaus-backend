# coding: utf-8

import os
import sys

import pandas as pd

from progress_download import ProgressDownload

MANAUS_ESTIMATED_POPULATION = 2219580
VACCINE_TARGET = 70  # %
VACCINE_TARGET_ESTIMATED_POPULATION = MANAUS_ESTIMATED_POPULATION*VACCINE_TARGET/100


def get_latest_filename():
    paths = os.listdir('data/cleaned')
    # Add absolute path to get information about tha last modification to max method
    _paths = list(map(lambda x: 'data/cleaned/{}'.format(x), paths))
    return max(_paths, key=os.path.getctime)


class DataProcessor:

    def __init__(self, input, output_path):
        self.df = pd.read_csv(input)
        self.output_path = output_path

        self.df['vaccine_date'] = pd.to_datetime(self.df['vaccine_date'], format='%d/%m/%Y')

    @staticmethod
    def __calculate_interval(days_from_now: int = 3, from_day: int = None, to_day: int = None):
        from_day = from_day or days_from_now * -1 + 1
        to_day = to_day or 0
        interval = len(range(from_day, to_day))+1

        return from_day, to_day, interval

    def vaccination_count(self):
        df_ = pd.DataFrame(data={
            'vaccinated': [len(self.df)],
            'estimated_non_vaccinated': [int(MANAUS_ESTIMATED_POPULATION*VACCINE_TARGET/100-len(self.df))]
        })

        return df_

    def vaccination_count_statistics(self):
        df_ = pd.DataFrame(data={
            'vaccinated': [len(self.df)],
            'estimated_non_vaccinated': [int(MANAUS_ESTIMATED_POPULATION*VACCINE_TARGET/100-len(self.df))],
            'estimated_population': [MANAUS_ESTIMATED_POPULATION],
        })

        df_['estimated_vaccinated_percentage'] = df_['vaccinated']/df_['estimated_population']*100
        df_['estimated_non_vaccinated_percentage'] = 100 - df_['estimated_vaccinated_percentage']

        return df_

    def vaccination_site_count(self):
        return self.df[['vaccination_site', 'id']]\
            .groupby('vaccination_site')\
            .count()\
            .rename(columns={'id': 'count'})\
            .sort_values(['count'], ascending=False)

    def area_count(self):
        return self.df[['area', 'id']]\
            .groupby('area')\
            .count()\
            .rename(columns={'id': 'count'})\
            .sort_values(['count'], ascending=False)

    def vaccine_date_count(self, format_datetime=True):
        df_ = self.df[['vaccine_date', 'id']]

        df_ = df_.loc[df_['vaccine_date'] >= '2021-01-01'] \
            .groupby('vaccine_date')\
            .count()\
            .rename(columns={'id': 'count'})\
            .sort_values(['vaccine_date'], ascending=True)

        idx = pd.date_range(start=df_.index.min(), end=df_.index.max())

        df_.index = pd.DatetimeIndex(df_.index)

        df_ = df_.reindex(idx, fill_value=0)

        df_.index = df_.index.rename('vaccine_date')

        if format_datetime:
            df_.index = df_.index.strftime("%d/%m/%Y")

        return df_

    def vaccine_evolution_by_date(self, format_datetime=True):
        df_ = self.vaccine_date_count(format_datetime=False).cumsum()

        if format_datetime:
            df_.index = df_.index.strftime("%d/%m/%Y")

        return df_

    def vaccine_date_count_by_interval(
        self,
        format_datetime=True,
        days_from_now=3,
        from_day=None,
        to_day=None
    ):

        from_day, to_day, interval = self.__calculate_interval(
            days_from_now,
            from_day,
            to_day
        )

        df_ = pd.merge(
            self.vaccine_date_count(format_datetime=False).reset_index(),
            self.vaccine_date_count(format_datetime=False).reset_index(),
            how='cross'
        )

        df_['diff_days'] = (df_['vaccine_date_y'] - df_['vaccine_date_x']).dt.days

        df_ = df_.loc[(df_['diff_days'] >= from_day) & (df_['diff_days'] <= to_day)][['vaccine_date_x', 'count_y']] \
            .rename(columns={'vaccine_date_x': 'vaccine_date', 'count_y': 'count'})

        df_ = pd.merge(
            df_,
            df_.groupby('vaccine_date').count().reset_index(),
            how='inner',
            on='vaccine_date'
        ).rename(columns={'count_x': 'count', 'count_y': 'interval'})

        df_ = df_.loc[df_['interval'] == interval][['vaccine_date', 'count']] \
            .groupby('vaccine_date') \
            .sum()

        if format_datetime:
            df_.index = df_.index.strftime("%d/%m/%Y")

        return df_

    def vaccine_date_count_moving_avg(
        self,
        format_datetime=True,
        days_from_now=3,
        from_day=None,
        to_day=None
    ):

        from_day, to_day, interval = self.__calculate_interval(
            days_from_now,
            from_day,
            to_day
        )

        moving_avg_key = 'moving_avg_{}_days'.format(interval)

        df_ = self.vaccine_date_count_by_interval(
            format_datetime=False,
            days_from_now=days_from_now,
            from_day=from_day,
            to_day=to_day
        ).rename(columns={'count': moving_avg_key})

        df_[moving_avg_key] = (df_[moving_avg_key]/interval).astype(int)

        if format_datetime:
            df_.index = df_.index.strftime("%d/%m/%Y")

        return df_

    def vaccine_trend(
        self,
        format_datetime=True,
        days_from_now=3,
        from_day=None,
        to_day=None
    ):

        from_day, to_day, interval = self.__calculate_interval(
            days_from_now,
            from_day,
            to_day
        )

        df_ = pd.merge(
            self.vaccine_evolution_by_date(
                format_datetime=False,
            ).reset_index(),
            self.vaccine_date_count_moving_avg(
                format_datetime=False,
                days_from_now=days_from_now,
                from_day=from_day,
                to_day=to_day
            ).reset_index(),
            how='inner',
            on='vaccine_date',
        ).set_index('vaccine_date')

        moving_avg_key = 'moving_avg_{}_days'.format(interval)
        trend_key = 'trend_{}_days'.format(interval)

        df_['remaining_vaccination'] = VACCINE_TARGET_ESTIMATED_POPULATION - df_['count']
        df_[trend_key] = (df_['remaining_vaccination']/df_[moving_avg_key]).astype(int)

        df_ = df_[[trend_key]]

        if format_datetime:
            df_.index = df_.index.strftime("%d/%m/%Y")

        return df_

    def cpf_count(self):
        return self.df[['cpf', 'id']]\
            .groupby('cpf')\
            .count()\
            .rename(columns={'id': 'count'})\
            .sort_values(['count'], ascending=False)

    def full_name_count(self):
        return self.df[['full_name', 'id']]\
            .groupby('full_name')\
            .count()\
            .rename(columns={'id': 'count'})\
            .sort_values(['count'], ascending=False)

    def service_group_count(self):
        return self.df[['service_group', 'id']]\
            .groupby('service_group')\
            .count()\
            .rename(columns={'id': 'count'})\
            .sort_values(['count'], ascending=False)

    def priority_group_count(self):
        return self.df[['priority_group', 'id']]\
            .groupby('priority_group')\
            .count()\
            .rename(columns={'id': 'count'})\
            .sort_values(['count'], ascending=False)

    def uncategorized_service_group_by_area_count(self):
        return self.df.loc[self.df['service_group'] == 'Outros', ['area', 'id']] \
            .groupby('area') \
            .count() \
            .rename(columns={'id': 'count'}) \
            .sort_values(['count'], ascending=False)

    def uncategorized_service_group_by_area_full_data(self):
        df_ = self.uncategorized_service_group_by_area_count()\
            .rename(columns={'count': 'uncategorized_count'})\
            .join(self.area_count().rename(columns={'count': 'total_count'}))

        df_['categorized_count'] = df_['total_count'] - df_['uncategorized_count']
        df_['uncategorized_percent'] = df_['uncategorized_count']/df_['total_count']*100
        df_['categorized_percent'] = df_['categorized_count']/df_['total_count']*100

        return df_

    def uncategorized_service_group_by_area_percent(self):
        return self.uncategorized_service_group_by_area_full_data()[['uncategorized_percent']]\
            .sort_values(['uncategorized_percent'], ascending=False)

    def uncategorized_service_group_by_vaccination_site_count(self):
        return self.df.loc[self.df['service_group'] == 'Outros', ['vaccination_site', 'id']]\
            .groupby('vaccination_site')\
            .count()\
            .rename(columns={'id': 'count'})\
            .sort_values(['count'], ascending=False)

    def uncategorized_service_group_by_vaccination_site_full_data(self):
        df_ = self.uncategorized_service_group_by_vaccination_site_count()\
            .rename(columns={'count': 'uncategorized_count'})\
            .join(self.vaccination_site_count().rename(columns={'count': 'total_count'}))

        df_['categorized_count'] = df_['total_count'] - df_['uncategorized_count']
        df_['uncategorized_percent'] = df_['uncategorized_count']/df_['total_count']*100
        df_['categorized_percent'] = df_['categorized_count']/df_['total_count']*100

        return df_

    def uncategorized_service_group_by_vaccination_site_percent(self):
        return self.uncategorized_service_group_by_vaccination_site_full_data()[['uncategorized_percent']]\
            .sort_values(['uncategorized_percent'], ascending=False)

    def vaccine_by_service_group_and_vaccine_date_count(self, pivot=True, format_datetime=True):
        df_ = self.df[['id', 'service_group', 'vaccine_date']] \
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

        df_ = df_[['service_group', 'vaccine_date', 'count']] \
            .sort_values(['service_group', 'vaccine_date'])\
            .reset_index()

        if pivot:
            df_ = df_.pivot_table('count', ['vaccine_date'], 'service_group')

        if format_datetime:
            df_.index = df_.index.strftime("%d/%m/%Y")

        return df_

    def vaccine_by_service_group_and_vaccine_date_evolution(self, pivot=True, format_datetime=True):
        df_ = pd.merge(
            self.vaccine_by_service_group_and_vaccine_date_count(pivot=False, format_datetime=False)
            [['service_group', 'vaccine_date']],

            self.vaccine_by_service_group_and_vaccine_date_count(pivot=False, format_datetime=False)
            [['service_group', 'vaccine_date', 'count']]
            .rename(columns={'vaccine_date': 'vaccine_date2'}),

            how='inner',
            on=['service_group']
        )

        df_ = df_.loc[df_['vaccine_date'] >= df_['vaccine_date2']] \
            .groupby(['service_group', 'vaccine_date'], as_index=False) \
            .sum('count') \
            .reset_index()

        if pivot:
            df_ = df_.pivot_table('count', ['vaccine_date'], 'service_group')

        if format_datetime:
            df_.index = df_.index.strftime("%d/%m/%Y")

        return df_

    def process_all(self):

        dfs_to_extract = [
            self.vaccination_count,
            self.vaccination_count_statistics,
            self.vaccination_site_count,
            self.area_count,
            self.cpf_count,
            self.full_name_count,
            self.service_group_count,
            self.priority_group_count,
            self.vaccine_by_service_group_and_vaccine_date_count,
            self.vaccine_by_service_group_and_vaccine_date_evolution,
            self.vaccine_date_count,
            self.vaccine_date_count_moving_avg,
            self.vaccine_trend,
            self.uncategorized_service_group_by_area_count,
            self.uncategorized_service_group_by_area_percent,
            self.uncategorized_service_group_by_vaccination_site_full_data,
            self.uncategorized_service_group_by_vaccination_site_percent
        ]

        count = 1
        size_dfs = len(dfs_to_extract)
        progress_download = ProgressDownload()
        for df_to_extract in dfs_to_extract:

            df_to_extract().to_csv(
                ''.join(
                    ['/'.join([self.output_path, df_to_extract.__name__]), '.csv']
                ), encoding='utf-8-sig'
            )

            progress_download(count, 1, size_dfs)
            count += 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        fileName = get_latest_filename()
    dataProcessor = DataProcessor(fileName, 'data/analyzed')
    dataProcessor.process_all()
