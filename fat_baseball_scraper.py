
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import re
import matplotlib.pyplot as plt
from scipy import stats
import time
get_ipython().run_line_magic('matplotlib', 'inline')
pd.options.display.max_columns = 500
pd.options.display.max_rows = 500


# In[2]:


r = requests.get('http://www.baseball-almanac.com/players/ballplayer.shtml')


# In[3]:


soup = BeautifulSoup(r.content, 'html.parser')


# In[4]:


BeautifulSoup.prettify(soup)


# In[5]:


td_tags = soup.find_all('td', {'class':'datacolBoxC'})


# In[6]:


td_tags_yellow = soup.find_all('td', {'class': 'datacolBoxYellowC'})


# In[7]:


td_tags_yellow


# In[8]:


link_list = []
for td in td_tags:
    if td.find('a') is None:
        print('NONE')
    else:
        url = td.find('a').get('href')
        if 'shtml' in url:
            link_list.append(url)


# In[9]:


for td in td_tags_yellow:
    if td.find('a') is None:
        print('NONE')
    else:
        url = td.find('a').get('href')
        if 'shtml' in url:
            link_list.append(url)


# In[10]:


link_list = sorted(link_list)


# In[11]:


link_list[0]


# In[12]:


player_list = []
for l in link_list:
    print(l, len(link_list))
    c = requests.get('http://www.baseball-almanac.com/players/' + l).content
    soup = BeautifulSoup(c)
    td_tags = soup.find_all('td', {'class':'datacolBox'})
    for td in td_tags:   
        if 'href' in str(td):
            player_url = td.find('a').get('href')
            player_name = td.find('a').get_text().strip()
            player_list.append({'url':player_url,
                                'name':player_name})


# In[ ]:


df_players = pd.DataFrame(player_list)


# In[ ]:


df_players


# In[ ]:


c = requests.get('http://www.baseball-almanac.com/players/player.php?p=abadfe01').content
soup = BeautifulSoup(c)

tables = soup.find_all('table', {'class':'boxed'})
for t in tables:
    if 'Totals' in str(t):
        print('this one')
        table = t

t_list = table.find_all('td', {'class' : 'datacolC'})
for td in t_list:
    if 'Totals' in str(td):
        pp = td.text.strip(' Totals')


# In[ ]:


height_list = []
weight_list = []
name_list = []
url_list = []
firstyear_list = []
lastyear_list = []
pos_list = []
for i, row in df_players.iterrows():    
    print(str(i) + '/' + str(len(df_players)))
    c = requests.get('http://www.baseball-almanac.com/players/' + row['url']).content

    soup = BeautifulSoup(c)

    td_tags = soup.find_all('td', {'class':'biocolpad'})


    for i, td in enumerate(td_tags):
        if 'Height' in str(td):
            reference = i
            height_i = reference + 1

        if 'Weight' in str(td):
            weight_i = i + 1

    height = td_tags[height_i].get_text().strip()
    height_list.append(height)

    weight = td_tags[weight_i].get_text().strip()
    weight_list.append(weight)
    
    url_list.append(row['url'])
    name_list.append(row['name'])
    
    
#     grab first and last year
    tables = soup.find_all('table', {'class':'boxed'})

    r_list = []
    for t in tables:
        r = t.find_all('td', {'class':'datacolBoxC'})
        for td in r:
            r_list.append(td)

    del r_list[-1]

    year_list = []
    for r in r_list:
        if len(r.text) > 3:
            year_list.append(int(r.text))
    firstyear_list.append(year_list[0])
    lastyear_list.append(year_list[-1])
    

#     grab primary position
    for t in tables:
        if 'Totals' in str(t):
            table = t

    t_list = table.find_all('td', {'class' : 'datacolC'})
    for td in t_list:
        if 'Totals' in str(td):
            pp = td.text.strip(' Totals')
    pos_list.append(pp)



    


# In[ ]:



df_h_w = pd.DataFrame(
{
    'height':height_list,
    'weight':weight_list,
    'url':url_list,
    'name':name_list,
    'firstyear':firstyear_list,
    'lastyear':lastyear_list,
    'primary_pos': pos_list
         }
)


# In[ ]:


df_h_w


# In[ ]:


df_h_w.to_csv('player_hw.csv')


# In[4]:


df_stats = pd.read_csv('~/fat_baseball/player_hw.csv', index_col = 0)


# In[5]:


df_stats['car_length'] = df_stats['lastyear'] - df_stats['firstyear']


# In[6]:


df_stats.info()


# In[7]:


df_stats = df_stats[df_stats.weight != 'Unknown']


# In[8]:


df_stats.weight = df_stats.weight.astype('int64')


# In[9]:


df_stats.corr()


# In[10]:


df_stats = df_stats[df_stats['firstyear'] > 1959]


# In[11]:


df_stats.corr()


# In[12]:


df_stats = df_stats[df_stats['lastyear'] != 2018]


# In[13]:


df_stats.corr()


# In[14]:



