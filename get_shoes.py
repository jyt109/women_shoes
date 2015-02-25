from bs4 import BeautifulSoup
import requests

base_url = 'http://www.saksfifthavenue.com/search/EndecaSearch.jsp?bmForm=endeca_search_form_one&bmFormID=kKYnHcK&bmUID=kKYnHcL&bmIsForm=true&bmPrevTemplate=%2Fmain%2FSectionPage.jsp&bmText=SearchString&SearchString=flats&submit-search=&bmSingle=N_Dim&N_Dim=0&bmHidden=Ntk&Ntk=Entire+Site&bmHidden=Ntx&Ntx=mode%2Bmatchpartialmax&bmHidden=prp8&prp8=t15&bmHidden=prp13&prp13=&bmHidden=sid&sid=14BBCA598131&bmHidden=FOLDER%3C%3Efolder_id&FOLDER%3C%3Efolder_id='

# search_term = 'pumps'
response = requests.get(base_url)
soup = BeautifulSoup(response.content)
img_lst = soup.select('img')
counter = 0
for item in img_lst:
    try:
        link = item['src']
        if link.startswith('http'):
            image = requests.get(link).content
            counter += 1
            f = open('/Users/JeffreyTang/Desktop/zipfian/winter2015/testing/scraping_shoes/flats%s.png' % str(counter)
                     , 'w')
            f.write(image)
    except:
        pass


