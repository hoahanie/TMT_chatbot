resp = require("../response/response.js");
request = require("request");
sync = require("sync-request");

var UserController = require("../utils/usercontroller.js");
const CONVERSATION_MANAGER_ENDPOINT = "http://localhost:5000/api/send-message";

var userController = new UserController();

module.exports = function (controller) {
    var promiseBucket = {
        default: [],
    };

    var userMessageCount = {};

    var isRating = {};
    var star = {};
    var appropriate = {}; // "khong_phu_hop", "hoi_thieu", "phu_hop", "hoi_du",
    var catched_intents = {}; //arr type
    var edited_intents = {}; // arr type
    var conversation = {}; // arr type
    var previousNonameRound = 0;
    var currentRound = 0;
    var nonameStreak = 0;

    function isEmpty(obj) {
        for (var key in obj) {
            if (obj.hasOwnProperty(key)) return false;
        }
        return true;
    }

    function store_conversation(id, body, message_text, reply_text){
        data = {}
        // console.log(body[0]);
        // console.log(body[0][0]);
        data['userId'] = id;
        data['datetime'] = new Date();
        data['last_conversation'] = {'type': body[1].type, 'inform_slots': body[0]};
        data['message_text'] = message_text;
        data['reply_text'] = {'bot': reply_text, 'admin': ''};
        console.log('********');
        console.log(data);
    }

    function conductOnboarding(bot, message) {
        bot.startConversation(message, function (err, convo) {
            var id = message.user;
            convo.say({
                text: resp.hello,
            });
            userMessageCount[id] = 0;
            var user = userController.searchSession(id);
            if (user == null) {
                user = userController.insertSession(id, bot);
            }
        });
    }

    function conductReset(bot, message) {
        bot.startConversation(message, function (err, convo) {
            var id = message.user;
            convo.say({
                text: resp.reset,
            });
            userMessageCount[id] = 0;
        });
        var id = message.user;
        var user = userController.searchSession(id);
        if (user == null) {
            user = userController.insertSession(id, bot);
        }
    }

    function continueConversation(bot, message) {
        bot.startConversation(message, function (err, convo) {
            convo.say({
                text: resp.hello,
            });
        });
        var id = message.user;
        var user = userController.searchSession(id);
        if (user == null) {
            user = userController.insertSession(id, bot);
        }
    }

    function restartConversation(bot, message) {
        var id = message.user;
        if (isRating[id] && message.save) {
            console.log("CALL SAVE API HERE");
            body = {
                star: star[id],
                appropriate: appropriate[id],
                catched_intents: catched_intents[id],
                edited_intents: edited_intents[id],
                conversation: conversation[id],
            };
            console.log(JSON.stringify(body));
            request.post(
                RATING_CONVERSATION_ENDPOINT,
                { json: body },
                (err, resp, data) => {
                    if (err) {
                        console.log(err);
                    } else {
                        console.log(data);
                    }
                }
            );
        }
        isRating[id] = false;
        bot.reply(message, { graph: {}, text: resp.thank });
        var success = userController.deleteSession(id);
        if (!success) {
            console.log("Error in delete function");
        } else {
            console.log("Delete success");
        }

        console.log("id " + id);
        if (id) {
            conversation[id] = [];
            var delete_body = sync(
                "DELETE",
                CONVERSATION_MANAGER_ENDPOINT + "?graph_id=" + id
            );
            console.log("DELETE GRAPH CODE:" + delete_body.statusCode);
        }
        setTimeout(() => {
            bot.reply(message, resp.hello);
            userMessageCount[id] = 0;
            userController.deleteSession(id);
        }, 1000);
    }

    // function color_size(bot, message, body) {
    //     bot.reply(message, {
    //         text: resp.cs,
    //     });
    // }
    // function color(bot, message, body) {
    //     bot.reply(message, {
    //         text: resp.c,
    //     });
    // }
    // function size(bot, message, body) {
    //     bot.reply(message, {
    //         text: resp.s,
    //     });
    // }
    function transfer_to_admin(bot, message, body) {
        bot.reply(message, {
            text: resp.transfer_to_admin,
        });
        reply_text = resp.transfer_to_admin;
        store_conversation(message.user, body, message.text, reply_text);
        
    }
    function found_id_product(bot, message, body) {
        bot.reply(message, {
            text: resp.found_id_product + body[0]['product_name'],
        });
        reply_text = resp.found_id_product + body[0]['product_name'];
        store_conversation(message.user, body, message.text, reply_text);
    }

    function rep_hello(bot, message, body){
        reply_text = resp.rep_hello;
        bot.reply(message, {
            text: resp.rep_hello,
        });
        store_conversation(message.user, body, message.text, reply_text);
    }

    function rep_done(bot, message, body){
        bot.reply(message, {
            text: resp.rep_done,
        });
        reply_text = resp.rep_done;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function rep_inform(bot, message, body){
        reply_text = resp.rep_inform + String(body[0]['amount']) + " " + body[0]['product_name'] + " " + body[0]['color'] + " size " + body[0]['size'];
        bot.reply(message, {
            text: reply_text,
        });
        store_conversation(message.user, body, message.text, reply_text);
    }

    function rep_request(bot, message, body){
        bot.reply(message, {
            text: resp.rep_request,
        });
        reply_text = resp.rep_request;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function rep_feedback(bot, message, body){
        bot.reply(message, {
            text: resp.rep_feedback,
        });
        reply_text = resp.rep_feedback;
        store_conversation(message.user, body, message.text, reply_text);
    }

    // Giong rep_inform
    function rep_connect(bot, message, body){
        bot.reply(message, {
            text: resp.rep_connect,
        });
        reply_text = resp.rep_connect;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function rep_order(bot, message, body){
        bot.reply(message, {
            text: resp.rep_order,
        });
    }

    function rep_order_color(bot, message, body){
        reply_text = resp.rep_order_color;
        bot.reply(message, {
            text: resp.rep_order_color,
            product_introduction: body[0]['suggestion'],
        });
        store_conversation(message.user, body, message.text, reply_text);
    }

    function rep_order_size(bot, message, body){
        bot.reply(message, {
            text: resp.rep_order_size,
            product_introduction: body[0]['suggestion'],
        });
        reply_text = resp.rep_order_size;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function rep_order_amount(bot, message, body){
        bot.reply(message, {
            text: resp.rep_order_amount,
            product_introduction: body[0]['suggestion'],
        });
        reply_text = resp.rep_order_amount;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function rep_order_product_name(bot, message, body){
        bot.reply(message, {
            text: resp.rep_order_product_name,
        });
        reply_text = resp.rep_order_product_name;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function rep_changing(bot, message, body){
        bot.reply(message, {
            text: resp.rep_changing,
        });
        reply_text = resp.rep_changing;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function rep_return(bot, message, body){
        bot.reply(message, {
            text: resp.rep_return,
        });
        reply_text = resp.rep_return;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function have_product_name(bot, message, body){
        bot.reply(message, {
            text: resp.have_product_name,
        });
        reply_text = resp.have_product_name;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function nothing(bot, message, body) {
        bot.reply(message, {
            text: resp.n,
        });
    }

    function dont_reg_color(bot, message, body) {
        bot.reply(message, {
            text: resp.dont_reg_color,
        });
        reply_text = resp.dont_reg_color;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function misunderstand_color(bot, message, body) {
        bot.reply(message, {
            text: resp.misunderstand_color,
        });
        reply_text = resp.misunderstand_color;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function misunderstand_size(bot, message, body) {
        bot.reply(message, {
            text: resp.misunderstand_size,
        });
        reply_text = resp.misunderstand_size;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function misunderstand_amount(bot, message, body) {
        bot.reply(message, {
            text: resp.misunderstand_amount,
        });
        reply_text = resp.misunderstand_amount;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function misunderstand_product_name(bot, message, body) {
        bot.reply(message, {
            text: resp.misunderstand_product_name,
        });
        reply_text = resp.misunderstand_product_name;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function not_found_product(bot, message, body) {
        bot.reply(message, {
            text: resp.not_found_product,
        });
        reply_text = resp.not_found_product;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function not_found_product_from_image(bot, message, body) {
        bot.reply(message, {
            text: resp.not_found_product_from_image,
        });
        reply_text = resp.not_found_product_from_image;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function found_lots_products(bot, message, body) {
        bot.reply(message, {
            text: resp.found_lots_products + ' ' + body[0][0],
        });
        reply_text = resp.found_lots_products;
        store_conversation(message.user, body, message.text, reply_text);
    }

    function handleUnknown(bot, message, body) {
        bot.reply(message, {
            text: resp.dontunderstand,
        });
    }

    function handleError(bot, message, body) {
        bot.reply(message, {
            text: resp.err,
        });
    }

    function callConversationManager(bot, message) {
        var body = null;
        var id = message.user;

        var raw_mesg = message.text;
        if (
            new RegExp(
                [
                    "tks",
                    "thanks",
                    "thank",
                    "cảm ơn",
                    "cam on",
                    "cảm ơn bạn",
                    "Cảm ơn",
                    "bye",
                ].join("|")
            ).test(message.text.toLowerCase())
        ) {
            bot.reply(message, {
                text: "Cảm ơn bạn. Hẹn gặp lại!",
                goodbye: true,
            });
            return;
        }
        request.post(
            CONVERSATION_MANAGER_ENDPOINT,
            {
                json: {
                    message: message.text,
                    image: message.image,
                    // state: message.tthc_id ? message.tthc_id : "not_found",
                    userId: id,
                },
            },
            (error, res, body) => {
                if (error) {
                    console.log(error);
                    handleError(bot, message, body);
                    return;
                }
                // console.log(message);
                if (message.user == "master") {
                    // console.log(bot);
                    broadcast(message);
                }
                console.log(message.user)
                switch (body[1].type) {
                    case "color_size":
                        color_size(bot, message, body);
                        break;
                    case "color":
                        color(bot, message, body);
                        break;
                    case "size":
                        size(bot, message, body);
                        break;
                    case "transfer_to_admin":
                        transfer_to_admin(bot, message, body);
                        break;
                    case "found_id_product":
                        found_id_product(bot, message, body);
                        break;
                    case "rep_hello":
                        rep_hello(bot, message, body);
                        break;
                    case "rep_done":
                        rep_done(bot, message, body);
                        break;
                    case "rep_inform":
                        rep_inform(bot, message, body);
                        console.log(body[0])
                        break;
                    case "rep_request":
                        rep_request(bot, message, body);
                        break;
                    case "rep_feedback":
                        rep_feedback(bot, message, body);
                        break;
                    case "rep_connect":
                        rep_connect(bot, message, body);
                        break;
                    case "rep_order":
                        rep_inform(bot, message, body);
                        console.log(body[0])
                        break;
                    case "rep_order_color":
                        rep_order_color(bot, message, body);
                        break;
                    case "rep_order_size":
                        rep_order_size(bot, message, body);
                        break;
                    case "rep_order_amount":
                        rep_order_amount(bot, message, body);
                        break;
                    case "rep_order_product_name":
                        rep_order_product_name(bot, message, body);
                        break;
                    case "rep_changing":
                        rep_changing(bot, message, body);
                        break;
                    case "rep_return":
                        rep_return(bot, message, body);
                        break;
                    case "have_product_name":
                        have_product_name(bot, message, body);
                        break;
                    case "nothing":
                        nothing(bot, message, body);
                        break;
                    case "dont_reg_color":
                        dont_reg_color(bot, message, body);
                        break;
                    case "misunderstand_color":
                        misunderstand_color(bot, message, body);
                        break;
                    case "misunderstand_size":
                        misunderstand_size(bot, message, body);
                        break;
                    case "misunderstand_amount":
                        misunderstand_amount(bot, message, body);
                        break;
                    case "misunderstand_product_name":
                        misunderstand_product_name(bot, message, body);
                        break;
                    case "not_found_product":
                        not_found_product(bot, message, body);
                        break;

                    case "not_found_product_from_image":
                        not_found_product_from_image(bot, message, body);
                        break;

                    case "found_lots_products":
                        found_lots_products(bot, message, body);
                        break;
                    default:
                        handleUnknown(bot, message, body);
                }
            }
        );

        var user = userController.searchSession(id);
        if (user == null) {
            user = userController.insertSession(id, bot);
        }
        // console.log(id);
        if (raw_mesg) {
            if (conversation[message.user]) {
                conversation[message.user].push("user: " + raw_mesg);
            } else {
                conversation[message.user] = ["user: " + raw_mesg];
            }
        }
        if (message.quit) {
            restartConversation(bot, message);
            return;
        }

        // if (message.completed) {
        //     bot.reply(message, {
        //         text: resp.goodbye[Math.floor(Math.random() * resp.goodbye.length)],
        //         force_result: [
        //             {
        //                 title: 'Bắt đầu hội thoại mới',
        //                 payload: {
        //                     'restart_conversation': true
        //                 }
        //             }
        //         ]
        //     });
        //     var success = userController.deleteSession(id);
        //     if (!success) {
        //         console.log("Error in delete function");
        //     } else {
        //         console.log("Delete success");
        //     }
        //     return;
        // }
        // if (message.restart_conversation) {
        //     bot.reply(message, {
        //         text: resp.hello
        //     });
        //     return;
        // }
        // if (!promiseBucket[id]) {
        //     promiseBucket[id] = []
        // }
        // var bucket = promiseBucket[id]
        // var pLoading = { value: true };
        // bucket.push(pLoading)

        // if (raw_mesg && raw_mesg.length > 0) {
        //     var messageBack = raw_mesg;
        //     if (message.continueToConversation != undefined && message.continueToConversation != null){
        //         handleInformResponse(bot, message, message.continueToConversation);
        //         return;
        //     }
        //     if (message.userResponeToInform != null){
        //         if (message.userResponeToInform.anything){
        //             userAction = message.userResponeToInform.userAction;
        //             for (var prop in userAction.inform_slots){
        //                 // if (userAction.inform_slots.hasOwnProperty(prop)){
        //                 //     userAction.inform_slots.prop = 'anything'
        //                 // }
        //                 userAction.inform_slots[prop] = 'anything';
        //             }
        //             delete userAction.round;
        //             delete userAction.speaker;
        //             messageBack = userAction;
        //         }
        //         else if (message.userResponeToInform.acceptInform){
        //             userAction = message.userResponeToInform.userAction;
        //             delete userAction.round;
        //             delete userAction.speaker;
        //             messageBack = userAction;
        //         } else {
        //             var enableEditInform = null;
        //             userAction = message.userResponeToInform.userAction;
        //             slot = resp.AGENT_INFORM_OBJECT[Object.keys(userAction.inform_slots)[0]];
        //             var msg = `Vậy ${slot} là gì bạn?`;
        //             if (message.userResponeToInform.enableEditInform != null){
        //                 enableEditInform = message.userResponeToInform.enableEditInform;
        //                 msg = `Vậy bạn điều chỉnh lại thông tin giúp mình nhé!`;
        //             }

        //             bot.reply(message, {
        //                     text: msg,
        //                     enableEditInform : enableEditInform
        //                 });
        //             return;

        //         }
        //     }
        //     if (message.userResponeToMatchfound != null){
        //         if (message.userResponeToMatchfound.acceptMatchfound){
        //             messageBack = {intent: "done", inform_slots:{}, request_slots: {}}
        //         } else {
        //             messageBack = {intent: "reject", inform_slots:{}, request_slots: {}}
        //         }
        //     }
        //     if (message.userEditedInformSlot != null){
        //         userAction = {intent: "inform", request_slots: {}, inform_slots:message.userEditedInformSlot.userInform};
        //         messageBack = userAction;
        //     }
        //     console.log("request action::#########")
        //     console.log(messageBack)
        //     request.post(CONVERSATION_MANAGER_ENDPOINT, {
        //         json: {
        //             message: messageBack,
        //             state_tracker_id: id
        //         }
        //     }, (error, res, body) => {
        //         intent = null;

        //         if (error || res.statusCode != 200) {
        //             console.log(error);
        //             bot.reply(message, {
        //                 text: resp.err
        //             });
        //             return;
        //         }
        //         if (body != null && body.agent_action != null){
        //             console.log(body.agent_action)
        //             currentRound += 1;
        //             switch (body.agent_action.intent){
        //                 case "inform":
        //                     handleInformResponse(bot, message, body);
        //                     break;
        //                 case "match_found":
        //                     console.log(body.agent_action.inform_slots[body.agent_action.inform_slots['activity']])

        //                     handleMatchfoundResponse(bot, message, body);
        //                     break;
        //                 case "done":
        //                     handleDoneResponse(bot, message, body);
        //                     break;
        //                 case "hello":
        //                     handleHelloResponse(bot, message, body);
        //                     break;
        //                 case "no_name":
        //                     handleNonameResponse(bot, message, body);
        //                     break;
        //                 default:
        //                     bot.reply(message, {
        //                         text: body.message
        //                     })
        //             }

        //             return;
        //         }

        //     });

        // }
    }

    function imageProcess(bot, message) {
        console.log("Receive image");
    }

    function masterProcess(bot, message) {
        console.log("Receive master");
    }

    controller.on("hello", conductOnboarding);
    controller.on("welcome_back", continueConversation);
    controller.on("reset", conductReset);
    controller.on("message_received", callConversationManager);
    controller.on("image", imageProcess);
    controller.on("master_message", masterProcess);
    function broadcast(message) {
        console.log(message);
        for (var i = 0; i < userController.listSession.length; i++) {
            if (userController.listSession[i].userId != "master") {
                message.user = userController.listSession[i].userId;
                message.raw_message.user = userController.listSession[i].userId;
                callConversationManager(
                    userController.listSession[i].bot,
                    message
                );
            }
        }
    }
};