def inches(x):
    x = x.replace('½','')
    f_i = re.split('-', x)
    feet = int(f_i[0]) * 12
    inches = int(f_i[1])
    height = feet + inches
    return height


# In[15]:


df_stats['height'] = df_stats.height.apply(inches)


# In[16]:


df_stats['bmi'] = (df_stats['weight'] / df_stats['height'] / df_stats['height']) * 703


# In[17]:


df_stats = df_stats.sort_values('bmi', ascending = False).reset_index(drop = True)


# In[18]:


df_stats[df_stats['name'].str.contains('Colon')]


# In[19]:


df_stats.sort_values('car_length', ascending = False)


# In[20]:


df_pitchers = df_stats[df_stats['primary_pos'] == 'P']


# In[21]:


df_pitchers.corr()


# In[31]:


df_p_obese = df_pitchers[df_pitchers['bmi'] > 30]


# In[32]:


df_p_obese.car_length.mean()


# In[33]:


df_p_obese.car_length.hist()


# In[34]:


df_p_fit = df_pitchers[df_pitchers['bmi'] <= 30]


# In[35]:


df_p_fit.car_length.hist()


# In[36]:


df_p_fit.car_length.mean()


# In[37]:


df_pitchers.reset_index(drop = True, inplace = True)


# In[38]:


df_pitchers


# In[39]:


stats.ttest_ind(df_p_fit.car_length, df_p_obese.car_length, equal_var = False)


# In[45]:


df_matcher = pd.read_csv('~/Downloads/people.csv')[['name_first', 'name_last', 'key_fangraphs']]


# In[46]:


df_matcher.columns


# In[47]:


df_matcher['name'] = (df_matcher['name_first'] + ' ' + df_matcher['name_last'])


# In[48]:


df_matcher['name']


# In[49]:


df_matched = pd.merge(df_matcher, df_pitchers, how = 'outer', on = 'name').dropna(subset = ['height'])


# In[50]:


df_pitchers


# In[51]:


df_matched.dropna(subset = ['height', 'name_first', 'key_fangraphs'], inplace = True)


# In[52]:


df_matched.reset_index(drop = True, inplace = True)


# In[53]:


df_matched[df_matched.name_last == 'Pichardo']


# In[54]:


df_matched


# In[55]:


df_duped= df_matched[df_matched['name'].duplicated(keep = False)]


# In[60]:


df_duped.drop_duplicates(subset = ['name', 'firstyear', 'lastyear'])


# In[57]:


f = requests.get('https://www.fangraphs.com/statss.aspx?playerid=13801.0')
    
f_soup = BeautifulSoup(f.content.decode('utf-8'), 'html.parser')

tables = f_soup.find_all('table', {'class': 'rgMasterTable', 'id': 'SeasonStats1_dgSeason11_ctl00'})

war_table = tables[0]

trs = war_table.find_all('tr')

for tr in trs:

    if tr:
        tds = tr.find_all('td')


# In[58]:


tds


# In[60]:



def war_scraper(name, player_id):
    global df_player
    
    f = requests.get('https://www.fangraphs.com/statss.aspx?playerid={}'.format(player_id))
    
    f_soup = BeautifulSoup(f.content.decode('utf-8'), 'html.parser')

    tables = f_soup.find_all('table', {'class': 'rgMasterTable', 'id': 'SeasonStats1_dgSeason11_ctl00'})

    war_table = tables[0]

    trs = war_table.find_all('tr')

    for tr in trs:

        if tr:
            tds = tr.find_all('td')
            if tds:
                if tds[-1].text != '\xa0': 
                    df_list.append(
                    {
                        'year': tds[0].text,
                        'war': tds[-1].text,
                        'team': tds[1].text,
                        'name': name,
                        'games': tds[5].text,
                        'gs': tds[6].text
                    })



# In[ ]:


#df_list = []
for name, key, n in zip(df_matched.name[3059:], df_matched.key_fangraphs[3059:], range(0, len(df_matched))):
#    time.sleep(.25)
    print(name)
    print(str(n) + '/' + str(len(df_matched)))
    war_scraper(name, key)
    
#%%
df_matched[df_matched.name == 'Joe Nathan']
#%%
len(df_list)
#%%
df_player = pd.DataFrame(df_list)

df_player = df_player[~df_player['team'].str.contains('Depth Charts|Steamer|Fans|Zips|ZiPS|- - -')]

df_player = df_player.drop_duplicates(subset = ['name','year'], keep = 'first').reset_index(drop = True)

df_player.war = pd.to_numeric(df_player.war, errors = 'coerce')

#%% 
df_player
#%% 

df_player_saved = pd.DataFrame()
df_player_saved = pd.concat([df_player_saved, df_player])


# In[63]:


df_player

#%%
df_player_saved.war = pd.to_numeric(df_player_saved.war, errors = 'coerce')
df_player_saved.games = pd.to_numeric(df_player_saved.games, errors = 'coerce')
df_player_saved.gs = pd.to_numeric(df_player_saved.gs, errors = 'coerce')


# In[64]:


df_player_saved.to_csv('pitcher_war.csv')


# In[307]:


