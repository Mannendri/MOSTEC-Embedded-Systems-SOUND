// Updates the image in the iframe every second
window.onload = function() {
    var image = document.getElementById("image");

    function updateImage() {
        image.src = "https://608dev.net/sandbox/mostec_camera/sound?id=1"
    }

    setInterval(updateImage, 1000);
}