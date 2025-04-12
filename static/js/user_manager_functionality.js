document.addEventListener("DOMContentLoaded", () => {
    // Funcionalidad para eliminar cursos
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", async (event) => {
            const row = event.target.closest("tr");
            const courseUID = row.id || "";

            if (!courseUID) {
                alert("Error: No se encontró el ID del usuario.");
                return;
            }
            if (confirm("¿Está seguro de eliminar este usuario? No se puede deshacer.")) {
                try {
                    const response = await fetch("/delete_user", {
                        method: "POST",
                        headers: { "Content-Type": "application/x-www-form-urlencoded" },
                        body: `id=${encodeURIComponent(courseUID)}`
                    });

                    const result = await response.json();
                    alert(result.message);

                    // Si la eliminación fue exitosa, quitar la fila del DOM
                    if (result.success) {
                        row.remove();
                    }
                } catch (error) {
                    alert("Error al comunicarse con el servidor.");
                }
            }
        });
    });

    // Funcionalidad para quitar admin al usuario
    document.querySelectorAll(".admin_remove").forEach(button => {
        button.addEventListener("click", async (event) => {
            const row = event.target.closest("tr");
            const userUID = row.id || "";

            if (!userUID) {
                alert("Error: No se encontró el ID del usuario.");
                return;
            }

            if (confirm("¿Está seguro de quitar admin a este usuario?")) {
                try {
                    const response = await fetch("/update_user_role", {
                        method: "POST",
                        headers: { "Content-Type": "application/x-www-form-urlencoded" },
                        body: `id=${encodeURIComponent(userUID)}&role=remove_admin`
                    });

                    const result = await response.json();
                    alert(result.message);

                    // Si el rol fue actualizado exitosamente, cambiar la interfaz
                    if (result.success) {
                        // Ocultar el botón "Quitar Admin" y mostrar el botón "Hacer Admin"
                        button.style.display = "none";
                        const newButton = row.querySelector(".admin_add");
                        if (newButton) {
                            newButton.style.display = "inline-block";
                        }

                        // Ocultar el icono admin
                        const iconAdmin = row.querySelector(".icon_admin");
                        if (iconAdmin) {
                            iconAdmin.style.display = "none";
                        }
                    }
                } catch (error) {
                    alert("Error al comunicarse con el servidor.");
                }
            }
        });
    });

    // Funcionalidad para dar admin al usuario
    document.querySelectorAll(".admin_add").forEach(button => {
        button.addEventListener("click", async (event) => {
            const row = event.target.closest("tr");
            const userUID = row.id || "";

            if (!userUID) {
                alert("Error: No se encontró el ID del usuario.");
                return;
            }

            if (confirm("¿Está seguro de dar admin a este usuario?")) {
                try {
                    const response = await fetch("/update_user_role", {
                        method: "POST",
                        headers: { "Content-Type": "application/x-www-form-urlencoded" },
                        body: `id=${encodeURIComponent(userUID)}&role=add_admin`
                    });

                    const result = await response.json();
                    alert(result.message);

                    // Si el rol fue actualizado exitosamente, cambiar la interfaz
                    if (result.success) {
                        // Ocultar el botón "Hacer Admin" y mostrar el botón "Quitar Admin"
                        button.style.display = "none";
                        const newButton = row.querySelector(".admin_remove");
                        if (newButton) {
                            newButton.style.display = "inline-block";
                        }

                        // Mostrar el icono admin
                        const iconAdmin = row.querySelector(".icon_admin");
                        if (iconAdmin) {
                            iconAdmin.style.display = "inline-block";
                        }
                    }
                } catch (error) {
                    alert("Error al comunicarse con el servidor.");
                }
            }
        });
    });
});
