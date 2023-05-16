$(document).ready(function () {

    $(document).on('click', '#login365', function (event) {
        $('#status').empty();
        $('#optBranch').empty();
        let link = $('#link').val().trim();
        if (link.length === 0){
            $('#status').html('Đi đâu vội thế nhập link đã bạn ê!');
            return;
        }
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                // Username: "quantri@pos365.vn",
                // Password: "IT@P0s365kms",
                UserName: "admin",
                Password: "123456"
            }),
            url: `https://${link}.pos365.vn/api/auth`,
            // timeout: 150000,
            success: function (res) {
                $('#cookie').val(res.SessionId);
                $('#status').html('Họ họ... Đang sync chi nhánh');
                $.ajax({
                    type: "POST",
                    data: {
                        cookie: res.SessionId,
                        link: link
                    },
                    url: '/Config/VendorSession',
                    success: function (r) {
                        r.branchs.forEach(function (value){
                            $('#optBranch').append($('<option>', {
                                value: value.Id,
                                text: value.Name
                            }));
                        });
                        $(`#optBranch option[value=${r.current.Id}]`).attr('selected','selected');
                        $('#status').text('Làm gì thì làm tớ mệt rồi!')
                    },
                    error: function (e){
                        $('#status').html(e);
                    }
                });
            },
            error: function (err) {
                $('#status').html(err.responseJSON.ResponseStatus.Message);
                // alert(request.responseJSON.ResponseStatus.Message);
            }
        });
    });
    $(document).on('click', '#billID', function (event) {
        $('#status').empty();
        let link = $('#link').val().trim();
        if (link.length === 0){
            $('#status').html('Đi đâu vội thế nhập link đã bạn ê!');
            return;
        }
        let billCode = $('#billCode').val().trim();
        if (billCode.length === 0){
            $('#status').html('Đi đâu vội thế chưa có mã đơn hàng bạn ê!');
            return;
        }
        let cookie = $('#cookie').val().trim();
        $.ajax({
            type: "POST",
            url: '/api/orders',
            data: {
                code: billCode,
                cookie: cookie,
                link: link
            },
            success: function (res){
                if (res.results.length === 0){
                    $('#status').html('Không tìm thấy mã đơn hàng bạn ê!');
                    return;
                }
                $('#status').append(`<thead><tr><th class="text-align-center">Id</th><th>Mã đơn hàng</th></tr></thead>`);
                res.results.forEach(function (r){
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
});