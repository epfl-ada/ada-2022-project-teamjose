# Entertainment evolution during the COVID crisis

Notebook: analyses/Milestone3.ipynb

Datastory: [rob789.github.io/datastory_entertainment](https://rob789.github.io/datastory_entertainment/)

# Abstract
In March of 2020, the Covid-19 outbreak was declared a global pandemic by the World health Organization. Worldwide, people were then recommended or obliged to stay home in order to limit the spread of the virus. This unusual situation left people with limited options for social and work activity, causing many to turn to the Internet for work, education and entertainment. As explained in the "Sudden Attention Shifts on Wikipedia During the COVID-19 Crisis" paper, the volume and nature of Wikipedia article research was affected by the lockdown waves. Notable findings were that "the sharp decrease in human mobility induced by COVID-19-related non-pharmaceutical interventions has boosted the volume of information seeking on Wikipedia and has changed the nature of the information sought, even considering non-COVID-19-related articles". After mobility restrictions were lifted the volume of research returned to the baseline for most topics, but not all. Topics that experienced persistent increases are mostly related to entertainment/culture. We decided to dig deeper, to find whether isolation situation changed the nature of media consumption (i.e., video-game/movie/book genres), and if those changes are persistent with mobility restrictions.
# Research Questions

How did the entertainment means change during the CoronaVirus pandemic lockdown compared to pre-Covid times? Did the genres, consumption levels and nature of entertainment change? Were these changes only valid during the lockdown or did we witness a continuation in the new means of entertainments even after the end of lockdown? Can we see the Covid virus as a proxy to what people enjoy consuming in isolation times?


# Proposed additional datasets

* Mobile application downloads 2019-2021,
  This Dataset contains the number of downloads of applications and games from 2015 to 2021 divided into quarters
  
  SOURCE 
  https://www.businessofapps.com/data/app-statistics/

* Top 50 Bestselling Novels 2009-2020 of Amazon,
  This dataset contains the name, genre (Fiction or Non Fiction) and number of reviews of the top 50 best selling books on Amazon between 2009 and 2020.
  
  SOURCE  
  https://www.kaggle.com/datasets/palanjali007/amazons-top-50-bestselling-novels-20092020?resource=download
  
* Google trends  
    Non-official API allowing us to query the Google Trends database. We can find the frequency of research terms within a certain period of time, while filtering by language, theme, result type, geolocation.
* Wikipedia Api  
  Api allowing us to compare the number of pageviews of different wikipedia pages. We will compare the number of visits of different categories as well as different     topics among a same category (ie different video games genres)

* Steam DB  
    A database of the number of people logged in steam over time. We can also research the number of players of a certain game over time. This allows us to compare videogames players over time by category.
* Twitch : Top games on Twitch 2016 - 2021  
  In this dataset we can find the top 200 games on twitch for each month from 2016 to present day.
  The data is divided into two datasets:
    - A bigger file - Twitchgamedata in which we find 200 obeservations per month representing the top games or categories on twitch for that month.
    - A smaller file - Twitchglobaldata in which there is one obeservation per month that contains the general statistics about viewership on twitch.  
  SOURCE  
    www.sullygnome.com  
  COLLECTION METHODOLOGY  
    Scraped using RSelenium and Rvest

# Methods
*DATA*  
Step 1: Dataset Collection and Construction   
Step 2: Dataset Preprocessing and Organization  
*ANALYSIS*  
Step 3: General preliminary analysis  
Step 4: Defining the analysis questions regarding the Datastory  
Step 5: Perform the statistical analysis and regressions to answer the questions 
  (Difference-in-differences and Distance from normality)  
*VISUALIZATION/STORY-TELLING*  
Step 6: Find the best way to visualize and present the data  
Step 7: Github site building and Datastory redaction  
Step 8: Make everything nice and aesthetic  

# Proposed Timeline

* 25.12.22 Finalize datasets + Pause project work.
* 02.12.22 Homework 2 deadline
* 12.12.22 Perform final analyses.
* 14.12.22 Rough datastory outline.
* 17.12.22 Finalize code implementations and visualisations.
* 20.12.22 Complete datastory.
* 23.12.22 Milestone 3 deadline

# Organization within the team
* Analysis: 
    - Wikidata : Shadya, José
    - G-Trends : Robin, Shadya
    - Twitch : José, Joe
    - Amazon Best sellers : Joe, Robin
    - SteamDB : José, Robin
    - Wikipedia API : Shadya, Joe
    
    Then for the analysis across the datasets, it's gonna be a collaborative work with the whole team.
        
* Datastory: The big ideas will be better discussed with the whole team.
        Robin and Shadya will then prepare the final storyline, plots, UX etc.
        
* Website: The design of the website will be discussed with the whole team. José and Joe will be in charge of the implementation.
    P.S. As we never had to build such a website before, this repartition of task will probably change.

