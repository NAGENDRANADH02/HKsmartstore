document.addEventListener("DOMContentLoaded", function() {
  const sidebar = document.querySelector('.sidebar');
  const toggleBtn = document.querySelector('#sidebarToggle');

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('d-none');
    });
  }
});
document.addEventListener("DOMContentLoaded", () => {
  const scrollContainers = document.querySelectorAll(".scroll-container");
  
  scrollContainers.forEach(container => {
    let scrollAmount = 0;
    setInterval(() => {
      container.scrollLeft += 1;
      scrollAmount += 1;
      // reset scroll when end reached
      if (container.scrollLeft + container.clientWidth >= container.scrollWidth) {
        container.scrollLeft = 0;
        scrollAmount = 0;
      }
    }, 30); // Adjust speed
  });
});
document.addEventListener("DOMContentLoaded", () => {
  const scrollContainers = document.querySelectorAll(".scroll-container");
  
  scrollContainers.forEach(container => {
    let speed = 0.5; // adjust scroll speed
    let direction = 1;

    function autoScroll() {
      container.scrollLeft += speed * direction;
      if (container.scrollLeft >= container.scrollWidth - container.clientWidth) {
        direction = -1;
      } else if (container.scrollLeft <= 0) {
        direction = 1;
      }
      requestAnimationFrame(autoScroll);
    }

    container.addEventListener("mouseenter", () => direction = 0);
    container.addEventListener("mouseleave", () => direction = 1);
    autoScroll();
  });
});
