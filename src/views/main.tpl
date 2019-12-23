<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

        <script src="static/app.js"></script>

        <title>Camera Streamer</title>

        <style>
            .camera {
                text-align: center;
            }

            .frame {
                height: 94vh;
            }

            .controls {
                text-align: center;
            }
        </style>
    </head>

    <body>
        % for camera in cameras:
            <div class="camera">
                <img class="frame">
            </div>
        % end

        <div class="controls">
            <select id="fpsSelector">
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="5">5</option>
                <option value="10">10</option>
            </select>
            
            <button id="toggleRecording">
                {{ "Stop" if isRecording else "Start" }} Recording
            </button>
        </div>
    </body>
</html>
