document.addEventListener("DOMContentLoaded", () => {
  // Funcionalidad para eliminar cursos
  document.querySelectorAll(".delete-btn").forEach(button => {
    button.addEventListener("click", async (event) => {
      const row = event.target.closest("tr");
      const courseUID = row.id || "";

      if (!courseUID) {
        alert("Error: No se encontró el ID del curso.");
        return;
      }
      if (confirm("¿Está seguro de eliminar este curso?")) {
        try {
          const response = await fetch("/delete_course", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `uidd=${encodeURIComponent(courseUID)}`
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

  // Funcionalidad para editar cursos
  document.querySelectorAll(".edit-btn").forEach(button => {
    button.addEventListener("click", (event) => {
      const row = event.target.closest("tr");
      window.location.href = "/course_edit?uidd=" + row.id;
    });
  });
});
