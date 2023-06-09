## Run selenium and chrome driver to scrape data from cloudbytes.dev
import time
import os.path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime
# Set up Chrome options
chrome_options = Options()
chrome_options.headless = True  # Ensure GUI is off

# Set up Chrome webdriver service
homedir = os.path.expanduser("~")
webdriver_service = Service(f"{homedir}/ao3lockwood-co/chromedriver")

# Initialize Chrome browser
browser = webdriver.Chrome(service=webdriver_service, options=chrome_options)
def get_links(browser):
    # Find all the works using XPath
    works = browser.find_elements(By.XPATH, '//ol[2]/li')

    # Iterate through each work and extract author and datetime
    data = []
    for work in works:
        h4 = work.find_element(By.TAG_NAME, 'h4')
        a = h4.find_elements(By.TAG_NAME, 'a')
        # Get the href attribute of the first <a> tag
        link = a[0].get_attribute("href")
        data.append(link)

    return data
def check_list_inclusion(list1, list2):
    # Check if all items in list1 are present in list2
    return all(item in list2 for item in list1)
def process_tv_book(category, new_links, links):
    for page in range(1, 20):
        print(f'Processing page {page} of {category}')
        if category == 'tv':
            link = f'https://archiveofourown.org/tags/Lockwood%20*a*%20Co*d*%20(TV)/works?commit=Sort+and+Filter&exclude_work_search[fandom_ids][]=1250871&page={page}&work_search[complete]=&work_search[crossover]=&work_search[date_from]=&work_search[date_to]=&work_search[excluded_tag_names]=&work_search[language_id]=&work_search[other_tag_names]=&work_search[query]=&work_search[sort_column]=created_at&work_search[words_from]=&work_search[words_to]='
        elif category == 'book':
            link = f'https://archiveofourown.org/tags/Lockwood%20*a*%20Co*d*%20-%20Jonathan%20Stroud/works?commit=Sort+and+Filter&page={page}&work_search%5Bcomplete%5D=&work_search%5Bcrossover%5D=&work_search%5Bdate_from%5D=&work_search%5Bdate_to%5D=&work_search%5Bexcluded_tag_names%5D=&work_search%5Blanguage_id%5D=&work_search%5Bother_tag_names%5D=&work_search%5Bquery%5D=&work_search%5Bsort_column%5D=created_at&work_search%5Bwords_from%5D=&work_search%5Bwords_to%5D='
        
        time.sleep(10)
        browser.get(link)
        temp_links = get_links(browser)
        
        if check_list_inclusion(temp_links, links):
            break
        else:
            new_links += temp_links
    
    return new_links
def process_pages(links):
    new_links = []
    
    # Process TV pages
    new_links = process_tv_book('tv', new_links, links)
    
    # Process book pages
    new_links = process_tv_book('book', new_links, links)
    
    # Remove duplicates
    new_links = list(set(new_links))
    
    # Create a new DataFrame
    data = pd.DataFrame(columns=['link','title','author','published','updatedate','chapters','language','words','kudos','comments','bookmarks','hits','warning','relationship','characters','tags','summary','rating','series'])
    
    # Assign new links to the 'link' column
    data['link'] = new_links
    
    return data