df_player_saved.to_csv('~/Downloads/pitcher_war.csv')


# In[155]:




# In[59]:


df_pwar = pd.read_csv('~/fat_baseball/pitcher_war.csv', index_col = 0)


# In[31]:


#%%
df_pwar['gs'].astype(float, inplace = True, errors = 'ignore')
df_pwar['games'].astype(float, inplace = True, errors = 'ignore')

#%%
df_pwar['starter'] = np.where(df_pwar['gs'] / df_pwar['games'] >= 0.5, 'sp', 'rp')
# In[45]:


def drop_duplicate_players(player):
    global df_pwar
    
    print(player)

    df_player = df_pwar[df_pwar['name'] == player]

    df_player['year'] = df_player['year'].astype(int)

    df_player_years = df_matched[df_matched.name == player].iloc[0]

    years = range(int(df_player_years['firstyear']), int(df_player_years['lastyear'] + 1))



    drop_mask = df_player[~df_player.year.isin(years)]
    if drop_mask.empty == False:
        df_pwar = df_pwar.drop(drop_mask.index)


# In[46]:


df_pwar


# In[47]:


for n in df_pwar.name.unique():
    drop_duplicate_players(n)


# In[48]:


df_pwar.year = df_pwar.year.astype(int)


# In[49]:


df_pwar[df_pwar.year < 1960]


# In[136]:


df_combined = pd.merge(df_pwar, df_pitchers, on = 'name', how = 'outer').drop(['firstyear', 'lastyear', 'primary_pos', 'car_length', 'url'], axis = 1)


# In[137]:


df_combined['yoc'] = np.NaN


# In[138]:


df_combined[df_combined.name == 'Bob Malloy']


# In[139]:


df_combined.drop_duplicates(subset = ['name', 'yoc', 'year', 'war', 'team'], keep = False, inplace = True)


# In[140]:


df_combined = df_combined[~df_combined.name.str.contains('Dave Roberts|Henry Rodriguez')]


# In[141]:


df_yoc = df_combined

len(df_yoc)
# In[142]:


for p in df_yoc.name.unique():
    df_p = df_combined[df_combined.name == p]
    
    df_p = df_p.reset_index()
    df_p['yoc'] = df_p.index
    df_p = df_p.set_index('index')
    for i, row in df_p.iterrows():
        
        df_yoc.loc[i, ['yoc']] = (row['year'] - df_p.iloc[0, 5]) + 1
          


# In[143]:


df_yoc = df_yoc[df_yoc.yoc > 0]


# In[144]:


df_yoc.dropna(subset = ['yoc'], inplace = True)


# In[226]:


df_co = df_yoc[df_yoc.bmi >= 25]


# In[228]:


df_sv = df_yoc[df_yoc.bmi < 25]


# In[230]:


sv_year_counts = pd.DataFrame(df_sv.yoc.value_counts())


# In[231]:


co_year_counts = pd.DataFrame(df_co.yoc.value_counts())


# In[232]:


co_year_counts


# In[233]:


co_war = []
sv_war = []

# In[234]:


import math
def war_means(df, war_list):
    for i in df.yoc.unique():
        print(i)
        df_y = df[df.yoc == i]
        y_mean = df_y.war.mean()
        if math.isnan(y_mean):
            print(df_y, i)
        war_list.append(y_mean)
    return war_list


# In[235]:


co_war = war_means(df_co, co_war)


# In[236]:


sv_war = war_means(df_sv, sv_war)


# In[237]:

#sv_war = [x for x in sv_war if x > 0]
#sv_year_counts = [x for x in sv_year_counts if x > 0]
print(len(sv_war))
len(sv_year_counts)


# In[245]:


co_year_counts['war'] = co_war
sv_year_counts['war'] = sv_war


# In[248]:


co_year_counts = co_year_counts[co_year_counts.index > 0]
sv_year_counts = sv_year_counts[sv_year_counts.index > 0]

# In[249]:


sv_year_counts['ar'] = sv_year_counts['yoc'].pct_change()


# In[250]:


co_year_counts['ar'] = co_year_counts['yoc'].pct_change()


# In[251]:


co_year_counts


# In[260]:
sv_year_counts.reset_index(drop = True, inplace = True)
co_year_counts.reset_index(drop = True, inplace = True)

df_sv_plot = sv_year_counts.loc[:15]
df_co_plot = co_year_counts.loc[:15]


# In[261]:


plt.plot(df_sv_plot['ar'])
plt.plot(df_co_plot['ar'])


# In[262]:


plt.plot(df_sv_plot['war'])
plt.plot(df_co_plot['war'])

#%%
plt.legend()

#%%

#%%
df_yoc.reset_index(drop = True, inplace = True)

#%%
df_yoc.to_csv('full_data.csv')

#%%
df_yoc['last_year'] = np.nan
for i, row in df_yoc.iterrows():
    
    if row['name'] == df_yoc.loc[i, 'name']:
        df_yoc.loc['last_year'] = 'no'
    else:
        df_yoc.loc['last_year'] = 'yes'











