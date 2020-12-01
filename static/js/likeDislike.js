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


$('.js-vote').click(function(event) {
    event.preventDefault();
    var $this = $(this),
        action = $this.data('action'),
        questionID = $this.data('question_id'),
        answerID = $this.data('answer_id');
    
    console.log(action);

    if (questionID) {
        $.ajax({
            url: '/vote/',
            method: 'POST',
            data: {
                action: action,
                question_id: questionID,
            },
    
            success : function(json) {
                $('#questionRating' + questionID).html(json.question_rating);
                if (json.like_src) {
                    $('#questionLike' + questionID).attr('src', json.like_src);
                    $('#questionLike' + questionID).data('action', json.like_action);
                }
                if (json.dislike_src) {
                    $('#questionDislike' + questionID).attr('src', json.dislike_src);
                    $('#questionDislike' + questionID).data('action', json.dislike_action);
                }

                console.log('Success'); // another sanity check
            },

            error : function(jqXHR, errmsg, err) {
                jsonValue = jQuery.parseJSON(jqXHR.responseText);
                console.log(jqXHR.status + ": " + jsonValue.error);
            },
        });

    } else if (answerID) {
        $.ajax({
            url: '/vote/',
            method: 'POST',
            data: {
                action: action,
                answer_id: answerID,
            },
    
            success : function(json) {
                $('#answerRating' + answerID).html(json.answer_rating);
                if (json.like_src) {
                    $('#answerLike' + answerID).attr('src', json.like_src);
                    $('#answerLike' + answerID).data('action', json.like_action);
                }
                if (json.dislike_src) {
                    $('#answerDislike' + answerID).attr('src', json.dislike_src);
                    $('#answerDislike' + answerID).data('action', json.dislike_action);
                }

                console.log('Success'); // another sanity check
            },

            error : function(jqXHR, errmsg, err) {
                jsonValue = jQuery.parseJSON(jqXHR.responseText);
                console.log(jqXHR.status + ": " + jsonValue.error);
            },
        });
    }
    
    console.log('Voting ended')
});
