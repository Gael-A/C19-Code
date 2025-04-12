document.addEventListener('DOMContentLoaded', function () {
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    const content = document.querySelector('.content');
    const navbar = document.querySelector('.navbar');

    // Ajusta la altura del menú móvil según su contenido
    function adjustMobileMenuHeight() {
        if (mobileMenu.classList.contains('open')) {
            mobileMenu.style.maxHeight = mobileMenu.scrollHeight + "px";
        } else {
            mobileMenu.style.maxHeight = "0";
        }
    }

    // Ajusta el margen superior del contenido principal para que no quede tapado
    function adjustContentMargin() {
        const navHeight = navbar.offsetHeight;
        let menuHeight = mobileMenu.classList.contains('open') ? mobileMenu.scrollHeight : 0;
        content.style.marginTop = (navHeight + menuHeight) + 'px';
    }

    mobileToggle.addEventListener('click', function (e) {
        e.stopPropagation();
        mobileMenu.classList.toggle('open');
        adjustMobileMenuHeight();
        adjustContentMargin();
    });

    // Función para dropdowns (PC y móvil)
    document.querySelectorAll('.dropdown > .dropbtn').forEach(function (button) {
        button.addEventListener('click', function (e) {
            e.stopPropagation();

            // Cierra todos los dropdowns activos excepto el actual
            document.querySelectorAll('.dropdown-content.active').forEach(function (content) {
                if (content !== button.nextElementSibling) {
                    content.classList.remove('active');
                }
            });

            const dropdownContent = button.nextElementSibling;
            dropdownContent.classList.toggle('active');

            // Si el dropdown está dentro del menú móvil, reajusta la altura y el margen
            if (button.closest('.mobile-menu')) {
                adjustMobileMenuHeight();
                adjustContentMargin();
            }
        });
    });

    // Cerrar dropdowns al hacer click fuera
    document.addEventListener('click', function () {
        document.querySelectorAll('.dropdown-content.active').forEach(function (content) {
            content.classList.remove('active');
        });
    });

    // Ajuste inicial del margen del contenido
    adjustContentMargin();

    // Eliminar cuenta del usuario
    const deleteButton = document.getElementById("delete_user");

    if (deleteButton) {
        deleteButton.addEventListener("click", async (event) => {
            event.preventDefault(); // Evita que el enlace recargue la página

            if (!confirm("¿Está seguro de eliminar su cuenta? Esta acción es irreversible.")) {
                return;
            }

            let password = prompt("Ingrese su contraseña para confirmar:");

            if (!password) {
                return;
            }

            try {
                const response = await fetch("/delete_own_account", {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: `password=${encodeURIComponent(password)}`
                });

                const result = await response.json();
                alert(result.message);

                if (result.success) {
                    window.location.href = "/";  // Redirigir a la página principal tras la eliminación
                }
            } catch (error) {
                alert("Error al comunicarse con el servidor.");
            }
        });
    }
});

function checkMenuSize() {
    let mobileMenu = document.querySelector(".mobile-menu");
    let menuHeight = mobileMenu.scrollHeight; // Altura real del menú
    let windowHeight = window.innerHeight; // Altura de la ventana

    if (menuHeight >= windowHeight) {
        document.body.style.overflow = "hidden"; // Bloquea el scroll del contenido principal
        document.body.style.touchAction = "none"; // Bloquea el desplazamiento táctil en móviles
    } else {
        document.body.style.overflow = "";
        document.body.style.touchAction = "";
    }
}

// verifica cuando cambia el tamaño de la pantalla
window.addEventListener("resize", checkMenuSize);

// Animación de engranaje para el menú móvil
document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.getElementById("menu-toggle"); // Asegurar que ID exista
    const gearIcon = document.querySelector(".gear-icon");

    let rotation = 0; // Almacena el ángulo actual de rotación

    menuToggle.addEventListener("click", function () {
        rotation = (rotation === 0) ? 160 : 0; // Alterna entre 0° y 160°
        gearIcon.style.transform = `rotate(${rotation}deg)`; // Aplica la rotación con animación
    });
});

// Duplica el contenido de los elementos con la clase courses y admin-tools
document.addEventListener("DOMContentLoaded", function () {
    const courses = document.getElementsByClassName("courses");
    const adminTools = document.getElementsByClassName("admin-tools");

    courses[1].innerHTML = courses[0].innerHTML;
    adminTools[1].innerHTML = adminTools[0].innerHTML;
});
