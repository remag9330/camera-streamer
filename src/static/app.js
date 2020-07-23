// @ts-check

/** @type number */
var segmentLengthSeconds = window["segmentLengthSeconds"];

window.addEventListener("load", () => {
    const toggleRecording = document.getElementById("toggleRecording");
    if (!(toggleRecording instanceof HTMLButtonElement)) {
        throw new Error("toggleRecording is not a button!");
    }

    toggleRecording.addEventListener("click", async e => {
        const isStarting = toggleRecording.innerHTML.toUpperCase().indexOf("START") >= 0;

        toggleRecording.disabled = true;
        const result = await fetch("recording/" + (isStarting ? "start" : "stop"));
        toggleRecording.disabled = false;

        if (!result.ok) {
            alert("Error starting recording");
        } else {
            toggleRecording.innerHTML = (isStarting ? "Stop" : "Start") + " Recording";
        }
    });

    const video = document.getElementById("camera");
    if (!(video instanceof HTMLVideoElement)) {
        throw new Error("#camera is not a video!");
    }

    const ms = new MediaSource();
    const url = URL.createObjectURL(ms);
    video.src = url;

    ms.addEventListener("sourceopen", async() => {
        const sb = ms.addSourceBuffer('video/mp4; codecs="avc1.640016, mp4a.40.2"');
        sb.addEventListener("updateend", () => sb.timestampOffset += segmentLengthSeconds);

        let lastReceivedSegment = "";

        async function appendSegment() {
            /** @type Record<string, string> */
            const headers = {};
            if (lastReceivedSegment) {
                headers["X-last-received-segment"] = lastReceivedSegment;
            }

            const res = await fetch("segment", {
                headers: headers,
            });
            
            const segName = res.headers.get("X-segment-name");
            if (lastReceivedSegment === segName) {
                return false;
            }

            const buf = await res.arrayBuffer();
            if (buf.byteLength === 0) {
                return false;
            }
            
            lastReceivedSegment = segName;

            sb.appendBuffer(buf);
            return true;
        }

        while (true) {
            const startTime = Date.now();
            await appendSegment();
            const endTime = Date.now();
            const totalTimeTaken = endTime - startTime;

            const delayMs = segmentLengthSeconds * 250;
            await delay(delayMs - totalTimeTaken);
        }
    });
});

/**
 * @param {number} ms 
 */
function delay(ms) {
    ms = Math.max(ms, 0);
    return new Promise((res, rej) => setTimeout(res, ms));
}
