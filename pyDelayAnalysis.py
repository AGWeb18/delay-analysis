import os
import requests
import pandas as pd
from sqlalchemy import create_engine
import pymysql

os_name = "dev_user"
os_pss = "helloworld"

# Get the dataset metadata by passing package_id to the package_search endpoint
# For example, to retrieve the metadata for this dataset:
url = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show"
params = {"id": "996cfe8d-fb35-40ce-b569-698d51fc683b"}
package = requests.get(url, params=params).json()


#    This for loop will extract the necessary information
#    From the API response.
#    Future analysis could be done on other metadata points.
l_of_urls = []
for item in package["result"]["resources"]:
    data_name = item["name"]
    data_url = item["url"]
    l_of_urls.append([data_name, data_url])

#   Read into a clean DF
#   Create Connection String/engine
df = pd.DataFrame(l_of_urls, columns=["name", "url"])
df = df.iloc[1:, :]

pymysql_str = "mysql+pymysql://{}:{}@127.0.0.1/delayAnalysis".format(os_name, os_pss)
eng = create_engine(pymysql_str)

# Read the URLS into a DataFrame
# Write the DataFrame directly to MySQL
for row in df.iterrows():
    url = row[1]["url"]  #   Store the URL for later use.
    file_name = row[1]["name"]
    if file_name.find("readme") > 0:  #  Check if the word "readme" is found
        continue
    else:
        r = requests.get(url)  # If not found, download the XLSX
        open("temp.xls", "wb").write(r.content)
        df2 = pd.read_excel("temp.xls")  #   Read into DataFrame.
        df2["datasetName"] = file_name  #    Add a column
        print("writing {} to db".format(file_name))
        df2.to_sql("fctDelayFacts", con=eng, if_exists="append")  #  Write to DB
