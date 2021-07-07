let spinner
let name

function saveTeacherName() {
    spinner.show()
    let payLoad = {
        'name': name.val()
    }
    $.ajax({
        type: 'POST',
        url: "/name",
        contentType: "application/json",
        dataType: 'json',
        data: JSON.stringify(payLoad)
    }).done(function (data) {
        console.log(data);
        spinner.hide()
        window.location.replace('/')
    });
}

$(function () {
    spinner = $('#spinner')
    name = $('#name')
    spinner.hide()
})