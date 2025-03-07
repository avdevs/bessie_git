(async function() {
    const modalOverlay = document.getElementById('modalOverlay');
    const closeBtn = document.getElementById('closeBtn');
    const acknowledgeBtn = document.getElementById('acknowledgeBtn');
    
    // Function to open modal
    function openModal() {
        modalOverlay.classList.remove('hidden');
    }
    
    function closeModal() {
        modalOverlay.classList.add('hidden');
    }
    
    // Event listeners
    closeBtn.addEventListener('click', closeModal);
    acknowledgeBtn.addEventListener('click', function() {
        setTimeout(closeModal, 1000); // Close after 1 second
    });
    
    // Close modal when clicking outside
    modalOverlay.addEventListener('click', function(event) {
        if (event.target === modalOverlay) {
            closeModal();
        }
    });

    window.addEventListener('load', function() {
        console.log("page loaded")
        setTimeout(openModal, 500);
    });

    new Chart(
      document.getElementById('categoryComp'),
      {
        type: 'radar',
        options: {
            elements: {
                line: {
                    borderWidth: 3
                }
            }
        },
        data: {
            labels: ['Workplace Environment', 'Organisational Policies', 'Leadership approach', 'Training and development', 'Performance Management', 'Workplace Culture', 'Impact assessment', 'Future Planning'],
            datasets: [{
                label: 'Ideal Benchmarks',
                data: [15, 8, 10, 4, 7, 9, 8, 18],
                
            },{
                label: 'Your scores',
                data: res
            }
        ]
        }
      }
    );

    new Chart(
      document.getElementById('progressOverview'),
      {
        type: 'line',
        data: {
            labels: ['Workplace Environment', 'Organisational Policies', 'Leadership approach', 'Training and development', 'Performance Management', 'Workplace Culture', 'Impact assessment', 'Future Planning'],
            datasets: [{
                label: 'Ideal Benchmarks',
                data: [15, 8, 10, 4, 7, 9, 8, 18],
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            },
            {
                label: 'Your scores',
                data: res,
                fill: false,
                borderColor: 'rgb(238, 57, 34)',
                tension: 0.1
            }
        ]
        }   
      }
    );
  })();