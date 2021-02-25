import re
import numpy as np 
import pandas as pd 

from sklearn.feature_extraction.text import TfidfVectorizer  
from sklearn.model_selection import train_test_split  
from sklearn import svm,metrics
import pickle
import joblib

import re  
import nltk 
nltk.download('stopwords')  
from nltk.corpus import stopwords 
import unidecode

# %matplotlib inline
# from constant import clf, INTENT_THRESHOLD, TYPE_NAME_SEARCH_TTHC, list_chiphi_notification, list_giayto_notification, \
#     list_ketqua_notification, list_thoigian_notification, list_thuchien_notification, list_diadiem_notification
# from query import search
# from functools import reduce


# def searchTTHC(type_database, query):
#     query = preprocess_message(query)
#     [result, info] = search(type_database, query)
#     if len(result) > 0:
#         TTHC = list(map(lambda x: list(map(lambda y: {y[0]: y[1]}, x.items())), result))
#         return [flatten(TTHC), info]
#     return [[],{'type': 'unknown', 'count': 0}]


def catch_intent(message):
    message = preprocess_message(message)
    print(message)

    # intent = extract_and_get_intent(message)
    # if intent != 'none':
    #     return intent
    return predict_message(message)


def predict_message(message):

    X_corp = np.array([message])
    check1=True
    check2=True

    #Check color
    tfidfconverter = pickle.load(open('tfidf_color.pickle', 'rb'))
    clf = pickle.load(open('color_pickle', 'rb'))
    X_corp_tfidf = tfidfconverter.transform(X_corp).toarray()
    y_corp_pred = clf.predict(X_corp_tfidf)
    if int(y_corp_pred[0]) ==1:
        check1=True
    else:
        check1=False
    # if check1==True:
    #     return "color"
    print("check1")
    print (check1)

    #Check size
    tfidfconverter = pickle.load(open('tfidf_size.pickle', 'rb'))
    clf = pickle.load(open('size_pickle', 'rb'))
    X_corp_tfidf = tfidfconverter.transform(X_corp).toarray()
    y_corp_pred = clf.predict(X_corp_tfidf)
    if int(y_corp_pred[0]) ==1:
        check2=True
    else:
        check2=False
    # if check2==True:
    #     return "size"
    print("check2")
    print (check2)

    # if check1==True and check2==True:
    #     return "color_size"
    if check1==True and check2==False:
        return "color"   
    if check1==False and check2==True:
        return "size"
    if check1==False and check2==False:
        return "nothing"
    # #tfidf_converter
    # tfidfconverter = pickle.load(open('tfidf.pickle', 'rb'))
    # tfidfconverter = pickle.load(open('tfidf.pickle', 'rb'))
    # clf = pickle.load(open('module_pickle', 'rb'))
    # X_corp_tfidf = tfidfconverter.transform(X_corp).toarray()
    # y_corp_pred = clf.predict(X_corp_tfidf)
    # if int(y_corp_pred[0]) ==1:
    #     return True
    # else:
    #     return False
    # predict_result = clf.predict(message)

    # proba = max(predict_result[2].numpy()) * 100

    # if (proba < INTENT_THRESHOLD):
    #     return 'none'

    # return get_name_intent(int(predict_result[0]))


# def extract_and_get_intent(message):
#     for notification in list_chiphi_notification:
#         if message.lower().find(notification) != -1:
#             return 'chiphi'

#     for notification in list_diadiem_notification:
#         if message.lower().find(notification) != -1:
#             return 'diadiem'

#     for notification in list_thoigian_notification:
#         if message.lower().find(notification) != -1:
#             return 'thoigian'

#     for notification in list_ketqua_notification:
#         if message.lower().find(notification) != -1:
#             return 'ketqua'

#     for notification in list_thuchien_notification:
#         if message.lower().find(notification) != -1:
#             return 'thuchien'

