$(document).ready(function () {
    function sync_branch () {
        $.ajax({
            xhrFields: {
                withCredentials: true
            },
            type: "POST",
            data: {
                cookie: $('#cookie').val().trim(),
                link: $('#link').val().trim()
            },
            url: 'https://adapter.pos365.vn/tool/sync/branch',
            success: function (r) {
                r.branch.forEach(function (value) {
                    $('#optBranch').append($('<option>', {
                        value: value.Id,
                        text: value.Name
                    }));
                });
                $(`#optBranch option[value=${r.current.Id}]`).attr('selected', 'selected');
                $('#status').empty();
            },
            error: function (e) {
                $('#status').html(e.responseJSON.detail);
            }
        });
    }
    $(document).on('click', '#login365', function (event) {
        $('#status').empty();
        $('#optBranch').empty();
        let link = $('#link').val().trim();
        if (link.length === 0) {
            $('#status').html('Đi đâu vội thế nhập link đã bạn ê!');
            return;
        }
        let user = $('#username').val().trim();
        let password = $('#password').val().trim();
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                // Username: "quantri@pos365.vn",
                // Password: "IT@P0s365kms",
                UserName: user,
                Password: password
            }),
            url: `https://${link}.pos365.vn/api/auth`,
            // timeout: 150000,
            success: function (res) {
                $('#cookie').val(res.SessionId);
                $('#status').html('Họ họ... Đang sync chi nhánh');
                sync_branch();
            },
            error: function (err) {
                console.log(err);
                $('#status').html(err.responseJSON.ResponseStatus.Message);
                // alert(request.responseJSON.ResponseStatus.Message);
            }
        });
    });
    $(document).on('click', '#billID', function (event) {
        $('#status').empty();
        let link = $('#link').val().trim();
        if (link.length === 0) {
            $('#status').html('Đi đâu vội thế nhập link đã bạn ê!');
            return;
        }
        let billCode = $('#billCode').val().trim();
        if (billCode.length === 0) {
            $('#status').html('Đi đâu vội thế chưa có mã đơn hàng bạn ê!');
            return;
        }
        let cookie = $('#cookie').val().trim();
        $.ajax({
            type: "POST",
            url: '/tool/orders',
            data: {
                code: billCode,
                cookie: cookie,
                link: link
            },
            success: function (res) {
                if (res.results.length === 0) {
                    $('#status').html('Không tìm thấy mã đơn hàng bạn ê!');
                    return;
                }
                $('#status').append(`<thead><tr><th class="text-align-center">Id</th><th>Mã đơn hàng</th></tr></thead>`);
                res.results.forEach(function (r) {
                    $('#status').append(`<tr><td>${r.Id}</td><td>${r.Code}</td></tr>`);
                });
                // $('#status').text(res.results[0].Id);
            },
            error: function (err) {
                $('#status').text(err.responseJSON.ResponseStatus.Message);
                // alert(request.responseJSON.ResponseStatus.Message);
            }
        });
    });
    $(document).on('click', '[name="SNOption"]', function (event) {
        let opt = $('[name="SNOption"]:checked').val()
        if (opt === '2') {
            $('#btnSN').attr('rowspan', 2);
            $('#trSNProduct').removeClass('d-none');
        } else {
            $('#btnSN').removeAttr('rowspan');
            $('#trSNProduct').addClass('d-none');
        }
    })
    $(document).on('click', '[name="DelDataOption"]', function (event) {
        let opt = $('[name="DelDataOption"]:checked').val()
        if (opt === '2') {
            $('#btnDelData').attr('rowspan', 2);
            $('#trDelDataOption').removeClass('d-none');
            $('#trDelDataDate').addClass('d-none');
        } else if (opt === '3') {
            $('#btnDelData').attr('rowspan', 2);
            $('#trDelDataDate').removeClass('d-none');
            $('#trDelDataOption').addClass('d-none');
        } else {
            $('#btnDelData').removeAttr('rowspan');
            $('#trDelDataDate').addClass('d-none');
            $('#trDelDataOption').addClass('d-none');
        }
    })
    $(document).on('click', '#btnExtract', function (event) {
        $('#status').empty();
        let type = $('#typeExtract').val();
        let link = $('#link').val().trim();
        let cookie = $('#cookie').val().trim();
        let branch = $('#optBranch').val();
        switch (type) {
            case '1'://hàng hoá
                $.ajax({
                    type: "POST",
                    xhrFields: {
                        withCredentials: true
                    },
                    data: {
                        cookie: cookie,
                        link: link,
                        branch: branch
                    },
                    url: 'https://adapter.pos365.vn/tool/extract/products',
                    success: function (r) {
                        $('#status').html(r);
                        fuck_wss(r);
                    },
                    error: function (e) {
                        $('#status').html(e);
                    }
                });
                break;
            case '2':
                break;
            default:
                $('#status').html('Chưa chọn data cần xuất bạn ê');
                break;

        }
    });
    $(document).on('click', '[name="ImportOption"]', function (event) {
        let opt = $('[name="ImportOption"]:checked').val()
        if (opt === '1') {
            $('#import').html('<input type="text" class="form-control form-control-sm" placeholder="Link Sheet" id="inputImport">');
            // $('#inputSheet').removeClass('d-none');
        } else {
            $('#import').html('<input type="file" class="form-control form-control-sm" id="inputImport">');
            // $('#inputFile').removeClass('d-none');
            // $('#inputSheet').addClass('d-none');
        }
    })
    $(document).on('click', '#btnImport', function (event) {
        $('#status').empty();
        let type = $('#typeImport').val();
        let link = $('#link').val().trim();
        let cookie = $('#cookie').val().trim();
        let branch = $('#optBranch').val();
        switch (type) {
            case '1'://hàng hoá
                $.ajax({
                    type: "POST",
                    xhrFields: {
                        withCredentials: true
                    },
                    data: {
                        cookie: cookie,
                        link: link,
                        branch: branch,
                        type: $('[name="ImportOption"]:checked').val(),
                        data: $('#inputImport').val()
                    },
                    url: 'https://adapter.pos365.vn:6000/tool/import/products',
                    success: function (r) {
                        $('#status').html(r);
                        fuck_wss(r);
                    },
                    error: function (e) {
                        $('#status').html(e);
                    }
                });
                break;
            case '2':
                break;
            default:
                $('#status').html('Chưa chọn data cần xuất bạn ê');
                break;

        }
    });

    // let ws = new WebSocket(`wss://adapter.pos365.vn:6000/ws`);
    // ws.onmessage = function (event) {
    //     console.log(event);
    //     try {
    //         let js = JSON.parse(event.data);
    //         console.log(js);
    //         if (js.status) {
    //             // ws.onclose = function () {};
    //             // ws.close();
    //             // ws.onmessage = function () {};
    //         } else {
    //             $('#messages').html(`${js.progress}%`);
    //         }
    //     } catch {
    //     }
    // };
    // ws.onclose = function (e) {
    //     console.log(e);
    //     console.log('disconnected');
    // };

function fuck_wss(task_id) {
    var ws = new WebSocket(`wss://adapter.pos365.vn/tool/ws?tid=${task_id}`);
    ws.onmessage = function (event) {
        console.log(event);
        let js = JSON.parse(event.data);

        if (js.status) {
            $('#status').html(`<a target="_blank" href="${js.progress}">${js.progress}</a>`);
            // ws.onclose = function () {};
            ws.close();
            // ws.onmessage = function () {};
        } else {
            $('#status').html(`${js.progress}`);
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
});