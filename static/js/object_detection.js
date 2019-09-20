// Request a new image periodically (time in milliseconds). Setting
// this too results in too much flickering in the webpage.
var imageUpdateInterval = 100;

// Start updating the image periodically.
setInterval(function() {
  var src = "/frames/labelled.jpg?x=" + Math.random();
  $("#markedImage").attr("src", src);

  // Try to synchronize the chart with the new image.
}, imageUpdateInterval);
