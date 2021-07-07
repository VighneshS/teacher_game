let spinner
let question
let score
let last_score
let last_question
let waiting
let quiz
let student_name
let teacher_name
let answer

function saveQuestion() {
    spinner.show()
    let payLoad = {
        'question': question.val()
    }
    $.ajax({
        type: 'POST',
        url: "/question",
        contentType: "application/json",
        dataType: 'json',
        data: JSON.stringify(payLoad)
    }).done(function (data) {
        console.log(data);
        spinner.hide()
    });
}

function saveScore() {
    spinner.show()
    let payLoad = {
        'score': score.val()
    }
    $.ajax({
        type: 'POST',
        url: "/score",
        contentType: "application/json",
        dataType: 'json',
        data: JSON.stringify(payLoad)
    }).done(function (data) {
        console.log(data);
        spinner.hide()
    });
}

function endQuiz() {
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
    question = $('#question')
    score = $('#score')
    last_question = $('#last_question')
    last_score = $('#last_score')
    waiting = $('#waiting')
    quiz = $('#quiz')
    student_name = $('#student_name')
    teacher_name = $('#teacher_name')
    answer = $('#answer')
    waiting.show()
    spinner.hide()
    quiz.hide()
    spinner.hide()
    let dataInterval = setInterval(function () {
        $.ajax({
            type: 'GET',
            url: "/stream",
            contentType: "application/json",
            dataType: 'json'
        }).done(function (data) {
            console.log(data);
            if (data['student'] && data['teacher']) {
                student_name.html(data['student']['name'])
                teacher_name.html(data['teacher']['name'])
                last_question.html(data['question'])
                last_score.html(data['score'])
                answer.html(data['answer'])
                quiz.show()
                spinner.hide()
                waiting.hide()
            }
            if (!data['teacher']) {
                clearInterval(dataInterval)
                window.location.replace('/')
            }
        });
    }, 10000);
})