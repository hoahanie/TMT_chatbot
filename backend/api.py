from flask import Flask, request, jsonify
from flask_cors import CORS
# from message_handler import catch_intent, get_name_tthc,searchTTHC,flatten
from message_handler import catch_intent, catch_image, catch_image_intent
# from query import get_info
import json
import base64
import requests
import codecs

import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np

# url = "http://103.113.83.51:8001/api/v1.0/imagesearch"

app = Flask(__name__)
CORS(app)

def msg(code, mess=None):
    if code == 200 and mess is None:
        return jsonify({"code": 200, "value": True})
    else:
        return jsonify({"code": code, "message": mess}), code

@app.route('/api/send-message', methods=['POST'])



@app.route('/api/send-message', methods=['POST'])

def send_message():
    input_data = request.json
    with open('db.json', 'rb') as json_data:
        conversation_history = json.loads(json_data.read())
    print(conversation_history)
    
    print(input_data['userId'])
    if "message" not in input_data.keys():
        return msg(400, "Message cannot be None")
    else:
        message = input_data["message"]
        image = False
        if "image" in input_data.keys() and input_data["image"]:
            image = True

            img_string = input_data["image"][input_data["image"].index(',') + 1:]

            imgdata = base64.b64decode( img_string)
            filename = 'test.jpg'  # I assume you have a way of picking unique filenames
            with open(filename, 'wb') as f:
                f.write(imgdata)

            # --------------------- USE MY MODEL --------------------  

            # Disable scientific notation for clarity
            np.set_printoptions(suppress=True)

            # Load the model
            model = tensorflow.keras.models.load_model('keras_model.h5')

            # Create the array of the right shape to feed into the keras model
            # The 'length' or number of images you can put into the array is
            # determined by the first position in the shape tuple, in this case 1.
            data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

            # Replace this with the path to your image
            image = Image.open('test.jpg')

            #resize the image to a 224x224 with the same strategy as in TM2:
            #resizing the image to be at least 224x224 and then cropping from the center
            size = (224, 224)
            image = ImageOps.fit(image, size, Image.ANTIALIAS)

            #turn the image into a numpy array
            image_array = np.asarray(image)

            # display the resized image
            # image.show()

            # Normalize the image
            normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

            # Load the image into the array
            data[0] = normalized_image_array

            # run the inference
            ls_product_ID = ['S002','D005','D006','S006','S009','S005','S003','S008','S004',
            'DS001','D0015','D008','D0010','D0012','D0016','D009','D0011','D0013','D0017',
            'D0014','D004']

            prediction = model.predict(data)
            # print(prediction)
            confident = np.amax(prediction)
            print(confident)

            if confident < 0.8:
                product_ID = ''
            else:
                index = np.where(prediction == confident)[1][0]
                product_ID = ls_product_ID[index]
            print('++++++')
            print(product_ID)

            # --------------------- USE COMPANY's API --------------------------------

            # files=[('files',(open(filename,'rb')))]
            # # data = {'files': open ('/content/drive/MyDrive/a.jpg', 'rb')}
            # result = requests.post(url, files=files)
            # data = json.loads(result.text)
            # products=json.loads(data['result']['data'])
            # print(products)

    if image and not message:
        result = catch_image(product_ID)
    elif message and not image:
        result = catch_intent(message)
    elif message and image:
        result = catch_image_intent(product_ID, message)
    else:
        print('khong gui gi ca')
        result = {}
        result['dontunderstand'] = None
    print("********")
    # print(result)
    conversation_history += [result]
    with codecs.open('db.json', 'w') as reader:
        json.dump(conversation_history, reader)
    


    # if type(result) is dict:
    #     return jsonify([result,{'type': 'found_id_product', 'count': 0}])
    if 'transfer_to_admin' in result:
        return jsonify([[],{'type': 'transfer_to_admin', 'count': 0}])
    # if result=='color_size': 
    #     return jsonify([[],{'type': 'color_size', 'count': 0}])
    # if result=='color':
    #     return jsonify([[],{'type': 'color', 'count': 0}])   
    # if result=='size':
    #     return jsonify([[],{'type': 'size', 'count': 0}])
    if "rep_hello" in result:
        return jsonify([[],{'type': 'rep_hello', 'count': 0}])
    if "rep_done" in result:
        with codecs.open('db.json', 'w') as reader:
            json.dump([], reader)
        return jsonify([[],{'type': 'rep_done', 'count': 0}])
    if "rep_inform" in result:
        # Tong ket don hang
        return jsonify([result['rep_inform'],{'type': 'rep_inform', 'count': 0}])
    if "rep_request" in result:
        return jsonify([[],{'type': 'rep_request', 'count': 0}])
    if "rep_feedback" in result:
        return jsonify([[],{'type': 'rep_feedback', 'count': 0}])
    if "rep_connect" in result:
        return jsonify([[],{'type': 'rep_connect', 'count': 0}])
    if "rep_order" in result:
        return jsonify([result['rep_order'],{'type': 'rep_order', 'count': 0}])
    if "rep_order_color" in result:
        # Gioi thieu nhung san pham co the
        return jsonify([result['rep_order_color'],{'type': 'rep_order_color', 'count': 0}])
    if "rep_order_size" in result:
        # Gioi thieu nhung san pham co the
        return jsonify([result['rep_order_size'],{'type': 'rep_order_size', 'count': 0}])
    if "rep_order_amount" in result:
        # Gioi thieu nhung san pham co the
        return jsonify([result['rep_order_amount'],{'type': 'rep_order_amount', 'count': 0}])
    if "rep_order_product_name" in result:
        return jsonify([[],{'type': 'rep_order_product_name', 'count': 0}])
    if "rep_changing" in result:
        return jsonify([[],{'type': 'rep_changing', 'count': 0}])
    if "rep_return" in result:
        return jsonify([[],{'type': 'rep_return', 'count': 0}])
    if "have_product" in result:
        return jsonify([[result['have_product']],{'type': 'have_product', 'count': 0}])
    if "dont_have_product" in result:
        print('dont_have_product')
        return jsonify([[],{'type': 'dont_have_product', 'count': 0}])
    if "dont_reg_color" in result:
        return jsonify([[],{'type': 'dont_reg_color', 'count': 0}])
    if "misunderstand_color" in result:
        return jsonify([[],{'type': 'misunderstand_color', 'count': 0}])
    if "misunderstand_size" in result:
        return jsonify([[],{'type': 'misunderstand_size', 'count': 0}])
    if "misunderstand_amount" in result:
        return jsonify([[],{'type': 'misunderstand_amount', 'count': 0}])
    if "misunderstand_product_name" in result:
        return jsonify([[],{'type': 'misunderstand_product_name', 'count': 0}])
    if "not_found_product" in result:
        return jsonify([[],{'type': 'not_found_product', 'count': 0}])
    if "not_found_product_from_image" in result:
        return jsonify([[],{'type': 'not_found_product_from_image', 'count': 0}])
    if "found_lots_products" in result:
        return jsonify([[result['found_lots_products']],{'type': 'found_lots_products', 'count': 0}])
    if 'dontunderstand' in result:
        return jsonify([[],{'type': 'dontunderstand', 'count': 0}])
    if 'nothing' in result:
        return jsonify([[],{'type': 'nothing', 'count': 0}])




    # if result == True:
    #     return jsonify([[],{'type': 'True', 'count': 0}])
    # else:
    #     return jsonify([[],{'type': 'False', 'count': 0}])

    # if input_data['state'] == 'not_found':

    #     result = get_name_tthc(message)
    #     query = result[0]
    #     type_database = result[1]
    #     return jsonify(searchTTHC(type_database, query))

    # intent = catch_intent(message)
    # maTTHC = input_data['state']
    # print(maTTHC)

    # [info_result, info_type] = get_info(intent, maTTHC)
    # if(len(info_result) == 0 and intent == 'chiphi'):
    #     return jsonify([[],{'type': 'chiphi', 'count': 0}])

    # if(len(info_result) > 0):
    #     info = list(map(lambda x: list(map(lambda y: {y[0]: y[1]}, x.items())), info_result))
    #     flattern_info = flatten(info)
    #     return jsonify([flattern_info, {'type': intent, 'count': len(flattern_info)}])

    # return jsonify([[],{'type': 'unknown', 'count': 0}])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)