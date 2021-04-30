
$("#fredagsbarmailtekster").change(function () {
    var id = $(this).children(":selected").attr("id");
    $.get("./getfredagsbarmailtext/" + id, function (data) {
        $("#mailtext").html(data);
    });
});

$("#fredagsbarsmstekster").change(function () {
    var id = $(this).children(":selected").attr("id");
    $.get("./getfredagsbarsmstext/" + id, function (data) {
        $("#smstext").html(data);
    });
});

$("#medlemsmailtekster").change(function () {
    var id = $(this).children(":selected").attr("id");
    $.get("./getmedlemsmailtext/" + id, function (data) {
        $("#mailtext").html(data);
    });
});

$("#medlemssmstekster").change(function () {
    var id = $(this).children(":selected").attr("id");
    $.get("./getmedlemssmstext/" + id, function (data) {
        $("#smstext").html(data);
    });
});
