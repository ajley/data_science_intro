
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[1]:

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[2]:

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada',
          'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland',
          'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois',
          'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho',
          'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin',
          'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam',
          'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas',
          'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri',
          'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana',
          'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida',
          'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico',
          'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire',
          'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[3]:

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ],
    columns=["State", "RegionName"]  )

    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''

    raw = pd.read_csv('university_towns.txt',sep='\r\n',header=None)
    raw['State'] = raw[0].str.replace(r'\[edit\]$', '').where(raw[0].str.endswith(r'[edit]')).ffill()
    raw['RegionName'] = raw[0].str.replace(r'\ \(.*$', '')
    raw = raw[(raw[0].str.endswith(r'[edit]')) == False]
    result = raw.drop(0, axis= 1)
    return result.reset_index(drop=True)

get_list_of_university_towns()


# In[4]:

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    rawgdp = pd.read_excel('gdplev.xls',skiprows=220,header=None,parse_cols=[4,5,6])
    rawgdp.columns = ['quarter','GDP - Current','GDP - 2009 Dollars']
    results = rawgdp[(rawgdp['GDP - Current'] > rawgdp['GDP - Current'].shift(-1)) 
                     & (rawgdp['GDP - Current'].shift(-1) > rawgdp['GDP - Current'].shift(-2))]
    result = results[:1]['quarter'].to_string(index=False)
    return result

get_recession_start()


# In[5]:

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    rawgdp = pd.read_excel('gdplev.xls',skiprows=220,header=None,parse_cols=[4,5,6])
    rawgdp.columns = ['quarter','GDP - Current','GDP - 2009 Dollars']
    results = rawgdp[(rawgdp['GDP - Current'].shift(2) < rawgdp['GDP - Current'].shift(3)) 
                     & (rawgdp['GDP - Current'] > rawgdp['GDP - Current'].shift(1)) 
                     & (rawgdp['GDP - Current'].shift(1) > rawgdp['GDP - Current'].shift(2))]
    result = results[-1:]['quarter'].to_string(index=False)
    return result

get_recession_end()


# In[6]:

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    rawgdp = pd.read_excel('gdplev.xls',skiprows=220,header=None,parse_cols=[4,5,6])
    rawgdp.columns = ['quarter','GDP - Current','GDP - 2009 Dollars']
    start = rawgdp.loc[rawgdp['quarter'] == get_recession_start()].index.tolist()
    end = rawgdp.loc[rawgdp['quarter'] == get_recession_end()].index.tolist()
    results = rawgdp[start[0]:end[0]].sort('GDP - Current')
    return results[:1]['quarter'].to_string(index=False)

get_recession_bottom()


# In[25]:

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    raw = pd.read_csv('City_Zhvi_AllHomes.csv')
    years = [i for i in range(2000,2017)]
    months = [i for i in range(1,13)]
    cols = []
    for year in years:
        for month in months:
            cols.append('{0}-{1:0>2}'.format(year,month))
    
    #must be a better way then this rename and map
    raw.rename(columns = {'State':'StateAb'}, inplace = True)
    raw['State'] = raw['StateAb'].map(states)
   
    raw = raw.set_index(['State','RegionName'])
    raw_cut_down = raw[raw.columns.intersection(cols)]
    quarters = {'q1': [1,2,3],'q2': [4,5,6],'q3': [7,8,9],'q4':[10,11,12]}
    cols_to_keep = []
    for year in years:
        for key, value in quarters.items():
            new_col = str(year)+key
            cols_to_keep.append(new_col)
            cols_to_mean = []
            for m in value:
                cols_to_mean.append('{0}-{1:0>2}'.format(year,m))   
            raw_cut_down[new_col] = raw_cut_down[raw_cut_down.columns.intersection(cols_to_mean)].mean(axis=1)
    results = raw_cut_down[raw_cut_down.columns.intersection(cols_to_keep)]
    results = results.drop('2016q4',axis=1)
    
    return results

convert_housing_data_to_quarters()


# In[24]:

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    #grab mean house prices by quarter
    all_set = convert_housing_data_to_quarters()
    #grab start quarter for the recession
    recession_start = get_recession_start()
    #grab the recession bottom
    recession_bottom = get_recession_bottom()
    #don't need this but bring throuhg anyway
    recession_end = get_recession_end()
    #prune all_set down to the columns we're interested in
    quarters= all_set[[recession_start,recession_bottom,recession_end]]
    #add in the ratio - using .div() syntax takes care of NaN values
    quarters['ratio'] = quarters[recession_start].div(quarters[recession_bottom])
    
    #merge to grab university towns using inner join
    uni_towns = pd.merge(quarters,get_list_of_university_towns(),how='inner',left_index=True,right_on=['State','RegionName'])
    
    #index uni_towns to match index on quarters
    uni_towns = uni_towns.set_index(['State','RegionName'])
    
    # prune quarters down to non-uni towns by comparing indexes of quarters and uni towns, bring through the non-matching
    non_uni_towns = quarters[~quarters.index.isin(uni_towns.index)] 
    
    # run the ttest
    stat, pvalue = ttest_ind(uni_towns.dropna()['ratio'],non_uni_towns.dropna()['ratio'],axis=0)
  
    # basic logic to return expected values
    if pvalue < 0.01:
        different = True
        better = 'university town'
    else:
        different = False
        better = 'non-university town'
    
    return different, pvalue, better

run_ttest()


# In[ ]:



