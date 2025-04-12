document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("register-form");

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        // Pedir la contraseña antes de enviar la solicitud
        const password = prompt("Ingrese su contraseña para confirmar los cambios:");

        if (!password) {
            return;
        }

        // Agregar la contraseña al formulario
        const formData = new FormData(form);
        formData.append("password", password);

        fetch("/edit", {
            method: "POST",
            body: formData
        })
        .then(response => response.json()) 
        .then(data => {
            if (data.success) {
                alert(data.message);
                window.location.href = "/";
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error("Error:", error));
    });
});
