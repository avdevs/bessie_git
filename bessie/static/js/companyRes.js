// team factor pie charts
let teamEnv = 'absence';

const envFactorsPie = new Chart(
  document.getElementById('pieEnv'),
  {
    type: 'pie',
    options: {
      plugins: {
        legend: {
          position: 'right',
        }
      }
    },
    data : {
      labels: ['Low', 'Medium', 'High', 'Very High'],
      datasets: [
        {
          label: '',
          data: Object.values(environmentFactorsStats[environmentFactorsStats.findIndex(item => item.attr == teamEnv)].val),
          backgroundColor: ['#8fa604', '#ffbf00', '#fb6513', '#ff0000']
        }
      ]
    }
  }
);

const envSelect = document.getElementById("envSelect")

environmentFactorsStats.map(item => {
  let opt = document.createElement("option");
  opt.value = item.attr; // the index
  opt.innerHTML = item.attr.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  envSelect.append(opt);
});

envSelect.addEventListener('change', (event) => {
  teamEnv = event.target.value;
  envFactorsPie.data.datasets[0].data = Object.values(environmentFactorsStats[environmentFactorsStats.findIndex(item => item.attr == teamEnv)].val)
  envFactorsPie.update()
});

let teamH = 'abuse_and_trauma';

const hFactorsPie = new Chart(
  document.getElementById('pieHealth'),
  {
    type: 'pie',
    options: {
      plugins: {
        legend: {
          position: 'right',
        }
      }
    },
    data : {
      labels: ['Low', 'Medium', 'High', 'Very High'],
      datasets: [
        {
          label: '',
          data: Object.values(healthFactorsStats[healthFactorsStats.findIndex(item => item.attr == teamH)].val),
          backgroundColor: ['#8fa604', '#ffbf00', '#fb6513', '#ff0000']
        }
      ]
    }
  }
);

const healthSelect = document.getElementById("healthSelect");

healthFactorsStats.map(item => {
  let opt = document.createElement("option");
  opt.value = item.attr;
  opt.innerHTML = item.attr.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  healthSelect.append(opt);
});

healthSelect.addEventListener('change', (event) => {
  teamH = event.target.value;
  hFactorsPie.data.datasets[0].data = Object.values(healthFactorsStats[healthFactorsStats.findIndex(item => item.attr == teamH)].val)
  hFactorsPie.update()
});

let teamF = 'childcare';

const fFactorsPie = new Chart(
  document.getElementById('pieFamily'),
  {
    type: 'pie',
    options: {
      plugins: {
        legend: {
          position: 'right',
        }
      }
    },
    data : {
      labels: ['Low', 'Medium', 'High', 'Very High'],
      datasets: [
        {
          label: '',
          data: Object.values(familyFactorsStats[familyFactorsStats.findIndex(item => item.attr == teamF)].val),
          backgroundColor: ['#8fa604', '#ffbf00', '#fb6513', '#ff0000']
        }
      ]
    }
  }
);

const familySelect = document.getElementById("familySelect")

familyFactorsStats.map(item => {
  let opt = document.createElement("option");
  opt.value = item.attr;
  opt.innerHTML = item.attr.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  familySelect.append(opt);
});

familySelect.addEventListener('change', (event) => {
  teamF = event.target.value;
  fFactorsPie.data.datasets[0].data = Object.values(familyFactorsStats[familyFactorsStats.findIndex(item => item.attr == teamF)].val)
  fFactorsPie.update()
});

let teamP = 'hobbies';

const pFactorsPie = new Chart(
  document.getElementById('piePersonal'),
  {
    type: 'pie',
    options: {
      plugins: {
        legend: {
          position: 'right',
        }
      }
    },
    data : {
      labels: ['Low', 'Medium', 'High', 'Very High'],
      datasets: [
        {
          label: '',
          data: Object.values(personalFactorsStats[personalFactorsStats.findIndex(item => item.attr == teamP)].val),
          backgroundColor: ['#8fa604', '#ffbf00', '#fb6513', '#ff0000']
        }
      ]
    }
  }
);

const personalSelect = document.getElementById("personalSelect")

personalFactorsStats.map(item => {
  let opt = document.createElement("option");
  opt.value = item.attr;
  opt.innerHTML = item.attr.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  personalSelect.append(opt);
});

personalSelect.addEventListener('change', (event) => {
  teamP = event.target.value;
  pFactorsPie.data.datasets[0].data = Object.values(personalFactorsStats[personalFactorsStats.findIndex(item => item.attr == teamP)].val)
  pFactorsPie.update()
});