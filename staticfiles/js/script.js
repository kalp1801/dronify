document.addEventListener("DOMContentLoaded", function() {
    document.querySelector(".btn").addEventListener("click", function(event) {
        let fileInput = document.getElementById("logFile");
        if (fileInput.files.length === 0) {
            event.preventDefault();
            alert("Please select a file to upload.");
        }
    });
});
