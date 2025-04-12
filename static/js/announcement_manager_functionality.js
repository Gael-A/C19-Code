document.addEventListener("DOMContentLoaded", () => {
    // Funcionalidad para eliminar imágenes
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", async (event) => {
            const card = event.target.closest(".image-card");
            const cardId = card.id || "";

            if (!cardId) {
                alert("Error: No se encontró el ID de la imagen.");
                return;
            }
            if (confirm("¿Está seguro de eliminar este anuncio?")) {
                // Enviar solicitud para eliminar la imagen
                try {
                    const response = await fetch("/delete_announcement", {
                        method: "POST",
                        headers: { "Content-Type": "application/x-www-form-urlencoded" },
                        body: `uidd=${encodeURIComponent(cardId)}`
                    });

                    const result = await response.json();
                    alert(result.message);

                    // Si la eliminación fue exitosa, quitar la tarjeta del DOM
                    if (result.success) {
                        card.remove();
                    }
                } catch (error) {
                    alert("Error al comunicarse con el servidor.");
                }
            }
        });
    });

    // Funcionalidad para editar imágenes
    document.querySelectorAll(".edit-btn").forEach(button => {
        button.addEventListener("click", (event) => {
            const card = event.target.closest(".image-card");
            window.location.href = "/announcement_edit?uidd=" + card.id;
        });
    });
});
