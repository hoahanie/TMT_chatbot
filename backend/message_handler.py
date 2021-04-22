import re
import numpy as np 
import pandas as pd 

from sklearn.feature_extraction.text import TfidfVectorizer  
from sklearn.model_selection import train_test_split
from entity import get_entity_sq_from_list_pt, pattern_list
from product_handler import suggest_product, get_product_from_ID
from sklearn import svm,metrics
import pickle
import joblib

import re  
# import nltk 
# nltk.download('stopwords')  
# from nltk.corpus import stopwords 
import unidecode

import json
from functools import reduce

def catch_intent(message):
    message = preprocess_message(message)
    return predict_message(message)

def catch_image(product_ID):
    print('*****')
    print(product_ID)
    res = {}
    if not product_ID: #Cannot regconize the image
        res['not_found_product_from_image'] = None
    else:
        # product_names = []
        # for ele in products:
        #     ele_name = get_entity_sq_from_list_pt(pattern_list['product_name'], ele['product_name'].lower(), 'product_name')
        #     if ele_name:
        #         product_names += [ele['product_name'].lower()[ele_name[0][0]:ele_name[0][1]]]
        # print('++++')
        # print(product_names)
        # if len(product_names) == 1:
        #     suggestion = suggest_product(product_names[0], '', '', '')
        #     if not suggestion:
        #         res['not_found_product'] = None
        #     else:
        #         res['rep_order_color'] = {'color': '','size': '','amount': '','product_name': product_names[0],'suggestion': suggestion}
        # else:
        #     # ['a','b','c'] -> 'a, b, c'
        #     product_string = reduce(lambda x,y: x+' hay là '+y, product_names[1:],product_names[0])
        #     res['found_lots_products'] = product_string
        #     print(product_string)
        

        # product_color = get_product_from_ID(product_ID)[0]['product_color']
        product_name = get_product_from_ID(product_ID)
        suggestion = suggest_product(product_name, '', '', '')
        res['rep_order_color'] = {'color': '','size': '','amount': '','product_name': product_name,'suggestion': suggestion}
    return res

def catch_image_intent(product_ID, message):
    res = {}
    if not product_ID: #Cannot regconize the image
        res['not_found_product_from_image'] = None
    else:
        product_name = get_product_from_ID(product_ID)
        suggestion = suggest_product(product_name, '', '', '')

        if not suggestion:
            res['not_found_product'] = None
        else:
            res['have_product'] = {'color': '','size': '','amount': '','product_name': product_name,'suggestion': suggestion}
        # res['rep_order_color'] = {'color': '','size': '','amount': '','product_name': product_name,'suggestion': suggestion}
    return res


def get_entity_from_message(message):
    color = get_entity_sq_from_list_pt(pattern_list['color_product'], message, 'color_product')
    size = get_entity_sq_from_list_pt(pattern_list['size'], message, 'size')
    amount = get_entity_sq_from_list_pt(pattern_list['amount_product'], message, 'amount_product')
    product_name = get_entity_sq_from_list_pt(pattern_list['product_name'], message, 'product_name')

    weight = get_entity_sq_from_list_pt(pattern_list['weight customer'], message, 'weight_customer')
    height = get_entity_sq_from_list_pt(pattern_list['height customer'], message, 'height_customer')
    v1 = get_entity_sq_from_list_pt(pattern_list['v1'], message, 'v1_customer')
    v2 = get_entity_sq_from_list_pt(pattern_list['v2'], message, 'v2_customer')
    v3 = get_entity_sq_from_list_pt(pattern_list['v3'], message, 'v3_customer')


    color = message[color[0][0]:color[0][1]] if color else []
    size = message[size[0][0]:size[0][1]] if size else []
    amount = message[amount[0][0]:amount[0][1]] if amount else []
    product_name = message[product_name[0][0]:product_name[0][1]] if product_name else []
    weight = message[weight[0][0]:weight[0][1]] if weight else []
    height = message[height[0][0]:height[0][1]] if height else []
    v1 = message[v1[0][0]:v1[0][1]] if v1 else []
    v2 = message[v2[0][0]:v2[0][1]] if v2 else []
    v3 = message[v3[0][0]:v3[0][1]] if v3 else []
    
    return color, size, amount, product_name, weight, height, v1, v2, v3

