# CoffeeBeanDataProject

Here's my part of code and the flow is listed as below
coffeebeancorral.py
Connect with the mongo db
create an empty url_list for each product
for each page, extract all the product urls and inside https://www.coffeebeancorral.com/categories/Green-Coffee-Beans/All-Coffees.aspx?q=&o=1&p=1&i=12&d=12 , append it to the url_list and see is there is next page
if there is a next page, repeat b in the next page, if no, end
Then we have a list of urls with every product inside
For each url in the url list, scrap the data need and insert the product into the mongo db coffee_source_corral collection (which is a table in mongo db)
a progress bar is implemented to check the progress
coffeebeancorral_Dataengineering.py
Connect to mongo db
Extract data from mongo db coffee_source_corral
Do data cleansing, including:
change data type from string to float
do data transformation logic using regular expression in altitude (from "1,750 - 1,950 masl" to 1750)
Import textBlob AI to check the subjectively of the comment
Import a weighted rating calculation logic in the comments with subjective and objective rating, to calculatet the avg_rating from customers
Import the cleaned dataset to coffee_all
As we expect data engineering will take a lot of time (including using AI and continuous update according to Macro and Dexter need),
our mindset is to first create a source database from scrapping so we don't have to scrap the data again and again every time we test it, to increase our efficiency in data engineering,
so we create two database, source and cleaned data.
I hopes it helps :微笑::微笑:
