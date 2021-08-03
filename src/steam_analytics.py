import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt

KEYWORDS = ['wow', 'refugee', 'bald', 'asmon', 'eighth', 'cat girl', 'cat boy','milfina','uberdanger']
asmon_declare = '2021/06/12'
asmon_stream = '2021/07/03'

# apply function for determining whether a string as asmongold-related keywords
def asmon_relevant(string, keywords):
    pat = '|'.join(keywords)
    try:
        return bool(re.search(pat, string.lower().strip()))
    except:
        return False
    
# perform keyword search on data
def find_asmon_reviews(data, keywords=KEYWORDS):
    data['is_relevant'] = data.copy()['review'].apply(asmon_relevant, keywords=keywords)
    return data

# function to generate graph for number of relevant 
def generate_relevancy_graph(data, smooth = False, N = 2):
    data = find_asmon_reviews(data)
    series = data[['timestamp_created', 'is_relevant']].groupby('timestamp_created').mean()
    asmon_declare_idx = series.index.get_loc(asmon_declare)
    asmon_stream_idx = series.index.get_loc(asmon_stream)
    title = 'Asmongold relevance over time'
    if smooth:
        # if MA smoothing required, create convolution filter for MA
        conv_filter = np.ones(N)/N
        # convolve, using mode same because we only care about vector of the left
        series['is_relevant'] = np.convolve(series['is_relevant'].values,conv_filter, mode='same')
        # change title for MA version
        title = f'Asmongold relevance over time with {N} moving average'
        
    # plot the series, pandas cleans the xticks for us so using their plot method wrapper
    ax = series.plot(kind='line', figsize=(15,14))
    # plot v line for when asmon started streaming ffxiv
    ax.axvline(asmon_declare_idx, label = 'asmon declared streaming plan', color = 'orange')
    ax.axvline(asmon_stream_idx, label = 'asmon started streaming', color = 'red')
    ax.set_xlabel('date')
    ax.set_ylabel('occurences')
    ax.legend()
