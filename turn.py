from django.utils.text import slugify
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor
def turn_completed(allrow):
    num , row = allrow
    name = row['Book Name']
    completed_tag = row['Novel Status']
    slug = slugify(name)
    if completed_tag == "Completed":
        
        base_url = "https://wuxianovels.co/api/admin-novels/"
        novel_url = f'{base_url}{slug}/'
        headers = {
            "Authorization" : f"Token 95c305735269dee5da99830919f9dacc6ca10e1f"
        }
        data = {
            "novelStatus" : True
        }
        response = requests.patch(novel_url, headers= headers, data = data)
        print(num)
df = pd.read_csv("both.csv")
with ThreadPoolExecutor(max_workers=50) as exec:
    all_rows = df.iterrows()
    results = exec.map(turn_completed,all_rows )