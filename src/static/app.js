// @ts-check

window.addEventListener("load", () => {
    let fps = +localStorage.getItem("fps") || 10;

    document.body.querySelectorAll(".camera").forEach((e, id) => {
        /** @type {HTMLImageElement} */
        const frame = e.querySelector(".frame");

        async function getFrame() {
            const start = Date.now();

            const response = await fetch(`frame/${id}`);
            /** @type {{ image: string | null }} */
            const data = await response.json();
            if (data.image) {
                frame.src = data.image;
            } else {
                console.warn("could not get image");
            }

            const end = Date.now();
            const sleepTime = 1000 / fps - (end - start);
            setTimeout(getFrame, Math.max(sleepTime, 0));
        }

        getFrame();

        emitter.on("fpsChanged", (/** @type {{ fps: number }} */e) => {
            fps = e.fps;
        });
    });

    const selector = document.getElementById("fpsSelector");
    if (!(selector instanceof HTMLSelectElement)) {
        throw new Error("fpsSelector is not a select!");
    }

    selector.value = fps.toString();

    selector.addEventListener("input", e => {
        const newFps = selector.value;
        localStorage.setItem("fps", newFps);
        emitter.emit("fpsChanged", { fps: newFps });
    });

    const toggleRecording = document.getElementById("toggleRecording");
    if (!(toggleRecording instanceof HTMLButtonElement)) {
        throw new Error("toggleRedcording is not a button!");
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
});

function Emitter() {
    /** @type {{ [key: string]: ((e) => void)[] }} */
    this._listeners = {}
}

Emitter.prototype.on = function(type, func) {
    if (!(type in this._listeners)) {
        this._listeners[type] = [];
    }

    const listeners = this._listeners[type];
    listeners.push(func);
}

Emitter.prototype.emit = function(type, event) {
    const listeners = this._listeners[type];
    if (!listeners) { return; }

    for (const listener of listeners) {
        listener(event);
    }
}

const emitter = new Emitter();
