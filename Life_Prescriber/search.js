const searchButton = document.querySelector("#search-button");
searchButton.addEventListener("click", (eventObject) => {
    const dataUrl = eventObject.currentTarget.getAttribute("data-url");
    const searchBox = document.querySelector("#search-box");
    const searchQuery = searchBox.textContent;
    const searchDataUrl = `${dataUrl}?search=${searchQuery}`;
    window.location.href = searchDataUrl;
})