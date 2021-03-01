$(document).ready(function() {
    var pollID = $('#poll-data').data('poll-id');

    var currentUserID = $('#poll-data').data('user-id');

    chatSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/poll/'
        + pollID
        + '/'
    );

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        // Here we write the following cases:
        switch(data['message']) {
            // Change in members
            case 'member_change':
                getAjaxReq(fetchPollMembers, 'poll-members')
                break;

            // Start Topic
            case 'topic_created':
                getAjaxReq(fetchCurrentTopic, 'poll-topic')
                $('#vote-box').removeClass('d-none')
                break;

            // End Topic
            case 'topic_ended':
                $('#vote-box').addClass('d-none')
                $('#poll-topic').html('')
                break;

            // Vote Received
            case 'vote_received':
                getAjaxReq(fetchVotingResults, 'poll-results')
                break;
        }
    };

    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };


    chatSocket.onopen = function(event) {
        chatSocket.send(JSON.stringify({
            'action': 'member_change'
        }))
    };

    // Function for get Ajax Requests
    function getAjaxReq(url, divID) {
        $.ajax({
            url: url,
            type: "GET",
            headers: {
                "X-CSRFToken": csrfToken
            },
            success: function (data) {
                $('#'+ divID).html(data)
            }
        });
    }

    // Function for post Ajax Requests
    function postAjaxReq(url, data, successFunction) {
        $.ajax({
            url: url,
            type: "POST",
            data: data,
            headers: {
                "X-CSRFToken": csrfToken
            },
            success: function (data) {
                successFunction()
            }
        });
    }

    // Form Submit Handling
    $('#submit-topic-btn').on('click', function(e) {
        var formData = $('form').serialize()
        postAjaxReq(createTopicUrl, formData, topicCreated)
    })

    $('#submit-vote-btn').on('click', function(e) {
        var formData = $('form').serialize()
        postAjaxReq(submitVoteUrl, formData, voteSubmitted)
    })

    $('#end-topic-btn').on('click', function(e) {
        var formData = $('form').serialize()
        postAjaxReq(endVoteUrl, formData, topicEnded)
    })

    function topicCreated() {
        $('form').trigger("reset");
        chatSocket.send(JSON.stringify({
            'action': 'topic_created'
        }))
        $('#create-topic-form').addClass('d-none');
        $('#end-topic').removeClass('d-none');
    }

    function voteSubmitted() {
        getAjaxReq(fetchVotingResults, 'poll-results')
        chatSocket.send(JSON.stringify({
            'action': 'vote_received'
        }))
    }

    function topicEnded() {
        getAjaxReq(fetchVotingResults, 'poll-results')
        chatSocket.send(JSON.stringify({
            'action': 'topic_ended'
        }))
        $('#create-topic-form').removeClass('d-none');
        $('#end-topic').addClass('d-none');
    }
})