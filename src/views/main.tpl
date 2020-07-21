<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

        <script>
            var segmentLengthSeconds = {{ segmentLengthSeconds }};
        </script>
        <script src="static/app.js"></script>

        <title>Camera Streamer</title>

        <style>
            #camera {
                text-align: center;
                max-height: 90vh;
                max-width: 90vw;

                border: 1px solid lightgrey;
            }

            #toggleRecording {
                text-align: center;
            }
        </style>
    </head>

    <body>
        <video id="camera" controls=""></video>
            
        <button id="toggleRecording">
            {{ "Stop" if isRecording else "Start" }} Recording
        </button>
        </div>
    </body>
</html>
