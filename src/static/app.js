// @ts-check

window.addEventListener("load", () => {
    let fps = +localStorage.getItem("fps") || 10;

    document.body.querySelectorAll(".camera").forEach((e, id) => {
        /** @type {HTMLImageElement} */
        const frame = e.querySelector(".frame");

        async function getFrame() {
            const response = await fetch(`frame/${id}`);
            /** @type {{ image: string | null }} */
            const data = await response.json();
            if (data.image) {
                frame.src = data.image;
            } else {
                console.warn("could not get image");
            }
        }

        let getFrameHandle = setInterval(getFrame, 1000 / fps);
        emitter.on("fpsChanged", (/** @type {{ fps: number }} */e) => {
            clearInterval(getFrameHandle);
            fps = e.fps;
            getFrameHandle = setInterval(getFrame, 1000 / fps);
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
});

class Emitter {
    /** @type {{ [key: string]: ((e) => void)[] }} */
    _listeners = {}

    on(type, func) {
        if (!(type in this._listeners)) {
            this._listeners[type] = [];
        }

        const listeners = this._listeners[type];
        listeners.push(func);
    }

    emit(type, event) {
        const listeners = this._listeners[type];
        if (!listeners) { return; }

        for (const listener of listeners) {
            listener(event);
        }
    }
}
const emitter = new Emitter();