def amount_to_int(amount):
    amount_index = get_entity_sq_from_list_pt(pattern_list['number'], amount, 'number')
    # return amount_index
    if not amount_index:
        ls_count = ['một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười']
        for ele in ls_count:
            if ele in amount.lower():
                return ls_count.index(ele) + 1
        return 0
    else:
        return int(amount[amount_index[0][0]:amount_index[0][1]])

def predict_message(message):
    with open('db.json', 'rb') as json_data:
        conversation_history = json.loads(json_data.read())
    
    res = {}

    # ------------------------- SPECIAL CASES -----------------------

    # 1. Ask about shop info (this can be either request or inform)
    # For example: Tôi muốn tìm hiểu thêm về doanh nghiệp -> inform
    #  Doanh nghiệp bán những sản phẩm gì vậy ? -> request

    # ------------------------                --------------------

    X_corp = np.array([message])

    # Check intent by svm multiclass model

    intent_list = ['hello', 'done', 'inform', 'request', 'feedback', 'connect', 'order', 'changing', 'return']
    tfidfconverter = pickle.load(open('tfidf.pickle', 'rb'))
    
    clf = pickle.load(open('hungne', 'rb'))
    X_corp_tfidf = tfidfconverter.transform(X_corp).toarray()
    y_corp_pred = clf.predict(X_corp_tfidf)
    intent = int(y_corp_pred[0])
    print(intent_list[intent])
    if intent >= 0 and intent <= 8:
        intent = intent_list[intent]

        last_order = {}
        if conversation_history:
                for ele in ['found_id_product',
                            'rep_hello',
                            'rep_done',
                            'rep_inform',
                            'rep_request',
                            'rep_feedback',
                            'rep_connect',
                            'rep_order', 'rep_order_product_name', 'rep_order_color','rep_order_size', 'rep_order_amount',
                            'have_product', 'dont_have_product',
                            'misunderstand_color',
                            'misunderstand_size',
                            'misunderstand_amount',
                            'misunderstand_product_name']:
                    if ele in conversation_history[-1]:
                        last_order = conversation_history[-1][ele]
                        break

        if intent in ['inform', 'order', 'request']:
            color, size, amount, product_name, weight, height, v1, v2, v3 = get_entity_from_message(message)

            print('+++++++++')
            print(message)
            print(weight)
            print(height)
            print(v1)
            print(v2)
            print(v3)

            # normalize weight
            if weight:
                weight_index = get_entity_sq_from_list_pt(pattern_list['number'], message, 'weight_number')
                weight = weight[weight_index[0][0]:weight_index[0][1]]
                weight = int(weight)
            else:
                weight = 0

            # normalize size: convert size s/xl/m/xXL -> S/XL/M/XXL, ao khoac S -> S...
            if size:
                for word in ['size', 'sai', 'sz']:
                    if word in size:
                        size = size[size.index(word)+len(word)+1:]
                        break
                if product_name:
                    if product_name in size:
                        size = size[size.index(product_name)+len(product_name)+1:]
                size = size.upper()
        
            # if size:
            #     if 'xxl' in size.lower():
            #         size = 'XXL'
            #     elif 'xl' in size.lower():
            #         size = 'XL'
            #     elif 'l' in size.lower():
            #         size = 'L'
            #     elif 'm' in size
            #     elif 's' in size.lower():
            #         size = 'S'
            if amount:
                amount = amount_to_int(amount)
            
            # print('**********')
            # print(size)
            # print(last_order)
            new_order = [color, size, amount, product_name]
            ls_feature = ['color', 'size', 'amount', 'product_name']
            if last_order:
                for idx in range(len(ls_feature)):
                    if last_order[ls_feature[idx]]:
                        # Consider misunderstand about ls_feature[idx]
                        if type(last_order[ls_feature[idx]]) is not list:
                            if new_order[idx] and new_order[idx] != last_order[ls_feature[idx]]:
                                res['misunderstand_' + ls_feature[idx]] = {}
                                for ele in range(len(ls_feature)):
                                    if ele == idx:
                                        res['misunderstand_' + ls_feature[idx]][ls_feature[ele]] = [new_order[ele], last_order[ls_feature[ele]]]
                                    else:
                                        # print('hehehehehe')
                                        # print(last_order)
                                        # print(idx)
                                        res['misunderstand_' + ls_feature[idx]][ls_feature[ele]] = last_order[ls_feature[ele]] if last_order[ls_feature[ele]] else new_order[ele]
                                # res['misunderstand_' + ls_feature[idx]] = ls_res
                                # print('------------')
                                # print(res)
                                return res
                            new_order[idx] = last_order[ls_feature[idx]]



            
            print(new_order)
            print('*********')

            color, size, amount, product_name = new_order[0], new_order[1], new_order[2], new_order[3]
            if 'màu' in color:
                color = color[color.index('màu')+4:] # normalize 'màu xxx' -> 'xxx'
            print(amount)
            print(color)
            print(size)
            print(product_name)
        
        if intent in ['inform', 'order']:
            if not product_name:
                # res['rep_order_product_name'] = {'color': color,'size': size,'amount': amount,'product_name': product_name}
                print("INFORM")
                res['dontunderstand'] = None
            elif not color:
                suggestion = suggest_product(product_name, color, size, amount)
                if not suggestion:
                    res['not_found_product'] = None
                # elif len(suggestion == 1):

                else:
                    res['rep_order_color'] = {'color':color,'size': size,'amount': amount,'product_name': product_name,'suggestion': suggestion}
            elif not size:
                suggestion = suggest_product(product_name, color, size, amount)
                if not suggestion:
                    res['not_found_product'] = None
                else:
                    res['have_product'] = {'color':color,'size': size,'amount': amount,'product_name': product_name,'suggestion': suggestion}
            elif not amount:
                suggestion = suggest_product(product_name, color, size, amount)
                # print('+++++')
                # print(product_name, color, size, amount)
                if not suggestion:
                    res['not_found_product'] = None
                else:
                    res['rep_order_amount'] = {'color':color,'size': size,'amount': amount,'product_name': product_name,'suggestion': suggestion}
            else:
                print('hehehehe')
                print(amount)
                suggestion = suggest_product(product_name, color, size, amount)
                if not suggestion:
                    res['not_found_product'] = None
                else:
                    res['rep_' + intent] = {'color':color,'size': size,'amount': amount,'product_name': product_name}
        
        elif intent in ['request']: # request

            # check_reject = get_entity_sq_from_list_pt(pattern_list['reject'], message, 'reject')
            # if last_order:
            #     if check_reject:
            #     # if ('rep_order' in conversation_history[-1] or 'rep_inform' in conversation_history[-1]) and check_reject:
            #         print('REJECT')
            #         res['transfer_to_admin'] = None
            #     else:
            #         res['have_product_name'] = last_order
            # else:
            #     print("REQUESTTTTTTT")
            #     res['dontunderstand'] = None

            check_product = get_entity_sq_from_list_pt(pattern_list['check_product'], message, 'check_product')
            if check_product:
                if not product_name:
                    res['dont_have_product'] = new_order if new_order else None
                else:
                    suggestion = suggest_product(product_name, color, size, amount)
                    if not suggestion:
                        res['not_found_product'] = None
                    else:
                        res['have_product'] = {'color':color,'size': size,'amount': amount,'product_name': product_name,'suggestion': suggestion}
            else:
                print("REQUESTTTTTTT")
                res['dontunderstand'] = None
            
        else:
            res['rep_' + intent] = None
    else:
        res['nothing'] = None
    
    return res


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