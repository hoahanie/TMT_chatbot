import pymongo
import re
# from entity import get_entity_sq_from_list_pt, pattern_list
# myclient = pymongo.MongoClient("mongodb://localhost:27017/")
myclient = pymongo.MongoClient("mongodb+srv://chatbot:tmtchatbot@cluster0.jj9cp.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
mydb = myclient["test_shopping_data"]
mycol = mydb["test_shopping_data"]

# mydoc = mycol.find().sort("product_name")
        

def suggest_product(name, color, size, amount):

    key = '(.)*' + name + '(.)*'
    myquery = { 'product_name': { '$regex': key } }
    # myresult = [{i:ele[i] for i in ele if i!='_id'} for ele in mycol.find(myquery)]
    # print('****')
    # print(len(myresult))
    # print(myresult)
    if color:
        key = '(.)*' + color + '(.)*'
        myquery['color'] = { '$regex': key }
        # myresult = [{i:ele[i] for i in ele if i!='_id'} for ele in mycol.find(myquery)]
    if size and amount:
        # amount = amount_to_int(amount)
        myquery[size] = { "$gte" : amount}
    # print(myquery)
    
    myresult = [{i:ele[i] for i in ele if i!='_id'} for ele in mycol.find(myquery)]
    return myresult if len(myresult) <= 5 else myresult[:5]


    # myquery = { 'product_name': { '$regex': key_name } }
    # list_dict = mycol.find(myquery)
    # if list_dict:
    #     return [ele['product_name'] for ele in list_dict]
    # else:
    #     return []

# def suggest_product_from_color(name, color):
    
# print(suggest_product('áo sơ mi nữ', 'đỏ', 'M', '30'))
    

# print(int(amount_to_int('10 cái')))
# print(x[0][0])