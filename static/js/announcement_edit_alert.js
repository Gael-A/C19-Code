document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("register-form");

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        console.log("Formulario enviado");

        const formData = new FormData(form);

        fetch("/update_announcement", {
            method: "POST",
            body: formData
        })
        .then(response => response.json()) 
        .then(data => {
            if (data.success) {
                alert(data.message);
                window.location.href = "/announcement_manager";
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
