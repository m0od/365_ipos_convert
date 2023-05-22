$(document).ready(function () {
    $(document).on('click', '#optBranch', function () {
       $.ajax({
            type: "POST",
            data: {
                cookie: $('#cookie').val().trim(),
                link: $('#link').val().trim()
            },
            url: '/Config/VendorSession',
            success: function (r) {
                r.branch.forEach(function (value){
                    $('#optBranch').append($('<option>', {
                        value: value.Id,
                        text: value.Name
                    }));
                });
                $(`#optBranch option[value=${r.current.Id}]`).attr('selected','selected');
                $('#status').text('Làm gì thì làm tớ mệt rồi!')
            },
            error: function (e){
                console.log('aaaaa');
                $('#status').html(e);
            }
        });
    });
    $(document).on('click', '#login365', function (event) {
        $('#status').empty();
        $('#optBranch').empty();
        let link = $('#link').val().trim();
        if (link.length === 0){
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
                $('#optBranch').click();
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
    $(document).on('click', '[name="SNOption"]', function (event){
        let opt = $('[name="SNOption"]:checked').val()
        if (opt === '2'){
            $('#btnSN').attr('rowspan',2);
            $('#trSNProduct').removeClass('d-none');
        }else{
            $('#btnSN').removeAttr('rowspan');
            $('#trSNProduct').addClass('d-none');
        }
    })
    $(document).on('click', '[name="DelDataOption"]', function (event){
        let opt = $('[name="DelDataOption"]:checked').val()
        if (opt === '2'){
            $('#btnDelData').attr('rowspan',2);
            $('#trDelDataOption').removeClass('d-none');
            $('#trDelDataDate').addClass('d-none');
        }else if(opt === '3'){
            $('#btnDelData').attr('rowspan',2);
            $('#trDelDataDate').removeClass('d-none');
            $('#trDelDataOption').addClass('d-none');
        }
        else{
            $('#btnDelData').removeAttr('rowspan');
            $('#trDelDataDate').addClass('d-none');
            $('#trDelDataOption').addClass('d-none');
        }
    })
    $(document).on('click', '#btnExtract', function (event){
        $('#status').empty();
        let type = $('#typeExtract').val();
        let link = $('#link').val().trim();
        let cookie = $('#cookie').val().trim();
        let branch = $('#optBranch').val();
        switch (type) {
            case '1'://hàng hoá
                $.ajax({
                    type: "POST",
                    data: {
                        cookie: cookie,
                        link: link,
                        branch: branch
                    },
                    url: '/api/extract/products',
                    success: function (r) {
                        $('#status').html(r)
                    },
                    error: function (e){
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
});