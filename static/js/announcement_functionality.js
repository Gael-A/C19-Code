document.addEventListener("DOMContentLoaded", function() {
    const carousel = document.getElementById("announcement");
    const slidesContainer = carousel.querySelector(".slides");
    const slides = carousel.querySelectorAll(".slide");
    const prevButton = carousel.querySelector(".prev");
    const nextButton = carousel.querySelector(".next");
    
    let currentIndex = 0;
    const intervalTime = 5000; // Tiempo en milisegundos para el cambio automático
    let slideInterval;
  
    function showSlide(index) {
      slidesContainer.style.transform = "translateX(-" + (index * 100) + "%)";
    }
  
    function nextSlide() {
      currentIndex = (currentIndex + 1) % slides.length;
      showSlide(currentIndex);
    }
  
    function prevSlide() {
      currentIndex = (currentIndex - 1 + slides.length) % slides.length;
      showSlide(currentIndex);
    }
  
    // Eventos para los botones
    nextButton.addEventListener("click", () => {
      nextSlide();
      resetInterval();
    });
  
    prevButton.addEventListener("click", () => {
      prevSlide();
      resetInterval();
    });
  
    // Función para iniciar el deslizamiento automático
    function startInterval() {
      slideInterval = setInterval(nextSlide, intervalTime);
    }
  
    // Reinicia el intervalo al interactuar con los botones
    function resetInterval() {
      clearInterval(slideInterval);
      startInterval();
    }
  
    startInterval();
  });
  