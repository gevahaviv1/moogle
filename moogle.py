#################################################################
# FILE : moogle.py
# WRITER : Geva Haviv
# DESCRIPTION:
# WEB PAGES I USED:
# NOTES:
#################################################################

import sys
import bs4
import pickle
import requests
import urllib.parse

# ---------------------------- PART 1 ----------------------------


"""
This function found the number of links for each linked_url in url_path.
url_path = the full path for each relative url in index_file.txt.
linked_url = the relative path from index_file.txt.
Input: url_path, linked_url
Output: The number of link of linked_url in url_path.
"""


def found_num_of_links(url_path, linked_url):
    response = requests.get(url_path)
    html = response.text
    soup = bs4.BeautifulSoup(html, 'html.parser')
    lst = []

    for p in soup.find_all('p'):
        for link in p.find_all('a'):
            target = link.get('href')
            if target != '':
                lst.append(target)

    return lst.count(linked_url)


"""
This function create dictionary for each full_url in index_file.
The dictionary is from type {base_url: num}.
index_file = the files that contains the relative urls.
base_url = the basic path.
full_url = the base_url + relative_url.
num = the num of specific relative links in full_url.
Input: index_file, full_url.
Output: dictionary.
"""


def create_dic_for_linked_page_name(index_file, full_url):
    linked_page_name = dict()
    for linked_url in index_file:
        count = found_num_of_links(full_url, linked_url)
        if count > 0:
            linked_page_name[linked_url] = count

    return linked_page_name


"""
This function create dictionary for each relative url in index_file.
The dictionary is from type {str: dic()}.
index_file = the files that contains the relative urls.
base_url = the basic path.
out_file = the file that we want to save the data into it.
Input: base_url, index_file, out_file.
Output: dictionary.
"""


def create_link_dic(base_url, index_file, out_file):
    with open(index_file, 'r') as file:
        small_index = file.read().splitlines()
    traffic_dict = dict()
    small_index_lst = [row for row in small_index]

    for relative_url in small_index_lst:
        full_url = urllib.parse.urljoin(base_url, relative_url)
        traffic_dict[relative_url] = create_dic_for_linked_page_name(small_index_lst, full_url)

    with open(out_file, 'wb') as f:
        pickle.dump(traffic_dict, f)


# ---------------------------- PART 2 ----------------------------


"""
This function get the sum of all links from one page.
d = the dictionary in place [i] that we got from the get_value() function.
Input: d.
Output: sum.
"""


def sum_of_links(d):
    sum_return = 0
    for key in d:
        sum_return += d[key]

    return sum_return


"""
This function get the value of each page.
d = the dictionary that we got from crawl the web.
r = the last dictionary.
key = the page we want to update.
Input: d, r, key.
Output: new_value (new rank for the page).
"""


def get_value(d, r, key):
    new_value = 0
    for i in d:
        if key in d[i]:
            new_value += (r[i] * (d[i][key] / sum_of_links(d[i])))

    return new_value


""" 
This function update the dictionary rank one time.
r = the dictionary we update.
d = the dictionary that we got from crawl the web.
Input: r, d.
Output: r (dictionary of all the pages after one rank).
"""


def update_values_in_dict(r, d):
    return_dict = dict()
    for key in r:
        return_dict[key] = get_value(d, r, key)

    return return_dict


"""
This function create dictionary that rank all the pages based on the links each page get from all pages.
iterations = number of iterations we rank the pages.
dict_file = the dictionary that we got from crawl the web.
out_file = the name of the dictionary page rank we want to save at the end of the function.
Input: iterations, dict_file, out_file.
Output: r (dictionary of all the pages after the rank).
"""


def create_rank_dic(iterations, dict_file, out_file):
    with open(dict_file, 'rb') as f:
        d = pickle.load(f)
    r = dict()
    for key in d:
        r[key] = 1

    for i in range(iterations):
        r = update_values_in_dict(r, d)

    with open(out_file, 'wb') as f:
        pickle.dump(r, f)


# ---------------------------- PART 3 ----------------------------


"""
This function get all the text from single webpage, spilt it and put it inside a list.
full_url = the base_url + relative_url from the function create_word_dict().
Input: full_url.
Output: lst.
"""


def get_all_text_from_web(full_url):
    response = requests.get(full_url)
    html = response.text
    soup = bs4.BeautifulSoup(html, 'html.parser')
    content = ''
    for p in soup.find_all('p'):
        content += ' ' + p.text

    content.replace('\r', '')
    return str.split(content)


"""
This function create dictionary that count all the words in each page.
base_url = the basic path.
index_file = the files that contains the relative urls.
out_file = the file that we want to save the data into it.
Input: base_url, index_file, out_file.
Output: dictionary.
"""


def create_word_dict(base_url, index_file, out_file):
    with open(index_file, 'r') as file:
        small_index = file.read().splitlines()
    word_dict = dict()
    small_index_lst = [page_name for page_name in small_index]

    for relative_url in small_index_lst:
        full_url = urllib.parse.urljoin(base_url, relative_url)
        content = get_all_text_from_web(full_url)  # The variable is from type list.
        for word in content:
            if word != '':
                if word not in word_dict:
                    word_dict[word] = {relative_url: content.count(word)}
                else:
                    word_dict[word].update({relative_url: content.count(word)})

    with open(out_file, 'wb') as f:
        pickle.dump(word_dict, f)


