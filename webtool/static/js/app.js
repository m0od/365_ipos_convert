$(document).ready(function () {
    $(document).on('click', '#send', function () {

        $.ajax({
            type: "POST",
            // contentType: "application/json",
            data: {
                // Username: "quantri@pos365.vn",
                // Password: "IT@P0s365kms",
                txt: $('#messageText').val()
            },
            url: `/extract/submit`,
            // timeout: 150000,
            success: function (res) {
                console.log(res.tid);
                // $('#cookie').val(res.tid);
                fuck_wss(res.tid);
            },
            error: function (err) {
                console.log(err);
                // $('#status').html(err.responseJSON.ResponseStatus.Message);
                // alert(request.responseJSON.ResponseStatus.Message);
            }
        });
    });
});

function fuck_wss(task_id) {
    var ws = new WebSocket(`ws://127.0.0.1:6001/ws?task=${task_id}`);
    ws.onmessage = function (event) {
        let js = JSON.parse(event.data);

        if (js.status) {
            // ws.onclose = function () {};
            ws.close();
            // ws.onmessage = function () {};
        }else{
            $('#messages').html(`${js.progress}%`);
        }
    };
    ws.onclose = function () {
        console.log('disconnected');
    };

    // function sendMessage(event) {
    //     var input = document.getElementById("messageText")
    //     ws.send(input.value)
    //     input.value = ''
    //     event.preventDefault()
    // }
}