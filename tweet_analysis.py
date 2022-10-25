from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

def determine_gender(username, male_names, female_names):
    contains_username = lambda row: username.lower() in row['name'].lower()
    male_count = male_names[male_names.apply(contains_username)]['count'].sum()
    female_count = female_names[female_names.apply(contains_username)]['count'].sum()

    if male_count > female_count:
        return 'Male'
    elif female_count > male_count:
        return 'Female'
    else:
        return 'Other/Unknown'

def label_genders(tweet_sample):
    male_names = pd.read_csv('male_names.tsv', sep='\t')
    female_names = pd.read_csv('female_names.tsv', sep='\t')    

    def get_genders(username_field):
        return lambda row: determine_gender(row[username_field], male_names, female_names)    

    tweet_sample['gender'] = tweet_sample.apply(get_genders('username'))
    tweet_sample['original_poster_gender'] = tweet_sample.apply(get_genders('original_poster'))

    return tweet_sample

def to_datetime(date_str, time_str):
    return datetime.fromisoformat(f'{date_str}T{time_str}')

def time_series(tweet_sample):
    time_series = tweet_sample.copy()
    first_sample = time_series.loc[0]
    start = to_datetime(first_sample['date'], first_sample['time'])

    convert_datetime = lambda row: (to_datetime(row['date'], row['time']) - start).hours
    time_series['time'] = time_series.apply(convert_datetime)  
    time_series.groupby(['time']).count() 
    time_series = time_series[['time', 'gender', 'username']]
    time_series = time_series.rename(columns={'username': 'tweets'})

    return time_series

def plot_trend(tweet_sample, title, filename):
    fig, ax = plt.subplots()    

    for gender, group in tweet_sample.groupby(['gender']):
        ax = group.plot(ax=ax, kind='line', x='time', y='tweets', label=gender)

    plt.legend(loc='best')
    fig.xlabel('Hours since start of sampling')
    fig.ylabel('Tweets')
    fig.title(title)
    fig.savefig(filename, figsize=(8,8))

def plot_homophily(tweet_sample, title, filename):
    compare_with = ['Male', 'Female']
    homophily_labels = []
    homophily_data = []    

    for gender, group in tweet_sample.groupby(['gender']):
        group_size = group.shape[0]

        for rt_gender in compare_with:
            homophily_rating = group[group.original_poster_gender == rt_gender].size  / group_size
            
            homophily_labels.append(f'{gender}/{rt_gender}')
            homophily_data.append(homophily_rating)
    
     plt.bar(homophily_data, labels=homophily_labels)
     plt.ylabel('Homophily rating')
     plt.title(title)
     plt.savefig(filename, figsize=(8,8))

def main():
    random_sample = pd.read_csv('random_sample.tsv', sep='\t')
    filtered_sample = pd.read_csv('filtered_sample.tsv', sep='\t')
    
    random_sample = label_genders(random_sample)
    filtered_sample = label_genders(filtered_sample)
    
    random_trend = time_series(random_sample)
    filtered_trend = time_series(filtered_sample)

    plot_trend(random_trend, 'Randomly sampled tweets over time', 'random_trend.pdf')
    plot_trend(filtered_trend, 'Tweet containing the word "code" over time', 'filtered_trend.pdf')

    plot_homophily(random_sample, 'Gender homophily in randomly sampled tweets', 'random_homophily.pdf')
    plot_homophily(filtered_sample, 'Gender homophily in tweets containing the word "code"', 'filtered_homophily.pdf')

main()
