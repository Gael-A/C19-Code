document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("register-form");

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const formData = new FormData(form);

        fetch("/add_announcement", {
            method: "POST",
            body: formData
        })
        .then(response => response.json()) 
        .then(data => {
            if (data.success) {
                alert(data.message);
                window.location.href = "/home";
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            alert("Error inesperado al agregar el anuncio.");
            console.error("Error:", error);
        });
    });
});
