// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
        }
    }
});


$('.js-mark-correct').click(function(event) {
    event.preventDefault();
    var $this = $(this),
        action = $this.data('action'),
        questionID = $this.data('question_id'),
        answerID = $this.data('answer_id');
    
    console.log(action);

    $.ajax({
        url: '/mark_correct/',
        method: 'POST',
        data: {
            action: action,
            question_id: questionID,
            answer_id: answerID,
        },

        success : function(_json) {
            if ($this.is(':checked')) {
                $this.prop('checked', false);
                $this.data('action', 'uncheck');
                $('#answer' + answerID).removeClass("answer-correct");
            } else {
                $this.prop('checked', true);
                $this.data('action', 'check');
                $('#answer' + answerID).addClass("answer-correct");
            }

            console.log('Marking correctness successfull');
        },

        error : function(jqXHR, _errmsg, _err) {
            jsonValue = jQuery.parseJSON(jqXHR.responseText);
            console.log(jqXHR.status + ": " + jsonValue.error);
        },
    });
    
    console.log('Marking correctness ended')
});
