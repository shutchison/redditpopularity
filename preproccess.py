import csv
import sys
import time
import json
import re
sys.path.append('/p/home/fourmore/python_modules/nltk/gnu/python2.7/lib/python2.7/site-packages/')
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords


def read_JSON_as_dict(file_name):
    #read the file in as a string and remove non-alphanumeric characters
    dict_of_subs = {}
    for line in open(file_name, 'r'):
        json_object=(json.loads(line.lower()))
        subreddit = json_object["subreddit"]
        #the key is the subreddit and the value is the entirely of the dictionary. Thus we will have a list of dictionaries.
        dict_of_subs.setdefault(subreddit, []).append(json_object)
    return dict_of_subs

def remove_function_words(dict_of_subs):
    dict_of_all_words = {}
    for sub, list_of_comments in dict_of_subs.iteritems():
        for comment in list_of_comments:
            comment_list = wordList = re.sub("[^\w]", " ",  comment["body"]).split()
            comment["body"] = comment_list
            for word in comment_list:
                dict_of_all_words[word] = dict_of_all_words.get(word, 0) + 1

        for comment in list_of_comments:
            comment["body"] = ([word for word in comment_list if word not in stopwords.words("english") if dict_of_all_words[word] >=2])
    return dict_of_subs

def filter_votes_length(dict_of_subs):
    dict = dict_of_subs
    for sub, list_of_comments in dict.iteritems():
        dict[sub] = [comment for comment in list_of_comments if int(comment["ups"]) >= 2 if len(comment["body"]) >= 20]
        #dict["body"] = " ".join(comment["body"])
    return dict

def split_training_test(dict_of_subs):
    comment_number = 0
    training_dict = {}
    testing_dict = {}
    for sub, list_of_comments in dict_of_subs.iteritems():
        for comment in list_of_comments:
            if (comment_number % 8 == 0): testing_dict.setdefault(sub, []).append(comment)
            else: training_dict.setdefault(sub, []).append(comment)
            comment_number +=1
    training_dict = {k: v for k, v in training_dict.items() if v}
    testing_dict = {k: v for k, v in testing_dict.items() if v}
    return (training_dict, testing_dict)

def determine_if_popular(training_dict):
    dict_of_upvotes = {} 
    for sub, list_of_comments in training_dict.iteritems():
        sub_list = []
        for comment in list_of_comments:
            sub_list.append(int(comment["ups"]))
        sorted_list = sorted(sub_list)
        dict_of_upvotes[sub] = int(sorted_list[(len(sorted_list)/4)*3])
    print(dict_of_upvotes)
    for sub, list_of_comments in training_dict.iteritems():
        for comment in list_of_comments:
            if (int(comment["ups"]) >= dict_of_upvotes[sub]): 
                comment["popular"] = True
            else: comment["popular"] = False
    return training_dict

def write_csv(file_name, training_dict):
    headers = ['ups', 'subreddit', 'popular']
    with open("training.csv", "wb") as file:
        w = csv.DictWriter(file, fieldnames=headers, extrasaction='ignore')
        w.writeheader()
        for sub, list_of_comments in training_dict.iteritems():
            for comment in list_of_comments:
                w.writerow(comment)
        file.close()

if __name__ == "__main__":
    print("Starting the timer.")
    start_time = time.time()
    dict_of_subs = read_JSON_as_dict("largeJSON")
    print("It took {0} to read the file.".format(time.time() - start_time))
    dict_of_subs_no_function_words = remove_function_words(dict_of_subs)
    print("It took {0} to remove function words.".format(time.time() - start_time))
    dict_of_subs_stripped = filter_votes_length(dict_of_subs_no_function_words)
    dict_reduced = {k: v for k, v in dict_of_subs_stripped.items() if v}
    print("It took {0} to filter votes.".format(time.time() - start_time))
    
    training_dict, testing_dict = split_training_test(dict_reduced)
    testing_size = sum([len(v) for v in testing_dict.values()])
    training_size = sum([len(v) for v in training_dict.values()])
    print("Training size: {0}, testing size: {1}.".format(training_size, testing_size))
    
    training_dict_tagged = determine_if_popular(training_dict)
 
    print(training_dict_tagged)
    write_csv('training.csv', training_dict_tagged)
    print("total time: {0}.".format(time.time() - start_time))
