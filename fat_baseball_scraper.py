
# coding: utf-8

# In[2]:


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


# In[22]:


df_stats = pd.read_csv('player_hw.csv', index_col = 0)


# In[23]:


df_stats['car_length'] = df_stats['lastyear'] - df_stats['firstyear']


# In[24]:


df_stats.info()


# In[25]:


df_stats = df_stats[df_stats.weight != 'Unknown']


# In[26]:


df_stats.weight = df_stats.weight.astype('int64')


# In[27]:


df_stats.corr()


# In[28]:


df_stats = df_stats[df_stats['firstyear'] > 1959]


# In[29]:


df_stats.corr()


# In[30]:


df_stats = df_stats[df_stats['lastyear'] != 2018]


# In[31]:


df_stats.corr()


# In[32]:



def inches(x):
    x = x.replace('½','')
    f_i = re.split('-', x)
    feet = int(f_i[0]) * 12
    inches = int(f_i[1])
    height = feet + inches
    return height


# In[33]:


df_stats['height'] = df_stats.height.apply(inches)


# In[34]:


df_stats['bmi'] = (df_stats['weight'] / df_stats['height'] / df_stats['height']) * 703


# In[35]:


df_stats = df_stats.sort_values('bmi', ascending = False).reset_index(drop = True)


# In[36]:


df_stats[df_stats['name'].str.contains('Colon')]


# In[37]:


df_stats.sort_values('car_length', ascending = False)


# In[38]:


df_pitchers = df_stats[df_stats['primary_pos'] == 'P']


# In[39]:


df_pitchers.corr()


# In[40]:


df_p_obese = df_pitchers[df_pitchers['bmi'] > 30]


# In[41]:


df_p_obese.car_length.mean()


# In[42]:


df_p_obese.car_length.hist()


# In[43]:


df_p_fit = df_pitchers[df_pitchers['bmi'] <= 30]


# In[44]:


df_p_fit.car_length.hist()


# In[45]:


df_p_fit.car_length.mean()


# In[46]:


df_pitchers.reset_index(drop = True, inplace = True)


# In[47]:


df_pitchers


# In[48]:


stats.ttest_ind(df_p_fit.car_length, df_p_obese.car_length, equal_var = False)


# In[49]:


df_matcher = pd.read_csv('~/Downloads/people.csv')[['name_first', 'name_last', 'key_fangraphs']]


# In[50]:


df_matcher.columns


# In[51]:


df_matcher['name'] = (df_matcher['name_first'] + ' ' + df_matcher['name_last'])


# In[52]:


df_matcher['name']


# In[53]:


df_matched = pd.merge(df_matcher, df_pitchers, how = 'outer', on = 'name').dropna(subset = ['height'])


# In[54]:


df_pitchers


# In[55]:


df_matched.dropna(subset = ['height', 'name_first', 'key_fangraphs'], inplace = True)


# In[56]:


df_matched.reset_index(drop = True, inplace = True)


# In[57]:


df_matched[df_matched.name_last == 'Pichardo']


# In[58]:


df_matched


# In[59]:


df_duped= df_matched[df_matched['name'].duplicated(keep = False)]


# In[60]:


df_duped.drop_duplicates(subset = ['name', 'firstyear', 'lastyear'])


# In[61]:



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
                        'name': name
                    })
    df_player = pd.DataFrame(df_list)
    
    df_player = df_player[~df_player['team'].str.contains('Depth Charts|Steamer|Fans|Zips|ZiPS|- - -')]
    
    df_player = df_player.drop_duplicates(subset = ['name','year'], keep = 'first').reset_index(drop = True)
    
    df_player.war = pd.to_numeric(df_player.war, errors = 'coerce')


# In[62]:


df_list = []
for name, key, n in zip(df_matched.name[3377:], df_matched.key_fangraphs[3377:], range(0, len(df_matched))):
    print(name)
    print(str(n) + '/' + str(len(df_matched)))
    war_scraper(name, key)


# In[ ]:


df_player_saved = pd.concat([df_player_saved, df_player])


# In[63]:


df_player


# In[64]:


df_player_saved.to_csv('pitcher_war.csv')


# In[307]:


df_player_saved.to_csv('~/Downloads/pitcher_war.csv')


# In[155]:


df_player.war = pd.to_numeric(df_player.war, errors = 'coerce')


# In[3]:


df_pwar = pd.read_csv('pitcher_war.csv', index_col = 0)


# In[4]:


df_pwar


# In[65]:


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


# In[66]:


df_pwar


# In[ ]:


for n in df_pwar.name.unique():
    drop_duplicate_players(n)


# In[ ]:


df_pwar.year = df_pwar.year.astype(int)


# In[9]:


df_pwar[df_pwar.year < 1960]


# In[10]:


