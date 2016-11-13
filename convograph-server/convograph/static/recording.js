function captureUserMedia(mediaConstraints, successCallback, errorCallback) {
    navigator.mediaDevices.getUserMedia(mediaConstraints).then(successCallback).catch(errorCallback);
}
var mediaConstraints = {
    audio: true
};

var counter = 0;
var timeInterval;
var recordingType;

// TRAINING
document.querySelector('#training-recording #start-recording').onclick = function() {
    //this.disabled = true;
    timeInterval = 3 * 1000;
    recordingType = 'training';
    captureUserMedia(mediaConstraints, onMediaSuccess, onMediaError);
};
// CONVO
document.querySelector('#convo-recording #start-recording').onclick = function() {
    //this.disabled = true;
    timeInterval = 20 * 60 * 1000;
    recordingType = 'convo';
    captureUserMedia(mediaConstraints, onMediaSuccess, onMediaError);
};
document.querySelector('#convo-recording #stop-recording').onclick = function() {
    //this.disabled = true;
    mediaRecorder.stop();
    mediaRecorder.stream.stop();
    document.querySelector('#convo-recording #start-recording').disabled = false;
};

var mediaRecorder;

function onMediaSuccess(stream) {
    counter += 1;
    mediaRecorder = new MediaStreamRecorder(stream);
    mediaRecorder.stream = stream;

    mediaRecorder.recorderType = StereoAudioRecorder;
    mediaRecorder.mimeType = 'audio/wav';

    mediaRecorder.audioChannels = 1; //!!document.getElementById('left-channel').checked ? 1 : 2;
    mediaRecorder.start(timeInterval);
    mediaRecorder.ondataavailable = function(blob) {
        mediaRecorder.stop();
        //mediaRecorder.save();
        // post it!
        var fd = new FormData();
        var filename = (recordingType == 'training') ? ('sample' + counter + '.wav') : ('convo.wav')
        fd.append('filename', filename);
        fd.append('type', recordingType);
        fd.append('data', blob);
        $.ajax({
            type: 'POST',
            url: '/post',
            data: fd,
            processData: false,
            contentType: false
        }).done(function(data) {
            console.log("done posting!");
        });
    };
}

function onMediaError(e) {
    console.error('media error', e);
}

var index = 1;
// below function via: http://goo.gl/B3ae8c
function bytesToSize(bytes) {
    var k = 1000;
    var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 Bytes';
    var i = parseInt(Math.floor(Math.log(bytes) / Math.log(k)), 10);
    return (bytes / Math.pow(k, i)).toPrecision(3) + ' ' + sizes[i];
}

// below function via: http://goo.gl/6QNDcI
function getTimeLength(milliseconds) {
    var data = new Date(milliseconds);
    return data.getUTCHours() + " hours, " + data.getUTCMinutes() + " minutes and " + data.getUTCSeconds() + " second(s)";
}

window.onbeforeunload = function() {
    //document.querySelector('#training-recording #start-recording').disabled = false;
};
