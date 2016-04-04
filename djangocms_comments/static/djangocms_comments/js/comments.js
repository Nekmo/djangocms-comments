$(function () {
    var cbs = document.getElementsByClassName('comment-box');
    for(var i=0; i < cbs.length; i++){
        autosize(cbs[i].getElementsByTagName('textarea')[0]);
    }
});
