let spinner
let waiting
let game
let red_name
let green_name
let remaining_red
let remaining_green
let timer

function removeRock() {
    spinner.show()
    $.ajax({
        type: 'POST',
        url: "/rock",
        contentType: "application/json",
        dataType: 'json'
    }).done(function (data) {
        console.log(data);
        spinner.hide()
    });
}

function endGame() {
    spinner.show()
    $.ajax({
        type: 'POST',
        url: "/end",
        contentType: "application/json",
        dataType: 'json'
    }).done(function (data) {
        console.log(data);
        spinner.hide()
        window.location.replace('/')
    });
}

$(function () {
    spinner = $('#spinner')
    waiting = $('#waiting')
    game = $('#game')
    red_name = $('#red_name')
    green_name = $('#green_name')
    remaining_red = $('#remaining_red')
    remaining_green = $('#remaining_green')
    timer = $('#timer')
    waiting.show()
    game.hide()
    spinner.hide()
    spinner.hide()
    let dataInterval = setInterval(function () {
        let timerInterval
        $.ajax({
            type: 'GET',
            url: "/stream",
            contentType: "application/json",
            dataType: 'json'
        }).done(function (data) {
            console.log(data);
            if (data['red_name'] && data['green_name']) {
                red_name.html(data['red_name'])
                green_name.html(data['green_name'])
                remaining_red.html(data['red'])
                remaining_green.html(data['green'])
                game.show()
                spinner.hide()
                waiting.hide()
                /*let start_time = new Date(data['start_time'])
                let diffrence = new Date() - start_time;
                let timer_val = 90 - Math.floor(diffrence / 1000)
                timerInterval = setInterval(function () {
                    timer.html(timer_val + ' seconds remaining')
                }, 1000)*/
            }
            if (!data['red_name']) {
                clearInterval(dataInterval)
                window.location.replace('/')
            }
        });
    }, 3000);
})