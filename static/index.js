var image = document.getElementById("image");
var time = document.getElementById("time");
var inbox = document.getElementById("inbox");
var input = document.getElementById("message");
var send = document.getElementById("send");

// Updates image, time, and inbox
window.onload = function(){
  // Update image
  function updateImage() {
        image.src = "https://608dev.net/sandbox/mostec_camera/sound?id=1"
  }
  // Update time
  function updateTime(){
      var req = new XMLHttpRequest();
      var url = "https://608dev.net/sandbox/mostec/sound-doorbell?time";
      req.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log("Found good stuff");
            var response = this.responseText;
            var json  = JSON.parse(response); //if needed
            console.log(json);
            time.innerHTML = json["time"];
        }
      }
      req.open("GET", url, true);
      req.send();
    }
  // Update inbox
  function updateInbox(){
      var req = new XMLHttpRequest();
      var url = "https://608dev.net/sandbox/mostec/sound-doorbell?message";
      req.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log("Found good stuff");
            var response = this.responseText;
            var json  = JSON.parse(response); //if needed
            console.log(json);
            inbox.value = json["message"];
        }
      }
      req.open("GET", url, true);
      req.send();
  }
  function updateAllFunctions () {
    updateImage();
    updateTime();
    updateInbox();
  }
  setInterval(updateAllFunctions, 1000);
}

// Makes a POST request when the send button is clicked
function sendMessage(){ 
    message = input.value
    spot = "sound-resident"
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.responseText);
        }
    };
    var post = "https://608dev.net/sandbox/mostec/"+spot+"?message="+message
    console.log(post);
    xhttp.open("POST", post, true);
    xhttp.send();
    input.value = ""
} 
send.addEventListener("click", sendMessage);