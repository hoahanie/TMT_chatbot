from flask import Flask, request, jsonify
from flask_cors import CORS
# from message_handler import catch_intent, get_name_tthc,searchTTHC,flatten
from message_handler import catch_intent
# from query import get_info
import json

app = Flask(__name__)
CORS(app)

def msg(code, mess=None):
    if code == 200 and mess is None:
        return jsonify({"code": 200, "value": True})
    else:
        return jsonify({"code": code, "message": mess}), code

@app.route('/api/send-message', methods=['POST'])
def send_message():
    input_data = request.json
    if "message" not in input_data.keys():
        return msg(400, "Message cannot be None")
    else:
        message = input_data["message"]

    result=catch_intent(input_data['message'])
    print("********")
    print(result)

    if result=="color_size": 
        return jsonify([[],{'type': 'color_size', 'count': 0}])
    if result=="color":
        return jsonify([[],{'type': 'color', 'count': 0}])   
    if result=="size":
        return jsonify([[],{'type': 'size', 'count': 0}])
    if result=="nothing":
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
    app.run(debug=True)