#     for notification in list_giayto_notification:
#         if message.lower().find(notification) != -1:
#             return 'giayto'

#     return 'none'


# def get_name_tthc(message):
#     if 'lĩnh vực' in message.lower():
#         filter_message = re.sub(r"^.*?(lĩnh vực)", '', message.lower())
#         type_name = TYPE_NAME_SEARCH_TTHC.LINH_VUC
#         return [filter_message, type_name]

#     if 'của' in message.lower():
#         filter_message = re.sub(r"^.*?(của)", '', message.lower())
#         type_name = TYPE_NAME_SEARCH_TTHC.CO_QUAN
#         return [filter_message, type_name]

#     filter_message = re.sub(
#         r"^.*?((thủ tục)|(cách làm)|(cách))", '', message.lower())
#     type_name = TYPE_NAME_SEARCH_TTHC.THU_TUC
#     return [filter_message, type_name]


def preprocess_message(message):
    message = re.sub(
        '[\:\_=\+\#\@\$\%\$\\(\)\~\@\;\'\|\<\>\]\[\"\–“”…*]', ' ', message)

    message = message.lower()
    message = message.replace(',', ' , ')
    message = message.replace('.', ' . ')
    message = message.replace('!', ' ! ')
    message = message.replace('&', ' & ')
    message = message.replace('?', ' ? ')
    message = message.replace('(', ' ( ')
    message = message.replace(')', ' ) ')
    message = compound2unicode(message)
    list_token = message.split(' ')
    while '' in list_token:
        list_token.remove('')
    message = ' '.join(list_token)
    return message


