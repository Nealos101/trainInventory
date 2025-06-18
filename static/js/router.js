const currentPath = window.location.pathname;

var paths = {
    ind: "/",
    acc: "/account/",
    inv: "/inventory/",
    help: "/guides/"
};

function redirectTo(path) {
    window.location = path;
}

Object.keys(paths).forEach(function(key) {
    const button = document.getElementById(key + "Btn");
    if (button) {
        button.addEventListener("click", function() {
            redirectTo(paths[key]);
        });
    }
});

Object.keys(paths).forEach(function(key) {
    if (paths[key] === currentPath) {
        const button = document.getElementById(key + "Btn");
        if (button) {
            button.classList.add("headButtonActive");
        }
    }
});