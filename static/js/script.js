document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".btn").forEach(function(button) {
        button.addEventListener("click", function(event) {
            if (button.classList.contains("download-btn")) {
                let confirmDownload = confirm("Do you want to download this PDF report?");
                if (!confirmDownload) {
                    event.preventDefault();
                }
            }
        });
    });
});
