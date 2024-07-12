document.getElementById('pdf_file').addEventListener('change', function() {
    // Get the selected file
    const file = this.files[0];
    
    if (file) {
        // Show the text box
        document.getElementById('password').value = '';
        document.getElementById('textcontainer_1').style.display = 'block';
    } 
});

document.getElementById('clickbtn').addEventListener('click', function() {

        
        document.getElementById('textcontainer_1').style.display = 'none';

});

function toggle() {
    var passwordField = document.getElementById("password");
    var toggleCheckbox = document.getElementById("showPassword");

    if (toggleCheckbox.checked) {
        passwordField.type = "text";
    } else {
        passwordField.type = "password";
    }
}

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("submitButton").addEventListener("click", function() {
        document.getElementById("fileInput").value = null;
    });
});