df_combined = pd.merge(df_pwar, df_pitchers, on = 'name', how = 'outer').drop(['firstyear', 'lastyear', 'primary_pos', 'car_length', 'url'], axis = 1)


# In[11]:


df_combined['yoc'] = np.NaN


# In[196]:


for p in df_combined.name.unique():
    df_p = df_combined[df_combined.name == p]
    df_p = df_p.reset_index()
    df_p['yoc'] = df_p.index
    df_p = df_p.set_index('index')
    for i, row in df_p.iterrows():
        
        df_combined.loc[i, ['yoc']] = (row['year'] - df_p.iloc[0, 3]) + 1
          


# In[197]:


df_combined


# In[198]:


df_co = df_combined[df_combined.bmi >= 30]


# In[199]:


len(df_co)


# In[200]:


df_sv = df_combined[df_combined.bmi < 30]


# In[202]:


len(df_sv)


# In[220]:


df_sv.yoc.max()


# In[275]:


one = []
two = []
three = []
four = []
five = []
six=[]
seven=[]
eight=[]
nine=[]
ten=[]
eleven=[]
twelve=[]
thirteen=[]
fourteen=[]
fifteen=[]
sixteen=[]
seventeen = []
eighteen = []
nineteen = []
twenty = []


# In[286]:


players_one = 0
players_two = 0
players_three = 0
players_four = 0
players_five = 0
players_six = 0
players_seven = 0
players_eight = 0
players_nine = 0
players_ten = 0
players_eleven = 0
players_twelve = 0
players_thirteen = 0
players_fourteen = 0
players_fifteen = 0
players_sixteen = 0
players_seventeen = 0
players_eighteen = 0
players_nineteen = 0
players_twenty = 0


# In[292]:


year_list = [one, two, three, four, five, six, seven, eight, nine, ten, eleven, twelve, thirteen, fourteen, fifteen, sixteen, seventeen]
players_list = [players_one, 
                players_two, 
                players_three, 
                players_five, 
                players_six, 
                players_seven, 
                players_eight,
                players_nine,
                players_ten,
                players_eleven,
                players_twelve,
                players_thirteen,
                players_fourteen,
                players_fifteen,
                players_sixteen,
                players_seventeen,
                players_eighteen,
                players_nineteen,
                players_twenty
               ]


# In[288]:


for i, row in df_sv.iterrows():
    
    if row['yoc'] == 1:
        one.append(row['war'])
        players_one += 1
        
    if row['yoc'] == 2:
        two.append(row['war'])
        players_two += 1
        
    if row['yoc'] == 3:
        three.append(row['war'])
        players_three += 1
        
    if row['yoc'] == 4:
        four.append(row['war'])
        players_four += 1
        
    if row['yoc'] == 5:
        five.append(row['war'])
        players_five += 1
        
    if row['yoc'] == 6:
        six.append(row['war'])
        players_six += 1
        
    if row['yoc'] == 7:
        seven.append(row['war'])
        players_seven += 1
        
    if row['yoc'] == 8:
        eight.append(row['war'])
        players_eight += 1
        
    if row['yoc'] == 9:
        nine.append(row['war'])
        players_nine += 1
        
    if row['yoc'] == 10:
        ten.append(row['war'])
        players_ten += 1
        
    if row['yoc'] == 11:
        eleven.append(row['war'])
        players_eleven += 1
        
    if row['yoc'] == 12:
        twelve.append(row['war'])
        players_twelve += 1
        
    if row['yoc'] == 13:
        thirteen.append(row['war'])
        players_thirteen += 1
        
    if row['yoc'] == 14:
        fourteen.append(row['war'])
        players_fourteen += 1
        
    if row['yoc'] == 15:
        fifteen.append(row['war'])
        players_fifteen += 1
        
    if row['yoc'] == 16:
        sixteen.append(row['war'])
        players_sixteen += 1
        
    if row['yoc'] == 17:
        seventeen.append(row['war'])
        players_seventeen += 1
        
    if row['yoc'] == 18:
        eighteen.append(row['war'])
        players_eighteen += 1
        
    if row['yoc'] == 19:
        nineteen.append(row['war'])
        players_nineteen += 1
        
    if row['yoc'] == 20:
        twenty.append(row['war'])
        players_twenty += 1


# In[289]:


sv_year_mean_list = []
for y in year_list:
    sv_year_mean_list.append(np.mean(y))


# In[290]:


players_one


# In[293]:


players_list


# In[294]:


for p in enumerate(players_list[1:]):
    print(p)
    drops = players_list[p[0]] - p[1]
    print(drops / players_list[0])


# In[227]:


co_year_mean_list


# In[229]:


sv_year_mean_list


# In[230]:


plt.plot(co_year_mean_list)
plt.plot(sv_year_mean_list)