def compound2unicode(text):
    # https://gist.github.com/redphx/9320735`
    text = text.replace("\u0065\u0309", "\u1EBB")  # ẻ
    text = text.replace("\u0065\u0301", "\u00E9")  # é
    text = text.replace("\u0065\u0300", "\u00E8")  # è
    text = text.replace("\u0065\u0323", "\u1EB9")  # ẹ
    text = text.replace("\u0065\u0303", "\u1EBD")  # ẽ
    text = text.replace("\u00EA\u0309", "\u1EC3")  # ể
    text = text.replace("\u00EA\u0301", "\u1EBF")  # ế
    text = text.replace("\u00EA\u0300", "\u1EC1")  # ề
    text = text.replace("\u00EA\u0323", "\u1EC7")  # ệ
    text = text.replace("\u00EA\u0303", "\u1EC5")  # ễ
    text = text.replace("\u0079\u0309", "\u1EF7")  # ỷ
    text = text.replace("\u0079\u0301", "\u00FD")  # ý
    text = text.replace("\u0079\u0300", "\u1EF3")  # ỳ
    text = text.replace("\u0079\u0323", "\u1EF5")  # ỵ
    text = text.replace("\u0079\u0303", "\u1EF9")  # ỹ
    text = text.replace("\u0075\u0309", "\u1EE7")  # ủ
    text = text.replace("\u0075\u0301", "\u00FA")  # ú
    text = text.replace("\u0075\u0300", "\u00F9")  # ù
    text = text.replace("\u0075\u0323", "\u1EE5")  # ụ
    text = text.replace("\u0075\u0303", "\u0169")  # ũ
    text = text.replace("\u01B0\u0309", "\u1EED")  # ử
    text = text.replace("\u01B0\u0301", "\u1EE9")  # ứ
    text = text.replace("\u01B0\u0300", "\u1EEB")  # ừ
    text = text.replace("\u01B0\u0323", "\u1EF1")  # ự
    text = text.replace("\u01B0\u0303", "\u1EEF")  # ữ
    text = text.replace("\u0069\u0309", "\u1EC9")  # ỉ
    text = text.replace("\u0069\u0301", "\u00ED")  # í
    text = text.replace("\u0069\u0300", "\u00EC")  # ì
    text = text.replace("\u0069\u0323", "\u1ECB")  # ị
    text = text.replace("\u0069\u0303", "\u0129")  # ĩ
    text = text.replace("\u006F\u0309", "\u1ECF")  # ỏ
    text = text.replace("\u006F\u0301", "\u00F3")  # ó
    text = text.replace("\u006F\u0300", "\u00F2")  # ò
    text = text.replace("\u006F\u0323", "\u1ECD")  # ọ
    text = text.replace("\u006F\u0303", "\u00F5")  # õ
    text = text.replace("\u01A1\u0309", "\u1EDF")  # ở
    text = text.replace("\u01A1\u0301", "\u1EDB")  # ớ
    text = text.replace("\u01A1\u0300", "\u1EDD")  # ờ
    text = text.replace("\u01A1\u0323", "\u1EE3")  # ợ
    text = text.replace("\u01A1\u0303", "\u1EE1")  # ỡ
    text = text.replace("\u00F4\u0309", "\u1ED5")  # ổ
    text = text.replace("\u00F4\u0301", "\u1ED1")  # ố
    text = text.replace("\u00F4\u0300", "\u1ED3")  # ồ
    text = text.replace("\u00F4\u0323", "\u1ED9")  # ộ
    text = text.replace("\u00F4\u0303", "\u1ED7")  # ỗ
    text = text.replace("\u0061\u0309", "\u1EA3")  # ả
    text = text.replace("\u0061\u0301", "\u00E1")  # á
    text = text.replace("\u0061\u0300", "\u00E0")  # à
    text = text.replace("\u0061\u0323", "\u1EA1")  # ạ
    text = text.replace("\u0061\u0303", "\u00E3")  # ã
    text = text.replace("\u0103\u0309", "\u1EB3")  # ẳ
    text = text.replace("\u0103\u0301", "\u1EAF")  # ắ
    text = text.replace("\u0103\u0300", "\u1EB1")  # ằ
    text = text.replace("\u0103\u0323", "\u1EB7")  # ặ
    text = text.replace("\u0103\u0303", "\u1EB5")  # ẵ
    text = text.replace("\u00E2\u0309", "\u1EA9")  # ẩ
    text = text.replace("\u00E2\u0301", "\u1EA5")  # ấ
    text = text.replace("\u00E2\u0300", "\u1EA7")  # ầ
    text = text.replace("\u00E2\u0323", "\u1EAD")  # ậ
    text = text.replace("\u00E2\u0303", "\u1EAB")  # ẫ
    text = text.replace("\u0045\u0309", "\u1EBA")  # Ẻ
    text = text.replace("\u0045\u0301", "\u00C9")  # É
    text = text.replace("\u0045\u0300", "\u00C8")  # È
    text = text.replace("\u0045\u0323", "\u1EB8")  # Ẹ
    text = text.replace("\u0045\u0303", "\u1EBC")  # Ẽ
    text = text.replace("\u00CA\u0309", "\u1EC2")  # Ể
    text = text.replace("\u00CA\u0301", "\u1EBE")  # Ế
    text = text.replace("\u00CA\u0300", "\u1EC0")  # Ề
    text = text.replace("\u00CA\u0323", "\u1EC6")  # Ệ
    text = text.replace("\u00CA\u0303", "\u1EC4")  # Ễ
    text = text.replace("\u0059\u0309", "\u1EF6")  # Ỷ
    text = text.replace("\u0059\u0301", "\u00DD")  # Ý
    text = text.replace("\u0059\u0300", "\u1EF2")  # Ỳ
    text = text.replace("\u0059\u0323", "\u1EF4")  # Ỵ
    text = text.replace("\u0059\u0303", "\u1EF8")  # Ỹ
    text = text.replace("\u0055\u0309", "\u1EE6")  # Ủ
    text = text.replace("\u0055\u0301", "\u00DA")  # Ú
    text = text.replace("\u0055\u0300", "\u00D9")  # Ù
    text = text.replace("\u0055\u0323", "\u1EE4")  # Ụ
    text = text.replace("\u0055\u0303", "\u0168")  # Ũ
    text = text.replace("\u01AF\u0309", "\u1EEC")  # Ử
    text = text.replace("\u01AF\u0301", "\u1EE8")  # Ứ
    text = text.replace("\u01AF\u0300", "\u1EEA")  # Ừ
    text = text.replace("\u01AF\u0323", "\u1EF0")  # Ự
    text = text.replace("\u01AF\u0303", "\u1EEE")  # Ữ
    text = text.replace("\u0049\u0309", "\u1EC8")  # Ỉ
    text = text.replace("\u0049\u0301", "\u00CD")  # Í
    text = text.replace("\u0049\u0300", "\u00CC")  # Ì
    text = text.replace("\u0049\u0323", "\u1ECA")  # Ị
    text = text.replace("\u0049\u0303", "\u0128")  # Ĩ
    text = text.replace("\u004F\u0309", "\u1ECE")  # Ỏ
    text = text.replace("\u004F\u0301", "\u00D3")  # Ó
    text = text.replace("\u004F\u0300", "\u00D2")  # Ò
    text = text.replace("\u004F\u0323", "\u1ECC")  # Ọ
    text = text.replace("\u004F\u0303", "\u00D5")  # Õ
    text = text.replace("\u01A0\u0309", "\u1EDE")  # Ở
    text = text.replace("\u01A0\u0301", "\u1EDA")  # Ớ
    text = text.replace("\u01A0\u0300", "\u1EDC")  # Ờ
    text = text.replace("\u01A0\u0323", "\u1EE2")  # Ợ
    text = text.replace("\u01A0\u0303", "\u1EE0")  # Ỡ
    text = text.replace("\u00D4\u0309", "\u1ED4")  # Ổ
    text = text.replace("\u00D4\u0301", "\u1ED0")  # Ố
    text = text.replace("\u00D4\u0300", "\u1ED2")  # Ồ
    text = text.replace("\u00D4\u0323", "\u1ED8")  # Ộ
    text = text.replace("\u00D4\u0303", "\u1ED6")  # Ỗ
    text = text.replace("\u0041\u0309", "\u1EA2")  # Ả
    text = text.replace("\u0041\u0301", "\u00C1")  # Á
    text = text.replace("\u0041\u0300", "\u00C0")  # À
    text = text.replace("\u0041\u0323", "\u1EA0")  # Ạ
    text = text.replace("\u0041\u0303", "\u00C3")  # Ã
    text = text.replace("\u0102\u0309", "\u1EB2")  # Ẳ
    text = text.replace("\u0102\u0301", "\u1EAE")  # Ắ
    text = text.replace("\u0102\u0300", "\u1EB0")  # Ằ
    text = text.replace("\u0102\u0323", "\u1EB6")  # Ặ
    text = text.replace("\u0102\u0303", "\u1EB4")  # Ẵ
    text = text.replace("\u00C2\u0309", "\u1EA8")  # Ẩ
    text = text.replace("\u00C2\u0301", "\u1EA4")  # Ấ
    text = text.replace("\u00C2\u0300", "\u1EA6")  # Ầ
    text = text.replace("\u00C2\u0323", "\u1EAC")  # Ậ
    text = text.replace("\u00C2\u0303", "\u1EAA")  # Ẫ
    return text


# def get_name_intent(id):
#     if id == 0:
#         return 'chiphi'
#     if id == 1:
#         return 'diadiem'
#     if id == 2:
#         return 'giayto'
#     if id == 3:
#         return 'ketqua'
#     if id == 4:
#         return 'thoigian'
#     if id == 5:
#         return 'thuchien'
#     return 'none'


def update(a, b):
    a.update(b)
    return a


def flatten(result):
    return list(map(lambda x: reduce(update, x), result))