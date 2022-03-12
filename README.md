# TTC Subway Delay Data

![Dashboard](/delay-analysis/path/to/img.jpg "Optional title")


## Introduction 
TTC Subway Delay Data - [https://open.toronto.ca/dataset/ttc-subway-delay-data/](https://open.toronto.ca/dataset/ttc-subway-delay-data/)

The dataset provided includes provides data around TTC Subway & SRT Train Service Delays.The idea behind this analysis will be to investigate the delay categories themselves to quantify which ones are causing the most is

Methods

Step 1) 

Use Python to perform the API request, which will be using the requests platform.
An example query is: 

import pandas as pd
import requests
 
```py
# Get the dataset metadata by passing package_id to the package_search endpoint
# For example, to retrieve the metadata for this dataset:
 
url = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show"
params = { "id": "996cfe8d-fb35-40ce-b569-698d51fc683b"}
package = requests.get(url, params = params).json()
print(package["result"])
```



Step 2)

This JSON object contains a URL to download each month’s XLSX file. The python script will unpack the json object, create a DataFrame of dataset name: url  mapping. 

```py
l_of_urls = []
for item in package["result"]["resources"]:
    data_name = item["name"]
    data_url = item["url"]
    l_of_urls.append([data_name, data_url])

#   Read into a clean DF
#   Create Connection String/engine
df = pd.DataFrame(l_of_urls, columns=["name", "url"])
df = df.iloc[1:, :]
```



Step 3) 
Retrieve each XLSX file and append it to a MySQL Database. This will only be a viable solution for the first iteration as future iterations would not need to re-upload previous data. A conditional statement could be created such that no duplicate entries are added as well. 


```py
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
```

