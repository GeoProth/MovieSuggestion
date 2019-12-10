import operator
import pandas as pd
import numpy as np
from tabulate import tabulate

#---------------------------------------------------------------------------------------------------
    # IMPORT MOVIES AND MANIPULATE DATA FOR USE
#---------------------------------------------------------------------------------------------------

movies = pd.read_csv("movies.csv")
movies = movies.drop(['movieId'], axis=1)
movies['title'] = movies['title'].str.strip()   #remove trailing spaces to get accurate year
movies['year'] = movies['title'].str[-5:-1]     #get year in own separate column
movies['title'] = movies['title'].str[:-6]      #remove year from title

data = movies[['imdbId', 'genres']].copy()
data['genres'] = data['genres'].str.split('|')
#print(data)
dict = data.set_index('imdbId').T.to_dict('list')  # sets ImdbId to key, genres as values

user_movie_selections = [] #imdbid of movies selected
user_genre_selections = [] # list of genres user has selected
user_suggestions = ""
#print(tabulate(movies.head()))
#---------------------------------------------------------------------------------------------------
    # WHEIGHTED JACCARD
#---------------------------------------------------------------------------------------------------
# Based on 'Weighted Jaccard.'
# Weighted Jaccard definition is:
# J(A,B)= ∑i min(ai,bi) / ∑i max(ai,bi)
#
# my distance formula:
# distace = weighted(a,b) = (occurences of b in c) / (c.total_values)
# where c is a weighted dictionary that shows how many times each genre appears in the selections
# where a is a list of the list of genres
# where b is a list of genres of the compared to movie
# so the result will be between 0.0 - 1.0
def weighted_jaccard_similarity(a, b):
    # in this case, 'a' is all the selections that the user has made so far
    # build the weighted dictionary:
    c = {'total': 0}
    for genre in a:  # a is list of user_genres
        #print(genre)
        if genre in c:
            c[genre] += 1
        else:
            c[genre] = 1
        c['total'] += 1

    numerator = 0
    denomenator = c['total']
    for value in b:
        for genre in value:
            if genre in c:
                numerator += c[genre]

    return numerator / denomenator

#----------------------------------------------------------------------------------------------------
    # K NEAREST NEIGHBOR
#----------------------------------------------------------------------------------------------------
# looks at the entire data set ('data')
# and returns the k nearest neighbors based on the distance metric
# 'target' is the movie that we are comparing to
# returns the index of the k movies that are closest
def neighbors(data, target):
    distances = []
    for k, v in data.items():
        dist = weighted_jaccard_similarity(target, v)
        distances.append((k, v, dist))
    distances.sort(key=operator.itemgetter(2), reverse=True)  # sort based on the distance
    for x in range(len(user_movie_selections)):
        search = user_movie_selections[x]
        for sublist in distances:
            if sublist[0] == search:
                distances.remove(sublist) # remove already selected movies from distances
    neigh = []
    for x in range(10): # set k to 10
        neigh.append(distances[x][0])
    return neigh

def prev_suggestion(df):
    print("\n\t\tPREVIOUS SUGGESTIONS")
    print(tabulate(df[['title', 'year', 'imdbId']], showindex=False, headers=['title', 'year', 'imdbId']))
    input_selection(df)

# find k nearest neighbor and suggest to user using jacaard similarity
def movie_suggestions():
    result = neighbors(dict, user_genre_selections)
    user_titles = movies.loc[movies['imdbId'].isin(user_movie_selections)]
    print("\n\t\tMOVIES YOU'VE WATCHED SO FAR:")
    print(tabulate(user_titles[['title', 'year', 'imdbId']], showindex=False, headers=['title', 'year', 'imdbId']))
    user_suggestions = movies.loc[movies['imdbId'].isin(result)]
    print("\n\t\tNEW MOVIE SUGGESTIONS")
    print(tabulate(user_suggestions[['title', 'year', 'imdbId']], showindex=False, headers=['title', 'year', 'imdbId']))
    input_selection(user_suggestions)



