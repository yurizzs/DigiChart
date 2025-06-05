document.addEventListener('DOMContentLoaded', function() {
    const menuItems = document.querySelectorAll('.menu-item');
      
      // Get current path
    const currentPath = window.location.pathname;
      
      // Set active class based on current path
    menuItems.forEach(item => {
        if (item.getAttribute('href') === currentPath) {
          item.classList.add('bg-[#84e5ff]');
        }
        
        // Add click event listener
        item.addEventListener('click', function() {
          // Remove active class from all items
          menuItems.forEach(i => i.classList.remove('bg-[#84e5ff]'));
          // Add active class to clicked item
          this.classList.add('bg-[#84e5ff]');
        });
    });
});