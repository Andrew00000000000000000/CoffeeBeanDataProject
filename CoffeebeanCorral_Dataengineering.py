from pymongo import MongoClient
import pandas as pd
import re
from textblob import TextBlob

# Connect to the MongoDB server
client = MongoClient('mongodb+srv://admin:0000@cluster0.xfwvw.mongodb.net/')
db = client['coffee']
collection = db['coffee_source_corral']

# Query the collection
result = collection.find({})
# Function to extract the first number from a string
def extract_first_number(text):
    match = re.search(r'\d[\d,]*', text)
    if match:
        return match.group()
    else:
        return None

def remove_masl(text):
    if text is not None:
        text =  text.replace('masl', '').strip()
        match = re.search(r'\d[\d,]*', text)
        text = match.group().replace(',', '')
        
        return text
    else:
        return None

def is_subjective(text):
    blob = TextBlob(text)
    subjectivity = blob.sentiment.subjectivity
    return subjectivity > 0.5  # returns True if subjective, False if objective

def check_subjective(list):
    is_subjective_list = []
    if list is not None:
        for comment in list:
            is_subjective_list.append(is_subjective(comment))
    return is_subjective_list

def calculate_weighted_rating(is_subjective, rating):
   
    is_subj_series = pd.Series(is_subjective)
    rating_series = pd.Series(rating)

    # Calculate the number of subjective and objective items
    len_sub = is_subj_series.sum()
    len_obj = len(is_subj_series) - len_sub

    # Handle cases where there are no ratings to process
    if len_sub + len_obj == 0: 
        return -1

    # Replace True with 0.2 for subjective items and fill NaN values
    is_subj_series = is_subj_series.replace(True, 0.2).replace(False, 1).fillna(1.0)
    rating_series = rating_series.fillna(-1).astype(float)

    # Calculate the weighted rating
    normalized_term = len_sub * 0.2 + len_obj

    weighted_rating = (is_subj_series * rating_series).sum() / normalized_term
    return weighted_rating
  
df = pd.DataFrame(list(result))
df['Price / 100g in HKD'] = df['Price'].str.replace('$', '').astype(float)  / 4.53592 *7.79
df['Altitute in meters'] = df['Altitute in meters'].apply(remove_masl).astype(float)
df['is_subjective'] = df['Comments_list'].apply(check_subjective)
# Calculate the weighted rating for the row

weighted_ratings = []
for index, row in df.iterrows():
    weighted_ratings.append(calculate_weighted_rating(row['is_subjective'], row['Comment_ratings_list']))

df['avg_rating from customer'] = weighted_ratings
    



df = df.drop(columns=["Price","Weight","Comment_ratings_list","_id","is_subjective","avg_rating"])
df = df.rename(columns={"Comments_list": "Comments"})
attribute_keys = ["Attributes_Brightness", "Attributes_Body", "Attributes_Aroma", "Attributes_Complexity", "Attributes_Balance", "Attributes_Sweetness"]
flavor_keys = ["Flavors_Spicy", "Flavors_Choclaty", "Flavors_Nutty", "Flavors_Buttery", "Flavors_Fruity", "Flavors_Flowery", "Flavors_Winey","Flavors_Earthy"]



df [attribute_keys + flavor_keys] =   df [attribute_keys + flavor_keys].astype(int)
data_dict = df.to_dict("records")
collection_cleaned = db["coffee_data_engineering_carrol"]
collection_cleaned.insert_many(data_dict)
print("Finished")


# Close the MongoDB connection
client.close()