# find movie user has picked.  print it out
def movie_selector(imdbid):
    df = movies.loc[movies['imdbId'] == imdbid]
    user_movie_selections.append(df['imdbId'].values[0]) # append imdbId's to users selections
    genres = movies['genres'].loc[movies['imdbId'] == imdbid].apply(lambda x: x.split('|'))
    #print(genres)
    for x in genres:
        user_genre_selections.extend(x)
    #print(user_genre_selections)
    movie_suggestions()

def input_selection(df):
    print("-----------------------------------------------------------------------------------------")
    print("\t\tCHOOSE AN OPTION BELOW: ")
    print("1) Enter ImdbId selection")
    print("2) Search again")
    print("3) Clear Search")
    print("4) EXIT")
    select = input("\tEnter choice here: ")
    while select != '1' and select != '2' and select != '3' and select != '4':
        select = input("Sorry, invalid input. Try again: ")
    if select == '1':
        search = input("\tEnter ImdbId Choice here: ")
        check = True
        while check:
                try:
                    search = int(search)
                    if search < 5 or search > 4530184:
                        print("\t\tNot a Valid imdId, try again")
                    else:
                        check = False
                except ValueError:
                    print("\t\tNot a valid entry, try again: ")
        movie_selector(search)
    elif select == '2':
        print()
        search_title_year(df)
    elif select == '3':
        prev_suggestion(df)
    elif select == '4':
        print("Thanks for watching! good bye")
        exit(0)

# find matching movies by year
def search_df_year(str):
    key = str
    df = movies[movies['year'] == key]
    return df

# find matching movies by title
def search_df_title(str):
    key = str
    df = movies[movies['title'].str.contains(key, case=False)]
    return df

# get title word or key words from user, find matches
def get_title_word(df):
    print("\tPlease Enter a title or key words from title below: \n")
    check = True
    title_df = ""
    str = ""
    while check:
        title = input("Title: ")
        title_df = search_df_title(title)
        if not title_df.empty:
          str = title
          check = False
        else:
            print("No movies match that input, try again: ")
    print("\t\tMovies that match: ", str)
    print(tabulate(title_df[['title', 'year', 'imdbId']], showindex=False, headers=['title', 'year', 'imdbId']))
    input_selection(df)

# get movie year from user, find matches
def get_title_year(df):
    print("\tPlease Enter a title YEAR below: \n")
    check = True
    year_df = ""
    str = ""
    while check:
        year = input("Year: ")
        year_df = search_df_year(year)
        if not year_df.empty:
          str = year
          check = False
        else:
            print("No movies match that year, try again: ")
    print("\t\tMovies released in: ", str)
    print(tabulate(year_df[['title', 'year', 'imdbId']], showindex=False, headers=['title', 'year', 'imdbId']))
    input_selection(df)


# search option
def search_title_year(df):
    print("\t\tCHOOSE AN OPTION BELOW: ")
    print("1) Search movie title")
    print("2) Search movie year")
    print("3) EXIT\n")
    search = input("\tEnter choice here: ")
    while search != '1' and search != '2' and search != '3':
        search = input("Sorry, invalid input. Try again: ")
    if search == '1':
        print("\tsearch by title")
        get_title_word(df)
    elif search == '2':
        print("\tsearch by year")
        get_title_year(df)
    else:
        print("thank you, have a nice day. good bye!")
        exit(0)

#--------------------------------------------------------------------------------------------------
    # Opening Message with Random Selection of Movies
    # AND Search option
#--------------------------------------------------------------------------------------------------

def welcome_random():
    print("----------------------------------------------------------------------------------")
    print("\t\tWelcome! Here are 10 movie suggestions to begin: \n")
    user_suggestions = movies[['title', 'year', 'imdbId']].sample(n=10)
    print(tabulate(user_suggestions, showindex=False, headers=['title', 'year', 'imdbId']))
    print("----------------------------------------------------------------------------------")
    search_title_year(user_suggestions)


#start session
welcome_random()

