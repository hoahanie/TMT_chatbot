resp = require("../response/response.js");
request = require("request");
sync = require("sync-request");

var UserController = require("../utils/usercontroller.js");
const CONVERSATION_MANAGER_ENDPOINT = "http://backend:5000/api/send-message";

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

    function handleDoneResponse(bot, message, body) {
        bot.reply(message, {
            text: resp.thank,
            intent: body.agent_action.intent,
        });
    }
    function handleHelloResponse(bot, message, body) {
        bot.reply(message, {
            text: body.message,
            isAbleToSuggest: true,
        });
    }
    function handleNonameResponse(bot, message, body) {
        if (currentRound - previousNonameRound == 1) {
            nonameStreak += 1;
        } else {
            nonameStreak = 0;
        }
        previousNonameRound = currentRound;
        var text = body.message;
        if (nonameStreak > 2) {
            text =
                "Có vẻ như có vấn đề với tên hoạt động mà bạn cung cấp. Vui lòng kiểm tra lại chính xác tên hoặc thử hỏi cách khác bạn nhé!";
            nonameStreak = 0;
        }
        bot.reply(message, {
            text: text,
            isAbleToSuggest: true,
        });
    }
    function handleMatchfoundResponse(bot, message, body) {
        var matchFoundSlot = "activity";
        var enableResponseToMathfound = null;
        var enableEditInform = null;
        var listResults = null;
        if (
            body.agent_action.inform_slots[matchFoundSlot] !=
            "no match available"
        ) {
            keyListResults = body.agent_action.inform_slots[matchFoundSlot];
            listResults = body.agent_action.inform_slots[keyListResults];
            enableResponseToMathfound = [
                {
                    title: "Cảm ơn",
                    payload: {
                        userResponeToMatchfound: {
                            acceptMatchfound: true,
                            userAction: body.agent_action,
                        },
                    },
                },
                {
                    title: "Không thỏa mãn",
                    payload: {
                        userResponeToMatchfound: {
                            acceptMatchfound: false,
                            userAction: body.agent_action,
                        },
                    },
                },
            ];
        } else {
            enableEditInform = body.current_informs;
        }
        bot.reply(message, {
            text: body.message,
            enableResponseToMathfound: enableResponseToMathfound,
            listResults: listResults,
            enableEditInform: enableEditInform,
        });
    }
    function handleInformResponse(bot, message, body) {
        var slot = Object.keys(body.agent_action.inform_slots)[0];
        var enableResponseToConfirm = null;
        var enableEditInform = null;
        // handle show current results send from server
        if (
            "current_results" in body &&
            body.current_results.length > 0 &&
            body.agent_action.round > 2
        ) {
            var enableResponseToCurrentResults = [
                {
                    title: "Đã thỏa mãn",
                    payload: {
                        userResponeToMatchfound: {
                            acceptMatchfound: true,
                            userAction: null,
                        },
                    },
                },
                {
                    title: "Chưa, tiếp tục tư vấn",
                    payload: {
                        continueToConversation: {
                            message: body.message,
                            agent_action: body.agent_action,
                            current_informs: body.current_informs,
                        },
                    },
                },
            ];
            bot.reply(message, {
                text:
                    "Đây là thông tin mình tìm được theo yêu cầu hiện tại của bạn",
                listResults: body.current_results,
                enableResponseToCurrentResults: enableResponseToCurrentResults,
            });
            return;
        } else if (
            body.agent_action.inform_slots[slot] != "no match available"
        ) {
            if (body.agent_action.inform_slots[slot].length == 0) {
                var enableEditInformWhenDenied = null;
                if (body.current_informs != "null")
                    enableEditInformWhenDenied = body.current_informs;
                enableResponseToConfirm = [
                    {
                        title: "Đồng ý",
                        payload: {
                            userResponeToInform: {
                                anything: true,
                                userAction: body.agent_action,
                            },
                        },
                    },
                    {
                        title: "Không",
                        payload: {
                            userResponeToInform: {
                                acceptInform: false,
                                enableEditInform: enableEditInformWhenDenied,
                                userAction: body.agent_action,
                            },
                        },
                    },
                ];
            } else {
                enableResponseToConfirm = [
                    {
                        title: "Đồng ý",
                        payload: {
                            userResponeToInform: {
                                acceptInform: true,
                                userAction: body.agent_action,
                            },
                        },
                    },
                    {
                        title: "Sao cũng được",
                        payload: {
                            userResponeToInform: {
                                anything: true,
                                userAction: body.agent_action,
                            },
                        },
                    },
                    {
                        title: "Không",
                        payload: {
                            userResponeToInform: {
                                acceptInform: false,
                                userAction: body.agent_action,
                            },
                        },
                    },
                ];
            }

            console.log("RESPONSE CONFIRM");
        } else {
            if (body.current_informs != "null")
                enableEditInform = body.current_informs;
        }
        bot.reply(message, {
            text: body.message,
            enableResponseToConfirm: enableResponseToConfirm,
            enableEditInform: enableEditInform,
        });
    }

    function handleListTTHC(bot, message, body) {
        console.log(body[0]);
        bot.reply(message, {
            text: `Tìm thấy các thủ tục liên quan sau. Xin chọn một thủ tục bạn muốn.`,
            choices: body[0].map((e) => {
                return { key: e.MaTTHC, value: e.TenTTHC };
            }),
        });
    }

    function handleSearch(bot, message, body) {
        bot.reply(message, {
            type: "option",
            text: `Tìm thấy ${body.data.count} thủ tục liên quan đến ${body.data.name}. Bạn có muốn xem tất cả?`,
            choices: [
                { key: "1", value: "có" },
                { key: "2", value: "không" },
            ],
        });
    }

    function handleDiaDiem(bot, message, body) {
        bot.reply(message, {
            text:
                "Địa điểm làm thủ tục này là: " + body[0][0].DiaChiTiepNha
                    ? body[0][0].DiaChiTiepNhan
                    : "Không có",
        });
    }

    function handleChiPhi(bot, message, body) {
        if (body[0].length == 0) {
            bot.reply(message, {
                text: "Thủ tục này không mất phí",
            });
        } else {
            bot.reply(message, {
                text: resp.chiphi[0],
                chiphi: body[0],
            });
        }
    }

    function handleThoiGian(bot, message, body) {
        value = body[0][0] ? body[0][0] : null;
        bot.reply(message, {
            text: "Thời gian thực hiện thủ tục là: ",
            thoigian: value,
        });
    }

    function handleKetQua(bot, message, body) {
        bot.reply(message, {
            text: `Bạn sẽ nhận được: ${
                body[0][0].TenKetQua ? body[0][0].TenKetQua : "Không"
            }`,
        });
    }

    function handleThucHien(bot, message, body) {
        bot.reply(message, {
            text: "Quy trình thực hiện là",
            thuchien: body[0],
        });
    }

    // function handleGiayTo(bot, message, body) {
    //     bot.reply(message, {
    //         text: "Giấy tờ cần thiết cho thủ tục này là: ",
    //         giayto: body[0],
    //     });
    // }

    function handleCoQuanLinhVuc(bot, message, body) {
        bot.reply(message, {
            text: `Cơ quan này xử lí ${
                body[1].count
            } thủ tục trong các lĩnh vực : ${body[0]
                .map((e) => e.TenLinhVuc)
                .join(", ")}. Bạn muốn hỏi cụ thể lĩnh vực nào?`,
        });
    }

    function handleCoQuan(bot, message, body) {
        bot.reply(message, {
            text: `Cơ quan này xử lí những thủ tục sau: `,
            choices: body[0].map((e) => {
                return { key: e.MaTTHC, value: e.TenTTHC };
            }),
        });
    }

    function handleLinhVuc(bot, message, body) {
        bot.reply(message, {
            text: `Lĩnh vực này gồm những thủ tục sau: `,
            choices: body[0].map((e) => {
                return { key: e.MaTTHC, value: e.TenTTHC };
            }),
        });
    }
    // function shopping_True(bot, message, body){
    //     bot.reply(message, {
    //         text: resp.True,
    //     });
    // }
    // function shopping_False(bot, message, body){
    //     bot.reply(message, {
    //         text: resp.False,
    //     });
    // }
    function color_size(bot, message, body) {
        bot.reply(message, {
            text: resp.cs,
        });
    }
    function color(bot, message, body) {
        bot.reply(message, {
            text: resp.c,
        });
    }
    function size(bot, message, body) {
        bot.reply(message, {
            text: resp.s,
        });
    }
    function transfer_to_admin(bot, message, body) {
        bot.reply(message, {
            text: resp.transfer_to_admin,
        });
    }
    function found_id_product(bot, message, body) {
        bot.reply(message, {
            text: resp.found_id_product + body[0]['product_name'],
        });
    }

    function rep_hello(bot, message, body){
        bot.reply(message, {
            text: resp.rep_hello,
        });
    }

    function rep_done(bot, message, body){
        bot.reply(message, {
            text: resp.rep_done,
        });
    }

    function rep_inform(bot, message, body){
        bot.reply(message, {
            text: resp.rep_inform + String(body[0][2]) + " " + body[0][3] + " " + body[0][0] + " size " + body[0][1],
        });
    }

    function rep_request(bot, message, body){
        bot.reply(message, {
            text: resp.rep_request,
        });
    }

    function rep_feedback(bot, message, body){
        bot.reply(message, {
            text: resp.rep_feedback,
        });
    }

    // Giong rep_inform
    function rep_connect(bot, message, body){
        bot.reply(message, {
            text: resp.rep_connect,
        });
    }

    function rep_order(bot, message, body){
        bot.reply(message, {
            text: resp.rep_order,
        });
    }

    function rep_order_color(bot, message, body){
        bot.reply(message, {
            text: resp.rep_order_color,
            product_introduction: body[0],
        });
    }

    function rep_order_size(bot, message, body){
        bot.reply(message, {
            text: resp.rep_order_size,
            product_introduction: body[0],
        });
    }

    function rep_order_amount(bot, message, body){
        bot.reply(message, {
            text: resp.rep_order_amount,
            product_introduction: body[0],
        });
    }

    function rep_order_product_name(bot, message, body){
        bot.reply(message, {
            text: resp.rep_order_product_name,
        });
    }

    function rep_changing(bot, message, body){
        bot.reply(message, {
            text: resp.rep_changing,
        });
    }

    function rep_return(bot, message, body){
        bot.reply(message, {
            text: resp.rep_return,
        });
    }

    function have_product_name(bot, message, body){
        bot.reply(message, {
            text: resp.have_product_name,
        });
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
    }

    function misunderstand_color(bot, message, body) {
        bot.reply(message, {
            text: resp.misunderstand_color,
        });
    }

    function misunderstand_size(bot, message, body) {
        bot.reply(message, {
            text: resp.misunderstand_size,
        });
    }

    function misunderstand_amount(bot, message, body) {
        bot.reply(message, {
            text: resp.misunderstand_amount,
        });
    }

    function misunderstand_product_name(bot, message, body) {
        bot.reply(message, {
            text: resp.misunderstand_product_name,
        });
    }

    function not_found_product(bot, message, body) {
        bot.reply(message, {
            text: resp.not_found_product,
        });
    }

    function not_found_product_from_image(bot, message, body) {
        bot.reply(message, {
            text: resp.not_found_product_from_image,
        });
    }

    function found_lots_products(bot, message, body) {
        bot.reply(message, {
            text: resp.found_lots_products + ' ' + body[0][0],
        });
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
        if (message.type === "confirm") {
            bot.reply(message, {
                text: `bạn muốn hỏi gì về  ${message.name}?`,
            });
        }
        console.log(message);
        if (message.tthc_name) {
            bot.reply(message, {
                text: `Bạn đã chọn thủ tục: ${message.tthc_name}. Bạn muốn hỏi gì về thủ tục này?`,
            });
            return;
        }
        request.post(
            CONVERSATION_MANAGER_ENDPOINT,
            {
                json: {
                    message: message.text,
                    image: message.image,
                    state: message.tthc_id ? message.tthc_id : "not_found",
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
                    case "True":
                        shopping_True(bot, message, body);
                        break;
                    case "False":
                        shopping_False(bot, message, body);
                        break;
                    case "tentthc":
                        handleListTTHC(bot, message, body);
                        break;
                    case "coquan_linhvuc":
                        handleCoQuanLinhVuc(bot, message, body);
                        break;
                    case "coquan":
                        handleCoQuan(bot, message, body);
                        break;
                    case "linhvuc":
                        handleLinhVuc(bot, message, body);
                        break;
                    case "thoigian":
                        handleThoiGian(bot, message, body);
                        break;
                    case "chiphi":
                        handleChiPhi(bot, message, body);
                        break;
                    case "diadiem":
                        handleDiaDiem(bot, message, body);
                        break;
                    // case "giayto":
                    //     handleGiayTo(bot, message, body);
                    //     break;
                    case "ketqua":
                        handleKetQua(bot, message, body);
                        break;
                    case "thuchien":
                        handleThucHien(bot, message, body);
                        break;
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
