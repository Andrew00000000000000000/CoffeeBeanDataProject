import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


client = MongoClient('mongodb+srv://admin:0000@cluster0.xfwvw.mongodb.net/')
db = client['coffee']
collection = db['coffee_source_corral']



def create_empty_coffee_dict():
    empty_dict = {
        "sourceurl": None,
        "source_type": None,
        "name": None,
        "Taste": None,
        "Variety": None,
        "Process": None,
        "Country": None,
        "Region": None,
        "Price": None,
        "Weight": None,
        "Altitute in meters": None,
        "Roast": None,
        "Flavors_Spicy": None,
        "Flavors_Choclaty": None,
        "Flavors_Nutty": None,
        "Flavors_Buttery": None,
        "Flavors_Fruity": None,
        "Flavors_Flowery": None,
        "Flavors_Winey": None,
        "Flavors_Earthy": None,
        "Attributes_Brightness": None,
        "Attributes_Body": None,
        "Attributes_Aroma": None,
        "Attributes_Complexity": None,
        "Attributes_Balance": None,
        "Attributes_Sweetness": None,
        "Comments_list": None,
        "Comment_ratings_list" : None,
        "avg_rating from customer": None,
        "image_url": None
    }
    
    return empty_dict

# Call the function to get the empty dictionary

def get_each_coffee_bean_attribute(url):
    response = requests.get(url)
    url_base = "https://www.coffeebeancorral.com/"
    this_coffee_bean = create_empty_coffee_dict()
    this_coffee_bean['sourceurl'] = url
    this_coffee_bean['source_type'] = "corral"
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        #Name
        name_element = soup.find('span', {'id': 'ctl00_MainContentHolder_sName', 'class': 'coff-name'})        
        if name_element:
            coffee_name = name_element.text.strip()
            this_coffee_bean['name'] = coffee_name
            
        else:
            coffee_name = "Name not found on the page."
            this_coffee_bean['name'] = coffee_name
        
        #Image_Url
        image_a = soup.find('a', id='ctl00_MainContentHolder_ProductImageViewer_ctl00_lnkImage')
        if image_a:
            this_coffee_bean['image_url'] = url_base + image_a.get('href')
            
        #price
        price = soup.find('span', id='ctl00_MainContentHolder_lblSitePrice')
        if price:
            this_coffee_bean['Price'] = price.text
        #Taste
        Taste_list = soup.find('span', id='ctl00_MainContentHolder_lblShortDescription')
        
        if Taste_list:
            p_element = Taste_list.find('p')
            if p_element:
                p_text = p_element.get_text().replace("Cupping Notes: ", "")
                cleaned_text = [term.strip().replace(".", "") for term in p_text.split(",")]
                this_coffee_bean["Taste"] = cleaned_text
            else:
                this_coffee_bean["Taste"] = f"Not Provided"

        #Attributes
        
        
        attribute_keys = ["Attributes_Brightness", "Attributes_Body", "Attributes_Aroma", "Attributes_Complexity", "Attributes_Balance", "Attributes_Sweetness"]
        attribute_ids = ["ctl00_MainContentHolder_imgBrightness","ctl00_MainContentHolder_imgBody","ctl00_MainContentHolder_imgAroma","ctl00_MainContentHolder_imgComplexity","ctl00_MainContentHolder_imgBalance","ctl00_MainContentHolder_imgSweetness"]
        for key, id_name in zip(attribute_keys, attribute_ids):
            span = soup.find('span', id=id_name)
            if span:
                attribute_value = span.get('class')[0][-1]
                this_coffee_bean[key] = attribute_value

        #Flavors
        flavor_keys = ["Flavors_Spicy", "Flavors_Choclaty", "Flavors_Nutty", "Flavors_Buttery", "Flavors_Fruity", "Flavors_Flowery", "Flavors_Winey","Flavors_Earthy"]
        flavor_ids = ["ctl00_MainContentHolder_imgSpicy","ctl00_MainContentHolder_imgChocolaty","ctl00_MainContentHolder_imgNutty","ctl00_MainContentHolder_imgButtery","ctl00_MainContentHolder_imgFruity","ctl00_MainContentHolder_imgFlowery","ctl00_MainContentHolder_imgWiney","ctl00_MainContentHolder_imgEarthy"]
        for key, id_name in zip(flavor_keys, flavor_ids):
            span = soup.find('span', id=id_name)
            if span:
                flavor_value = span.get('class')[0][-1]
                this_coffee_bean[key] = flavor_value
        
        #Specification
        Coffee_spec = soup.find('div', id='ctl00_MainContentHolder_ProductTypeDisplay1_ProductTypePanel')
        if Coffee_spec:
        # Find all the li elements inside the div
            li_elements = Coffee_spec.find_all('li')
        Coffee_spec_dict = {}
        # Print the content of each li element
        for li in li_elements:
            key_value_span = li.find_all('span')
            key = key_value_span[0].text.strip()
            value = key_value_span[1].text.strip()
            Coffee_spec_dict[key] = value
        
        this_coffee_bean["Country"] = Coffee_spec_dict["Country"] if "Country" in Coffee_spec_dict else None
        this_coffee_bean["Region"] = Coffee_spec_dict["Local Region"]  if "Local Region" in Coffee_spec_dict else None
        this_coffee_bean["Process"] = Coffee_spec_dict["Process"]  if "Process" in Coffee_spec_dict else None
        this_coffee_bean["Variety"] = Coffee_spec_dict["Variety"]  if "Variety" in Coffee_spec_dict else None 
        this_coffee_bean["Altitute in meters"] = Coffee_spec_dict["Altitude (meters)"] if "Altitude (meters)" in Coffee_spec_dict else None
        
        #Avg_Rating:
        avg_rating_img = soup.find('img', id='ctl00_MainContentHolder_ProductReviewDisplayInline2_imgAverageRating')
        if avg_rating_img:
            average_rating = avg_rating_img['src'][-5]
            this_coffee_bean["avg_rating"] = average_rating
        #Comments:
        comments_table = soup.find('table', id='ctl00_MainContentHolder_ProductReviewDisplayInline2_dlReviews')
        if comments_table:
            rating_stars_imgs = comments_table.find_all('img', class_='ratingstars')
            comment_rating = [img['src'][-5] for img in rating_stars_imgs]
            comments_p = comments_table.find_all('p',class_="productreviewdescription")
            descriptions = [rating_description.find('span').text.strip() for rating_description in comments_p]
            comment_dict = {}
            #for i in range(min(5,len(comment_rating))):
            #    comment_dict[i] = f"{comment_rating[i]},{descriptions[i]} "
            #comment_dict = {str(key): value for key, value in comment_dict.items()}
            #this_coffee_bean["Comments"] = comment_dict 

            comment_rating = comment_rating[:min(len(comment_rating),5)]
            descriptions = descriptions[:min(len(descriptions),5)]
            this_coffee_bean["Comment_ratings_list"] = comment_rating
            this_coffee_bean["Comments_list"] = descriptions

        #Roast: Any
        this_coffee_bean["Roast"] = "Any"

        return this_coffee_bean