def get_data(data):
    counter=0
    slow_links = [] # List to store links that are taking too long to access
    for x in range(len(data['link'])):
        start_time = time.time()
        if pd.isnull(data.loc[x,'summary']):
            print(f"getting missing data {x+1}/{len(data['link'])}")
            try:
                newlink=data['link'][x]+'?view_adult=true'
                page_start_time=time.time()
                source = requests.get(newlink, headers={
                              'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}).text
                elapsed_time = time.time() - page_start_time
                if elapsed_time > 10:
                    print(f"Link {data['link'][x]} is taking too long to access. Adding to slow_links list.")
                    slow_links.append(data['link'][x])
                    continue
            except requests.exceptions.RequestException:
                print(f"Link {data['link'][x]} is taking too long to access. Adding to slow_links list.")
                slow_links.append(data['link'][x])
                continue
            soup = BeautifulSoup(source,'html.parser')
            try:
                data.loc[x,'title']=soup.find('h2', attrs={'class':'title heading'}).get_text().replace('\n','').strip()
            except:
                data.loc[x,'title']=np.nan
            try:
                data.loc[x,'author']=soup.find('a', attrs={'rel':'author'}).get_text()
            except:
                data.loc[x,'author']="Anonymous"
            try:
                data.loc[x,'published']=soup.find('dd', attrs={'class':'published'}).get_text()
            except:
                data.loc[x,'published']=np.nan
            try:
                data.loc[x,'updatedate'] = soup.find('dd', attrs={'class':'status'}).get_text()
            except:
                data.loc[x,'updatedate']=data['published'][x]
            
            try:
                data.loc[x,'chapters']=soup.find('dd', attrs={'class':'chapters'}).get_text()
            except:
                data.loc[x,'chapters']=np.nan
            
            try:
                data.loc[x,'language']=soup.find('dd', attrs={'class':'language'}).get_text().replace('\n','').strip()
            except:
                data.loc[x,'language']=np.nan
            
            try:
                data.loc[x,'words']=soup.find('dd', attrs={'class':'words'}).get_text()
            except:
                data.loc[x,'words']=np.nan
            try:
                data.loc[x,'kudos']=soup.find('dd', attrs={'class':'kudos'}).get_text()
            except:
                data.loc[x,'kudos']=0
            try:
                data.loc[x,'comments']=soup.find('dd', attrs={'class':'comments'}).get_text()
            except:
                data.loc[x,'comments']=0
            try:
                data.loc[x,'bookmarks']=soup.find('dd', attrs={'class':'bookmarks'}).get_text()
            except:
                data.loc[x,'bookmarks']=0
            try:
                data.loc[x,'hits']=soup.find('dd', attrs={'class':'hits'}).get_text()
            except:
                data.loc[x,'hits']=0
            
            try:
                data.loc[x,'warning']=soup.find('dd', attrs={'class':'warning tags'}).get_text().replace('\n','').strip()
            except:
                data.loc[x,'warning']=0
            try:
                r = soup.find('dd', attrs={'class':'relationship tags'})
                relationships = r.find_all('li')
                rel_list = []
                for rel in relationships:
                    rel_list.append(rel.get_text().strip())
                data.loc[x,'relationship'] = ', '.join(rel_list)
            except:
                data.loc[x,'relationship'] = ''
            try:
                c = soup.find('dd', attrs={'class':'character tags'})
                characters = c.find_all('li')
                char_list = []
                for char in characters:
                    char_list.append(char.get_text().strip())
                data.loc[x,'characters'] = ', '.join(char_list)
            except:
                data.loc[x,'characters']=''
            try:
                t = soup.find('dd', attrs={'class':'freeform tags'})
                tags = t.find_all('li')
                tag_list = []
                for tag in tags:
                    tag_list.append(tag.get_text().strip())
                data.loc[x,'tags'] = ', '.join(tag_list)
            except:
                data.loc[x,'tags'] = ''
            try:
                data.loc[x,'series'] = soup.find('span', attrs={'class':'position'}).get_text().replace('\n','').strip()
            except:
                data.loc[x,'series'] = 'not a series'
            try:
                data.loc[x,'summary']=soup.find('div', attrs={'class':'summary module'}).get_text().replace('\n', ' ').replace('Summary:','').strip()
            except:
                data.loc[x,'summary']=np.nan
            
            try:
                data.loc[x,'rating']=soup.find('dd', attrs={'class':'rating tags'}).get_text().replace('\n','').strip()
            except:
                data.loc[x,'rating']=np.nan
            print(data.iloc[x])
            time.sleep(10)
        elapsed_total_time = time.time() - start_time
        if elapsed_total_time > 120*60:
            for l in slow_links:
                print(l)
            return data
    for l in slow_links:
        print(l)
    return pd.DataFrame(data)


def update_data(data):
    slow_links = []  # List to store links that are taking too long to access

    for x in range(len(data['link'])):
        start_time = time.time()
        print(f"updating data {x+1}/{len(data['link'])}")

        try:
            # Add query parameter to link
            newlink = data['link'][x] + '?view_adult=true'
            page_start_time = time.time()
            source = requests.get(newlink, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}).text
            elapsed_time = time.time() - page_start_time

            if elapsed_time > 10:
                print(f"Link {data['link'][x]} is taking too long to access. Adding to slow_links list.")
                slow_links.append(data['link'][x])
                continue

        except requests.exceptions.RequestException:
            print(f"Link {data['link'][x]} is taking too long to access. Adding to slow_links list.")
            slow_links.append(data['link'][x])
            continue

        soup = BeautifulSoup(source, 'html.parser')

        try:
            data.loc[x, 'updatedate'] = soup.find('dd', attrs={'class': 'status'}).get_text()
        except:
            data.loc[x, 'updatedate'] = data['published'][x]

        try:
            data.loc[x, 'chapters'] = soup.find('dd', attrs={'class': 'chapters'}).get_text()
        except:
            data.loc[x, 'chapters'] = np.nan

        try:
            data.loc[x, 'words'] = soup.find('dd', attrs={'class': 'words'}).get_text()
        except:
            data.loc[x, 'words'] = np.nan

        try:
            data.loc[x, 'kudos'] = soup.find('dd', attrs={'class': 'kudos'}).get_text()
        except:
            data.loc[x, 'kudos'] = 0

        try:
            data.loc[x, 'comments'] = soup.find('dd', attrs={'class': 'comments'}).get_text()
        except:
            data.loc[x, 'comments'] = 0

        try:
            data.loc[x, 'bookmarks'] = soup.find('dd', attrs={'class': 'bookmarks'}).get_text()
        except:
            data.loc[x, 'bookmarks'] = 0

        try:
            data.loc[x, 'hits'] = soup.find('dd', attrs={'class': 'hits'}).get_text()
        except:
            data.loc[x, 'hits'] = 0

        try:
            data.loc[x, 'warning'] = soup.find('dd', attrs={'class': 'warning tags'}).get_text().replace('\n', '').strip()
        except:
            data.loc[x, 'warning'] = 0

        try:
            r = soup.find('dd', attrs={'class': 'relationship tags'})
            relationships = r.find_all('li')
            rel_list = [rel.get_text().strip() for rel in relationships]
            data.loc[x, 'relationship'] = ', '.join(rel_list)
        except:
            data.loc[x, 'relationship'] = ''

        try:
            c = soup.find('dd', attrs={'class': 'character tags'})
            characters = c.find_all('li')
            char_list = [char.get_text().strip() for char in characters]
            data.loc[x, 'characters'] = ', '.join(char_list)
        except:
            data.loc[x, 'characters'] = ''

        try:
            t = soup.find('dd', attrs={'class': 'freeform tags'})
            tags = t.find_all('li')
            tag_list = [tag.get_text().strip() for tag in tags]
            data.loc[x, 'tags'] = ', '.join(tag_list)
        except:
            data.loc[x, 'tags'] = ''

        try:
            data.loc[x, 'rating'] = soup.find('dd', attrs={'class': 'rating tags'}).get_text().replace('\n', '').strip()
        except:
            data.loc[x, 'rating'] = np.nan

        print(data.iloc[x])
        time.sleep(10)
        elapsed_total_time = time.time() - start_time

    if elapsed_total_time > 120 * 60:
        for l in slow_links:
            print(l)
        return data

    for l in slow_links:
        print(l)
    return pd.DataFrame(data)

# Original date string
dt_string = '20230602_0121'

# Construct the filename using f-string
filename = f'ao3_lockwood_and_co_ao_{dt_string}.csv'

# Read the previous DataFrame from the specified file path
prev_df = pd.read_csv(f'AO3/{filename}')

# Assign the previous DataFrame to the working DataFrame
working_df = prev_df

# Get the current date and time
now = datetime.now()

# Format the current date and time as a string
dt_string = now.strftime("%Y%m%d_%H%M")
print("date and time =", dt_string)

# Select specific columns in the working DataFrame
columns_to_keep = ['link', 'title', 'author', 'published', 'updatedate', 'chapters', 'language', 'words',
                   'kudos', 'comments', 'bookmarks', 'hits', 'warning', 'relationship', 'characters', 'tags',
                   'summary', 'rating', 'series']
working_df = working_df[columns_to_keep]

# Update the data in the working DataFrame (assuming the "update_data" function is defined elsewhere)
working_df = update_data(working_df)

new_df = process_pages(working_df['link'])
new_df = get_data(new_df)
working_df = pd.concat([new_df, working_df])

# Remove duplicate rows based on the 'link' column
working_df = working_df.drop_duplicates(subset=['link'])

# Generate the filename using the current date and time
filename = f'ao3_lockwood_and_co_ao_{dt_string}'

# Save the modified dataframe to a CSV file
working_df.to_csv(f'AO3/{filename}.csv', index=False)

# Open the file in read mode
working_df = pd.read_csv(f'AO3/{filename}.csv')

# Split the chapter column into chapter and chapter_max
working_df[['chapter', 'chapter_max']] = working_df['chapters'].str.split("/", expand=True)

# Create a completion column based on the chapter and chapter_max values
working_df['completion'] = working_df.apply(lambda row: 'completed' if row['chapter'] == row['chapter_max'] else 'incomplete', axis=1)

# Convert 'published' and 'updatedate' columns to datetime
working_df['published'] = pd.to_datetime(working_df['published'])
working_df['updatedate'] = pd.to_datetime(working_df['updatedate'])

# Find the maximum value of 'updatedate' and assign it to 'currentdate' column
working_df['currentdate'] = working_df['updatedate'].max()

# Calculate the difference in days between 'currentdate' and 'published' columns
working_df['datediff_pub'] = (working_df['currentdate'] - working_df['published']).dt.days

# Calculate the difference in days between 'currentdate' and 'updatedate' columns
working_df['datediff'] = (working_df['currentdate'] - working_df['updatedate']).dt.days

def classify(row):
    if row['chapter_max'] == '1':
        return 'oneshot'
    elif row['completion'] == 'completed':
        return 'multichapter(complete)'
    elif row['datediff'] <= 60:
        return 'multichapter(updating)'
    else:
        return 'multichapter(dormant)'

working_df['classification'] = working_df.apply(classify, axis=1)

def get_num_item(column):
    items = []  # Renamed 'item' to 'items' for clarity
    
    for row in column:
        try:
            row_item = row.replace("[", "").replace("]", "").replace("'", "").replace('"', '').split(",")
        except:
            row_item = ['']  # If an exception occurs, assign an empty list to 'row_item'
        
        if row_item != ['']:
            items.append(len(row_item))
        else:
            items.append(0)
    
    return items

# Group the 'working_df' DataFrame by 'author' and aggregate the columns
author_df = working_df.groupby('author', as_index=False).agg(
    lastauthorupdate=('updatedate', 'max'),
    firstauthorupdate=('published', 'min')
)
# Check if 'firstauthorupdate_x' column exists in working_df
if 'firstauthorupdate_x' in working_df.columns:
    # Drop unnecessary columns from working_df
    columns_to_drop = ['firstauthorupdate_x', 'lastauthorupdate_x', 'lastauthorupdate_y', 'firstauthorupdate_y']
    working_df = working_df.drop(columns=columns_to_drop)

# Merge working_df with author_df using 'author' as the key column
working_df = working_df.merge(author_df, how='left', on='author')


# Calculate the time difference between 'currentdate' and 'lastauthorupdate'
working_df['author_lastupdate_diff'] = (working_df['currentdate'] - working_df['lastauthorupdate']).dt.days

# Calculate the time difference between 'lastauthorupdate' and 'firstauthorupdate'
working_df['daysactive'] = (working_df['lastauthorupdate'] - working_df['firstauthorupdate']).dt.days

# Calculate the time difference between 'currentdate' and 'firstauthorupdate'
working_df['daysincefirtupload'] = (working_df['currentdate'] - working_df['firstauthorupdate']).dt.days

# Assign 'active' or 'inactive' based on the value of 'author_lastupdate_diff'
working_df['author_activity'] = np.where(working_df['author_lastupdate_diff'] <= 60, 'active', 'inactive')

# Compute the number of items in 'relationship' column and assign it to 'num_relationship' column
working_df['num_relationship']=get_num_item(working_df['relationship'])

# Compute the number of items in 'characters' column and assign it to 'num_characters' column
working_df['num_characters']=get_num_item(working_df['characters'])

# Compute the number of items in 'tags' column and assign it to 'num_tags' column
working_df['num_tags']=get_num_item(working_df['tags'])

# Selecting the desired columns in prev_df
prev_df = prev_df[['link', 'words', 'hits', 'kudos', 'comments', 'bookmarks']]

# Renaming the columns in prev_df
prev_df = prev_df.rename(columns={'words': 'prev_words', 'hits': 'prev_hits', 'kudos': 'prev_kudos', 'comments': 'prev_comments', 'bookmarks': 'prev_bookmarks'})

# Merging prev_df with working_df based on the 'link' column
working_df = working_df.merge(prev_df, how='left', on='link')

# Filling missing values in the 'prev_words', 'prev_hits', 'prev_kudos', 'prev_comments', 'prev_bookmarks' columns with 0
working_df['prev_words'].fillna(0, inplace=True)
working_df['prev_hits'].fillna(0, inplace=True)
working_df['prev_kudos'].fillna(0, inplace=True)
working_df['prev_comments'].fillna(0, inplace=True)
working_df['prev_bookmarks'].fillna(0, inplace=True)

def get_df_item(id_column, item_column, name_col):
    item_list = []
    
    # Iterate over the length of id_column
    for x in range(len(id_column)):
        try:
            # Clean up item_column values by removing unwanted characters and splitting by commas
            row_item = item_column[x].replace("[","").replace("]","").replace("'","").replace('"','').split(",")
        except:
            row_item = ['']  # Handle exception by assigning an empty list if an error occurs
        
        # Iterate over each item in the cleaned row_item
        for item in row_item:
            item = item.strip()  # Remove leading/trailing whitespaces
            
            if '&' not in item:
                item_list.append([id_column[x], item])  # Append id_column and item to item_list
    
    return pd.DataFrame(item_list, columns=['link', name_col])

# Get the 'charactername' column from 'working_df' and create a new DataFrame 'char_df'
char_df = get_df_item(working_df['link'], working_df['characters'], 'charactername')

# Read the 'characters.csv' file into a DataFrame 'character'
character = pd.read_csv('AO3/characters.csv')

# Merge 'char_df' and 'character' DataFrames based on 'charactername' column
char_df = char_df.merge(character, how='left', on='charactername')

# Fill missing values in 'character' column with values from 'charactername' column
char_df['character'] = char_df['character'].fillna(char_df['charactername'])

# Drop the 'charactername' column from 'char_df'
char_df = char_df.drop(columns='charactername')

# Return the modified 'char_df' DataFrame
char_df

relationship_df = get_df_item(working_df['link'], working_df['relationship'], 'shiptag')

# Read the 'relationships.csv' file into a DataFrame
relationship = pd.read_csv('AO3/relationships.csv')

# Merge relationship_df and relationship DataFrames based on 'shiptag' column
relationship_df = relationship_df.merge(relationship, how='left', on='shiptag')

# Fill missing values in 'ship' column with values from 'shiptag' column
relationship_df['ship'] = relationship_df['ship'].fillna(relationship_df['shiptag'])

# Drop the 'shiptag' column from relationship_df
relationship_df = relationship_df.drop(columns='shiptag')

# Display the updated relationship_df DataFrame
relationship_df

# Get DataFrame item for tags
tags_df = get_df_item(working_df['link'], working_df['tags'], 'tag_item')

# Merge DataFrames
char_rel_tag = char_df.merge(relationship_df, how='outer', on='link')
char_rel_tag = char_rel_tag.merge(tags_df, how='outer', on='link')

char_rel_tag

# Export character relationship tags to a CSV file
char_rel_tag.to_csv('AO3/character_relationship_tags.csv', index=False)

# Export working dataframe to a CSV file with a dynamic filename
working_df.to_csv(f'AO3/{filename}.csv', index=False)