$(function () {
    /* Auto resize comment textarea */
    var cbs = document.getElementsByClassName('comment-box');
    for(var i=0; i < cbs.length; i++){
        autosize(cbs[i].getElementsByTagName('textarea')[0]);
    }

    $('form.comment-box-form').submit(function (ev) {
        var commentBox = ev.currentTarget;
        var url = $(commentBox).attr('action') + '?ajax=1';
        var postData = $(commentBox).serialize();
        var commentsAndBoxPlugin = $(commentBox).closest('.comments-and-box-plugin');
        var commentsList = $(commentsAndBoxPlugin).find('.comments-list');

        $.post(url, postData, function (data) {
            var $data = $(data);
            var comment = $data.find('.comment-success');
            if(comment){
                $(commentsList).append(comment)
            }
            $('form.comment-box-form').html($data.find('.comment-box-form')[0].innerHTML);
        });
        ev.preventDefault();
    });
});