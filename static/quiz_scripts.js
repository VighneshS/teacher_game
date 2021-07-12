let spinner
let question
let waiting
let quiz
let student_name
let teacher_name
let gameId
let time_elapsed

const question_id = '{{question_id}}'
const student_answer = '{{student_answer}}'
const score_sent = '{{score_sent}}'
const last_question = '{{last_question}}'
const quiz_div = `
<label for="question{{question_id}}"><strong>Question {{question_id}}: </strong></label>
    <input id="question{{question_id}}" type="text">
    <input id="save_question_btn{{question_id}}" class="btn btn-primary" value="Submit" onclick="saveQuestion({{question_id}}, '#question{{question_id}}')" type="button"><br>
    <label for="last_question{{question_id}}"><strong>Question Last sent to student: </strong><span
            id="last_question{{question_id}}">{{last_question}}</span></label><br>
    <label for="answer{{question_id}}"><strong>Answer from student: </strong><span id="answer{{question_id}}">{{student_answer}}</span></label><br>
    <label for="score{{question_id}}"><strong>Score: </strong></label>
    <input id="score{{question_id}}" type="number" max="10" min="1" maxlength="2">
    <input id="save_score{{question_id}}" class="btn btn-primary" value="Submit" onclick="saveScore({{question_id}}, '#score{{question_id}}')" type="button"><br>
    <label for="last_score{{question_id}}"><strong>Score sent to student: </strong><span id="last_score{{question_id}}">{{score_sent}}</span></label><br><br><br>
`

function saveQuestion(id, question_div, callback) {
    question = question_div !== '' ? $(question_div).val() : ''
    let questionAnswer = {}
    spinner.show()
    let payLoad = {
        'question': question,
        'gameId': gameId,
        'id': id
    }
    $.ajax({
        type: 'POST',
        url: "/question",
        contentType: "application/json",
        dataType: 'json',
        data: JSON.stringify(payLoad)
    }).done(function (data) {
        questionAnswer = data
        spinner.hide()
        if (callback) {
            callback(data)
        }
    });
    return questionAnswer
}

function createNewQuestion(id) {
    saveQuestion(id, '', function (questionAnswer) {
        quiz.append(quiz_div.replaceAll(question_id, questionAnswer['id'])
            .replaceAll(student_answer, questionAnswer['answer'])
            .replaceAll(score_sent, questionAnswer['score'])
            .replaceAll(last_question, questionAnswer['question']))
    })

}

function createQuestionsBlock(questionAnswers) {
    quiz.empty()
    for (const questionAnswersKey in questionAnswers) {
        quiz.append(quiz_div.replaceAll(question_id, questionAnswers[questionAnswersKey]['id'])
            .replaceAll(student_answer, questionAnswers[questionAnswersKey]['answer'])
            .replaceAll(score_sent, questionAnswers[questionAnswersKey]['score'])
            .replaceAll(last_question, questionAnswers[questionAnswersKey]['question']))
    }

}

function saveScore(id, score_div_id) {
    spinner.show()
    let payLoad = {
        'score': $(score_div_id).val(),
        'id': id
    }
    $.ajax({
        type: 'POST',
        url: "/score",
        contentType: "application/json",
        dataType: 'json',
        data: JSON.stringify(payLoad)
    }).done(function (data) {
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
        spinner.hide()
        window.location.replace('/')
    });
}

$(function () {
    spinner = $('#spinner')
    question = $('#question')
    waiting = $('#waiting')
    quiz = $('#quiz')
    student_name = $('#student_name')
    teacher_name = $('#teacher_name')
    time_elapsed = $('#time_elapsed')
    waiting.show()
    spinner.hide()
    quiz.hide()
    spinner.hide()

    function sse() {
        let source = new EventSource('/stream');
        source.onmessage = function (e) {
            let data = JSON.parse(e.data)
            gameId = data.id
            if (data['student'] && data['teacher']) {
                student_name.html(data['student']['name'])
                teacher_name.html(data['teacher']['name'])
                let questions = data['questions']
                createQuestionsBlock(questions)
                let countDownDate = new Date(data['created_on']).getTime()
                let x = setInterval(function () {

                    // Get today's date and time
                    let now = new Date().getTime();

                    // Find the distance between now and the count down date
                    let distance = now - countDownDate;

                    // Time calculations for days, hours, minutes and seconds
                    let days = Math.floor(distance / (1000 * 60 * 60 * 24));
                    let hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    let seconds = Math.floor((distance % (1000 * 60)) / 1000);

                    // Display the result in the element with id="demo"
                    time_elapsed.html(days + "d " + hours + "h "
                        + minutes + "m " + seconds + "s ")
                }, 1000);
                quiz.show()
                spinner.hide()
                waiting.hide()
            }

            if (!data['teacher']) {
                source.close()
                window.location.replace('/')
            }

        };
    }

    sse();
})