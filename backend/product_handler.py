import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["test_shopping_data"]
mycol = mydb["test_shopping_data"]

# mydoc = mycol.find().sort("product_name")

def suggest_product(name, color):
    key = '(.)*' + name + '(.)*'
    myquery = { 'product_name': { '$regex': key } }
    myresult = [ele for ele in mycol.find(myquery)]
    print('****')
    print(len(myresult))
    print(myresult[0])
    if color:
        key = '(.)*' + color + '(.)*'
        myquery['color'] = { '$regex': key }
        myresult = [ele for ele in mycol.find(myquery)]
        print('-------')
        print(len(myresult))
        print(myresult[0])
    return myresult


    # myquery = { 'product_name': { '$regex': key_name } }
    # list_dict = mycol.find(myquery)
    # if list_dict:
    #     return [ele['product_name'] for ele in list_dict]
    # else:
    #     return []

# def suggest_product_from_color(name, color):
    
suggest_product('áo đôi - áo cặp váy sơ mi nam nữ dành cho cặp đôi du lịch chụp ảnh cưới', 'xanh')
    

#     for x in res:
#     print(x)
