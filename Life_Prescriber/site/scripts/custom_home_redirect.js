document.addEventListener("DOMContentLoaded", () => {
    let count = 1
    const intervalID = setInterval(myCallback, 3000);

    function myCallback() {
        // Your code here
        // Parameters are purely optional.
        if (count > 2) {
            clearInterval(intervalID);
            window.location.href = "/prescription_ongo/custom_home/"
        }
        setTimeout(() => {
            document.querySelector(".first").textContent = "."
        }, 100)
        setTimeout(() => {
            document.querySelector(".second").textContent = "."
        }, 500)
        setTimeout(() => {
            document.querySelector(".third").textContent = ".";
            setTimeout(() => {
                allPointSpan = document.querySelectorAll(".points")
                allPointSpan.forEach((element) => {
                    element.textContent = "";
                })
            }, 500)
        }, 1000)
        count++;
    }
})
