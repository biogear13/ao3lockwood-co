Introduction

I'm very much a fan of Lockwood & Co, the Netflix series and the books, and to tide over my anxiety in waiting for the series renewal, I have been reading fanfics in Archive of Our Own (AO3). I decided to become more productive and exercise some data analytics skills, so I analyzed the current Lockwood and Co fanfictions in AO3.
Objectives

    Web scrape all current fanfics in AO3 about Lockwood & Co and get the following data:
        Title
        Author
        Datetime
        Warnings
        Relationships
        Characters
        Freeforms
        Summary
        Language
        Words
        Chapters
        Collections
        Comments
        Kudos
        Bookmarks
        Hits

    Analyze the data to track the increase in the number of fanfics over time.

How it works

This code uses Selenium and Chrome Driver to scrape data from the website "archiveofourown.org." Specifically, it scrapes data from all pages related to the search query "Lockwood & Co - Jonathan Stroud" on the website.
Required Libraries

The following libraries need to be installed to run this code:

    time
    os.path
    selenium
    pandas
    numpy
    requests
    bs4 (BeautifulSoup)
    datetime

Setup

    The user needs to set up the Chrome driver path based on their configuration.
    The chrome_options object is set to headless = True to ensure that the GUI is turned off.
    The first page related to the search query is loaded to find the maximum number of pages. It is assumed that the number of pages is less than 13.
    The current date and time are also saved for later use.

Scraping

    The links to each work are extracted from each page, starting from the first page.
    These links are used to access each work's webpage to scrape the relevant data such as title, author, datetime, etc.
    If a link takes too long to access, it is added to a "slow_links" list and is skipped for the time being.

Output

    The extracted data is saved in a Pandas DataFrame.
    The DataFrame is saved as a CSV file, named with the current date and time.