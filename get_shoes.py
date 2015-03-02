from bs4 import BeautifulSoup
import requests
import argparse
import os
from mongodb import MongoDB
from itertools import izip

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("search_term", help="Search term of ", type=str)
args = parser.parse_args()


class SaksScarper(object):
    def __init__(self, search_term):
        """
        :param search_term: The term you search for, e.g. flats / pumps
        :return: None

        Define the search term, base url and a variable to store the links to
        all the pages related to the serach term
        """
        self.search_term = search_term
        self.params = {'SearchString': self.search_term, 'Nao': 0}
        self.base_url = 'http://www.saksfifthavenue.com/search/EndecaSearch.jsp?\
                         bmForm=endeca_search_form_one&bmFormID=kKYnHcK&bmUID=kKYnHcL&bmIsForm=true\
                         &bmPrevTemplate=%2Fmain%2FSectionPage.jsp&bmText=SearchString&submit-search=\
                         &bmSingle=N_Dim&N_Dim=0&bmHidden=Ntk&Ntk=Entire+Site&bmHidden=Ntx\
                         &Ntx=mode%2Bmatchpartialmax&bmHidden=prp8&prp8=t15&bmHidden=prp13&prp13=\
                         &bmHidden=sid&sid=14BBCA598131&bmHidden=FOLDER%3C%3Efolder_id&FOLDER%3C%3Efolder_id='
        self.base_url = self.base_url.replace(' ', '')
        self.all_links = []
        self.mongo = MongoDB(db_name='shoe', table_name=search_term)

    def join_url(self):
        """
        Concatenate the base_url and the search_term and the page number
        """
        param_str = ''
        for key, val in self.params.iteritems():
            param_str += '&%s=%s' % (key, val)
        return self.base_url + param_str

    def get_page_links(self):
        """
        Base on the first page, get all the links to all the pages
        and assign to instance variable
        """
        initial_link = self.join_url()
        soup = BeautifulSoup(requests.get(initial_link).content)
        # Get the number of total pages
        total_pages = int(soup.select('span.totalNumberOfPages')[0].text)
        # Produce the links to each of the pages (each page has 180 results)
        for ipage in range(total_pages):
            self.params['Nao'] = ipage * 180
            page_link = self.join_url()
            self.all_links.append(page_link)

    @staticmethod
    def _check_data_len(data_lst):
        lens = map(len, data_lst)
        if len(set(lens)) > 1:
            raise Exception('Number of descriptions and images do not match!')
        return lens[0]

    @staticmethod
    def _get_img(img_tags, category, ipage, orientation='front'):
        img_lst = []
        for i, tag in enumerate(img_tags):
            item_id = (ipage + 1) * i
            img_link = tag['src']
            img = requests.get(img_link).content
            img_lst.append(img)
            if not os.path.exists(category):
                os.makedir(category)
            f = open('%s/%s_%s.jpg' % (category, orientation, item_id), 'w')
            f.write(img)
            f.close()

    @staticmethod
    def _get_text(txt_tags):
            return [tag.text.strip() for tag in txt_tags]

    def _get_page_content(self, link, ipage):
        """
        :param html: The HTML page as string
        :return: None

        Get all the info
        """
        html = requests.get(link).content
        soup = BeautifulSoup(html, 'html.parser')

        # Use CSS selectors to get the tags containing the info we want
        designer_name_tags = soup.select('span.product-designer-name')
        description_tags = soup.select('p.product-description')
        price_tags = soup.select('span.product-price')
        front_img_tags = soup.select('img.pa-product-large')
        # Check if the list of tags are all of the same length
        total_num = self._check_data_len([designer_name_tags, description_tags, price_tags])

        # Scrape all the info from the page
        designer_name = self._get_text(designer_name_tags)
        description = self._get_text(description_tags)
        price = self._get_text(price_tags)
        self._get_img(front_img_tags, self.search_term, ipage, orientation='front')
        category = [self.search_term] * total_num

        return izip(category, description, designer_name, price)

    def _insert_into_db(self, data_tuples):
        fields = ['category', 'description', 'designer_name', 'price']
        self.mongo.insertion(fields, data_tuples)

    def main(self):
        """Runs the scraping looping through the pages"""
        self.get_page_links()
        print 'Number of Pages', len(self.all_links)
        for i, link in enumerate(self.all_links):
            if i == 0 or i % 5 == 0:
                print 'Done Page', i
            data_tuples = self._get_page_content(link, i)
            self._insert_into_db(data_tuples)

if __name__ == '__main__':
    sk = SaksScarper(args.search_term)
    sk.main()









