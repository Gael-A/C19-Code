document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("register-form");

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const formData = new FormData(form);

        fetch("/edit_course", {
            method: "POST",
            body: formData
        })
        .then(response => response.json()) 
        .then(data => {
            if (data.success) {
                alert(data.message);
                window.location.href = "/course_manager";
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            alert("Error inesperado al editar el curso.");
            console.error("Error:", error);
        });
    });
});
