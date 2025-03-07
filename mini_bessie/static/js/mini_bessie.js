(async function() {

console.log(data)

  new Chart(
    document.getElementById('miniBessie'),
    {
      type: 'bar',
      options: {
        scales: {
          y: {
            max: 100
          }
        }
      },
      data: {
        labels: data.map(row => row.attr),
        datasets: [
          {
            label: 'Stress and Wellbeing',
            data: data.map(row => row.val)
          }
        ]
      }
    }
  );
})();