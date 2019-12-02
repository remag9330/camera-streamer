// @ts-check

window.addEventListener("load", () => {
    let fps = 10;

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

        setInterval(getFrame, 1000 / fps);
    });
});
