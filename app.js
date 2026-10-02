document.getElementById("folder-form").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent form from submitting normally
    
    var fileInput = document.getElementById("folder-path");
    var folderPath = fileInput.files[0].webkitRelativePath; // Get the selected file path
    
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/upload");
    xhr.setRequestHeader("Content-Type", "multipart/form-data");
    var formData = new FormData();
    formData.append("folder_path", folderPath);
    xhr.send(formData); // Send the selected file path to the backend Python script
});
