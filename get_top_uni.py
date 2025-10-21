import requests
from bs4 import BeautifulSoup
import re
# List of QS ranking URLs (you can add more links here)
qs_urls = [
    "https://www.topuniversities.com/university-rankings-articles/world-university-rankings/top-universities-ireland",
    "https://www.topuniversities.com/university-rankings-articles/world-university-rankings/top-universities-canada",
    "https://www.topuniversities.com/university-rankings-articles/world-university-rankings/top-universities-australia",
    "https://www.topuniversities.com/university-rankings-articles/world-university-rankings/top-universities-uk",
    "https://www.topuniversities.com/university-rankings-articles/world-university-rankings/top-universities-germany",
    "https://www.topuniversities.com/university-rankings-articles/world-university-rankings/top-universities-new-zealand",
    "https://www.topuniversities.com/where-to-study/north-america/united-states/ranked-top-100-us-universities#page-1",
    "https://www.topuniversities.com/where-to-study/north-america/united-states/ranked-top-100-us-universities#page-2"
]
initials = [
            "ranking-data-row_IE-10-2026-no ranking-data-row",
            "ranking-data-row_CA-10-2026-no ranking-data-row",
            "ranking-data-row_AU-10-2026-no ranking-data-row",
            "ranking-data-row_GB-10-2026-no ranking-data-row",
            "ranking-data-row_DE-10-2026-no ranking-data-row",
            "ranking-data-row_NZ-10-2026-no ranking-data-row",
            "ranking-data-row_US-100-2026-no ranking-data-row",
            "ranking-data-row_US-100-2026-no ranking-data-row"
            ]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

all_universities = {}

for i,url in enumerate(qs_urls):
    country = url.split("/")[-1].replace("top-universities-", "").replace("-", " ").title()
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.find_all("div", class_=f"{initials[i]}")
    
    universities = []
    for row in rows[:25]:  # top 25 universities
        rank_div = row.find("div", class_="rank")
        rank = rank_div.get_text(strip=True) if rank_div else "N/A"

        uni_div = row.find("div", class_="uni_name")
        if uni_div and uni_div.find("a"):
            name = uni_div.find("a").get_text(strip=True)
            link = "https://www.topuniversities.com" + uni_div.find("a")["href"]
        else:
            name = "N/A"
            link = "N/A"

        loc_div = row.find("div", class_="location")
        location = loc_div.get_text(strip=True) if loc_div else "N/A"

        universities.append({
            "rank": rank,
            "name": name,
            "link": link,
            "location": location
        })
    
    all_universities[country] = universities

# Print results
for country, unis in all_universities.items():
    print(f"\nTop Universities in {country}:")
    names = []
    for uni in unis:
        names.append(uni['name'])
        print(f"{uni['rank']}. {uni['name']} - {uni['location']} ({uni['link']})")
    with open("universities.txt",'a',encoding='utf-8') as f:
        for name in names:
            name = re.sub('r[^a-zA-z]','',name)
            f.write(name + "\n")  # Write each name followed by a newline
    