# ---------------------------- PART 4 ----------------------------


"""
This function return all the max pages with the highest rank.
ranking_dict_file = the ranking dictionary.
lst_of_pages = list of pages that the word are exist in.
max_results = natural number.
Input: ranking_dict_file, lst_of_pages, max_results.
Output: List.
"""


def get_first_max_pages(ranking_dict_file, lst_of_pages, max_results):
    ranking_dict_file = list(ranking_dict_file)
    i = 0
    lst = []
    while len(lst) < max_results:
        if ranking_dict_file[i] in lst_of_pages:
            lst.append(ranking_dict_file[i])
        i += 1

    return lst


"""
This function return all the pages that contains the word.
word_dict_file = the word dict we got.
word = the word that we search.
Input: word_dict_file, word.
Output: List.
"""


def get_all_pages(word_dict_file, word):
    return [page for page in word_dict_file[word]]


"""
This function sort the dictionary by value from big to small.
un_sorted_dict = un sorted dictionary.
Input: un_sorted_dict.
Output: dictionary.
"""


def sort_dict(un_sorted_dict):
    sorted_keys_lst = sorted(un_sorted_dict, key=un_sorted_dict.get, reverse=True)
    sorted_dict = dict()

    for key in sorted_keys_lst:
        sorted_dict[key] = un_sorted_dict[key]

    return sorted_dict


"""
This function check if the dictionary is sorted by value from big to small.
dictionary = some dictionary.
Input: dictionary.
Output: Bool.
"""


def is_sorted(dictionary):
    lst_of_values = list(dictionary.values())
    i = 1
    while i < len(lst_of_values):
        if float(lst_of_values[i - 1]) < float(lst_of_values[i]):
            return False
        i += 1

    return True


"""
This function return the word from the list with the minimum value from the word_dict_file dictionary.
lst_words = list of words.
word_dict_file = word dictionary.
Input: lst_words, word_dict_file.
Output: List.
"""


def get_min_word(lst_words, word_dict_file):
    count = 0
    minimum = 0
    i = 0

    for word in lst_words:
        if word in word_dict_file:
            for page in word_dict_file[word]:
                count += word_dict_file[word][page]
        if count > minimum:
            minimum = count
            i += 1
        count = 0

    return lst_words[i]


"""
This function search for word in the word_dict_file dictionary.
Calculate the value of each word in each page from the top max_results (natural number),
by formula that use the ranking_dict_file and the number of times the word appears in word_dict_file. 
query = some string (word to search).
ranking_dict_file = rank dictionary.
word_dict_file = word dictionary.
max_results = the number of pages we take for each word.
Input: query, ranking_dict_file, word_dict_file, max_results.
Output: String.
"""


def search(query, ranking_dict_file, word_dict_file, max_results):
    with open(ranking_dict_file, 'rb') as f:
        ranking_dict_file = pickle.load(f)
    with open(word_dict_file, 'rb') as f:
        word_dict_file = pickle.load(f)
    lst_words = query.split()
    ranking_dict_file = sort_dict(ranking_dict_file)
    results = open('results.txt', 'a')

    if len(lst_words) > 1:
        value = get_min_word(lst_words, word_dict_file)
        lst_words.clear()
        lst_words.append(value)

    for word in lst_words:
        if word in word_dict_file:

            # This block take all the max_results pages that contains the word.
            lst_of_pages = get_all_pages(word_dict_file, word)
            if max_results > len(lst_of_pages):
                max_results = len(lst_of_pages)
            max_results_lst = get_first_max_pages(ranking_dict_file, lst_of_pages, max_results)

            # This block calculate the results by the formula and insert it into dictionary.
            final_results = dict()
            for i in range(len(max_results_lst)):
                page = max_results_lst[i]
                final_results[page] = str(ranking_dict_file[page] * word_dict_file[word][page])

            # This block sort the results and output them.
            if not is_sorted(final_results):
                final_results = sort_dict(final_results)
            for key in final_results:
                print(key + ' ' + final_results[key])
                results.write(key + ' ' + final_results[key] + '\r')
            results.write('**********\r')

    results.close()


if __name__ == '__main__':
    if sys.argv[1] == 'crawl':
        BASE_URL = sys.argv[2]
        INDEX_FILE = sys.argv[3]
        OUT_FILE = sys.argv[4]
        create_link_dic(BASE_URL, INDEX_FILE, OUT_FILE)

    elif sys.argv[1] == 'page_rank':
        ITERATIONS = int(sys.argv[2])
        DICT_FILE = sys.argv[3]
        OUT_FILE = sys.argv[4]
        create_rank_dic(ITERATIONS, DICT_FILE, OUT_FILE)

    elif sys.argv[1] == 'words_dict':
        BASE_URL = sys.argv[2]
        INDEX_FILE = sys.argv[3]
        OUT_FILE = sys.argv[4]
        create_word_dict(BASE_URL, INDEX_FILE, OUT_FILE)

    elif sys.argv[1] == 'search':
        QUERY = sys.argv[2]
        RANKING_DICT_FILE = sys.argv[3]
        WORD_DICT_FILE = sys.argv[4]
        MAX_RESULTS = int(sys.argv[5])
        search(QUERY, RANKING_DICT_FILE, WORD_DICT_FILE, MAX_RESULTS)