def scrape_product_divs(url):
    url_list = [] 
    response = requests.get(url)
    url_base = "https://www.coffeebeancorral.com/"
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        products_div = soup.find('div', id='products')
        if (products_div):
            product_links = products_div.find_all('a', class_='product-img-link rounded-top')
            for link in product_links:
                href = link.get('href')
                url_list.append(url_base + href)
            next_url_element =  li_item = soup.find('li', id="ctl00_MainContentHolder_ucFacetedSearchProductGrid_ucDevelisysFacetedSearchPagerTop_next")
            if next_url_element:
                a_tag = li_item.find('a')
                if a_tag:
                    next_url = url_base + a_tag.get('href')
        else:
            next_url = None

        return (url_list,next_url)
    
    else:
        print(f"Failed to retrieve content from {url}")
        return None

url_list = []
page_no = 1
url_list_with_next_page = scrape_product_divs("https://www.coffeebeancorral.com/categories/Green-Coffee-Beans/All-Coffees.aspx")
while(url_list_with_next_page[1] is not None):
    url_list_in_this_page = url_list_with_next_page[0]
    for url in url_list_in_this_page:
        url_list.append(url)
    print(f"Finished taking url_list from page: {page_no}")
    page_no = page_no + 1
    url_list_with_next_page = scrape_product_divs(url_list_with_next_page[1])
total_urls = len(url_list)
print(f"Total length: {total_urls}")

for index, url in enumerate(url_list, 1):  # Start enumeration from 1
    coffee_info = get_each_coffee_bean_attribute(url)
    collection.insert_one(coffee_info)
    
    # Calculate percentage completion
    progress = round(index / total_urls * 100)
    
    # Check if every 10% is reached
    if progress % 10 == 0:
        print(f"{progress}% of URLs processed.")

print("Finished")


