const q75radios = document.querySelectorAll('input[name="9-q75"]')

q75radios.forEach((radio) => {
    radio.addEventListener('change', (event) => {
      const selectedValue = event.target.value; // Get the value of the selected radio button
      if(selectedValue === '0') {
        document.getElementById("q76").style.display = 'block'
      } else {
        document.getElementById("q76").style.display = 'none'
      }
    });
});

const q77radios = document.querySelectorAll('input[name="10-q77"]')

q77radios.forEach((radio) => {
    radio.addEventListener('change', (event) => {
      const selectedValue = event.target.value; // Get the value of the selected radio button
      if(selectedValue === '2') {
        document.getElementById("q78").style.display = 'block'
        document.getElementById("q79").style.display = 'block'
        document.getElementById("q80").style.display = 'block'
        document.getElementById("q81").style.display = 'block'
        document.getElementById("q82").style.display = 'block'
      } else {
        document.getElementById("q78").style.display = 'none'
        document.getElementById("q79").style.display = 'none'
        document.getElementById("q80").style.display = 'none'
        document.getElementById("q81").style.display = 'none'
        document.getElementById("q82").style.display = 'none'
      }
    });
});

const q84radios = document.querySelectorAll('input[name="11-q84"]')

q84radios.forEach((radio) => {
    radio.addEventListener('change', (event) => {
      const selectedValue = event.target.value; // Get the value of the selected radio button
      if(selectedValue === '0') {
        document.getElementById("q85").style.display = 'block'
        document.getElementById("q86").style.display = 'block'
        document.getElementById("q87").style.display = 'block'
      } else {
        document.getElementById("q85").style.display = 'none'
        document.getElementById("q86").style.display = 'none'
        document.getElementById("q87").style.display = 'none'
      }
    });
});

const q105radios = document.querySelectorAll('input[name="14-q105"]')

q105radios.forEach((radio) => {
    radio.addEventListener('change', (event) => {
      const selectedValue = event.target.value; // Get the value of the selected radio button
      if(selectedValue === '2') {
        document.getElementById("q106").style.display = 'block'
        document.getElementById("q107").style.display = 'block'
        document.getElementById("q108").style.display = 'block'
        document.getElementById("q109").style.display = 'block'
        document.getElementById("q110").style.display = 'block'
        document.getElementById("q111").style.display = 'block'
        document.getElementById("q111Heading").style.display = 'block'
        document.getElementById("q112").style.display = 'block'
        document.getElementById("q113").style.display = 'block'
      } else {
        document.getElementById("q106").style.display = 'none'
        document.getElementById("q107").style.display = 'none'
        document.getElementById("q108").style.display = 'none'
        document.getElementById("q109").style.display = 'none'
        document.getElementById("q110").style.display = 'none'
        document.getElementById("q111").style.display = 'none'
        document.getElementById("q111Heading").style.display = 'none'
        document.getElementById("q112").style.display = 'none'
        document.getElementById("q113").style.display = 'none'
      }
    });
});

const q115radios = document.querySelectorAll('input[name="15-q115"]')

q115radios.forEach((radio) => {
    radio.addEventListener('change', (event) => {
      const selectedValue = event.target.value; // Get the value of the selected radio button
      if(selectedValue === '2') {
        document.getElementById("q116").style.display = 'block'
        document.getElementById("q117").style.display = 'block'
        document.getElementById("q118").style.display = 'block'
        document.getElementById("q119").style.display = 'block'
        document.getElementById("q120").style.display = 'block'
        document.getElementById("q120Heading").style.display = 'block'
        document.getElementById("q121").style.display = 'block'
        document.getElementById("q122").style.display = 'block'
      } else {
        document.getElementById("q116").style.display = 'none'
        document.getElementById("q117").style.display = 'none'
        document.getElementById("q118").style.display = 'none'
        document.getElementById("q119").style.display = 'none'
        document.getElementById("q120").style.display = 'none'
        document.getElementById("q120Heading").style.display = 'none'
        document.getElementById("q121").style.display = 'none'
        document.getElementById("q122").style.display = 'none'
      }
    });
});

const q124radios = document.querySelectorAll('input[name="16-q124"]')

q124radios.forEach((radio) => {
    radio.addEventListener('change', (event) => {
      const selectedValue = event.target.value; // Get the value of the selected radio button
      if(selectedValue === '2') {
        document.getElementById("q125").style.display = 'block'
        document.getElementById("q126").style.display = 'block'
      } else {
        document.getElementById("q125").style.display = 'none'
        document.getElementById("q126").style.display = 'none'
      }
    });
});

const q127radios = document.querySelectorAll('input[name="16-q127"]')

q127radios.forEach((radio) => {
    radio.addEventListener('change', (event) => {
      const selectedValue = event.target.value; // Get the value of the selected radio button
      if(selectedValue === '2') {
        document.getElementById("q128").style.display = 'block'
        document.getElementById("q129").style.display = 'block'
        document.getElementById("q130").style.display = 'block'
        document.getElementById("q131").style.display = 'block'
      } else {
        document.getElementById("q128").style.display = 'none'
        document.getElementById("q129").style.display = 'none'
        document.getElementById("q130").style.display = 'none'
        document.getElementById("q131").style.display = 'none'
      }
    });
});

const q134radios = document.querySelectorAll('input[name="17-q134"]')

q134radios.forEach((radio) => {
    radio.addEventListener('change', (event) => {
      const selectedValue = event.target.value; // Get the value of the selected radio button
      if(selectedValue === '2') {
        document.getElementById("q135").style.display = 'block'
        document.getElementById("q135Heading").style.display = 'block'
        document.getElementById("q136").style.display = 'block'
        document.getElementById("q137").style.display = 'block'
        document.getElementById("q138").style.display = 'block'
        document.getElementById("q138Heading").style.display = 'block'
        document.getElementById("q139").style.display = 'block'
        document.getElementById("q140").style.display = 'block'
        document.getElementById("q141").style.display = 'block'
        document.getElementById("q142").style.display = 'block'
      } else {
        document.getElementById("q135").style.display = 'none'
        document.getElementById("q135Heading").style.display = 'none'
        document.getElementById("q136").style.display = 'none'
        document.getElementById("q137").style.display = 'none'
        document.getElementById("q138").style.display = 'none'
        document.getElementById("q138Heading").style.display = 'none'
        document.getElementById("q139").style.display = 'none'
        document.getElementById("q140").style.display = 'none'
        document.getElementById("q141").style.display = 'none'
        document.getElementById("q142").style.display = 'none'
      }
    });
});

const q163radios = document.querySelectorAll('input[name="19-q163"]')

q163radios.forEach((radio) => {
    radio.addEventListener('change', (event) => {
      const selectedValue = event.target.value; // Get the value of the selected radio button
      if(selectedValue === '0') {
        document.getElementById("q164").style.display = 'block'
        document.getElementById("q164q").style.display = 'block'
        document.getElementById("q164Heading").style.display = 'block'
        document.getElementById("q165").style.display = 'block'
        document.getElementById("q166").style.display = 'block'
      } else {
        document.getElementById("q164").style.display = 'none'
        document.getElementById("q164Heading").style.display = 'none'
        document.getElementById("q164q").style.display = 'none'
        document.getElementById("q165").style.display = 'none'
        document.getElementById("q166").style.display = 'none'
      }
    });
});

const q177radios = document.querySelectorAll('input[name="20-q177"]')

q177radios.forEach((radio) => {
    radio.addEventListener('change', (event) => {
      const selectedValue = event.target.value; // Get the value of the selected radio button
      if(selectedValue === '2') {
        document.getElementById("q178").style.display = 'block'
        document.getElementById("q179").style.display = 'block'
        document.getElementById("q179Heading").style.display = 'block'
        document.getElementById("q180").style.display = 'block'
        document.getElementById("q181").style.display = 'block'
      } else {
        document.getElementById("q178").style.display = 'none'
        document.getElementById("q179Heading").style.display = 'none'
        document.getElementById("q179").style.display = 'none'
        document.getElementById("q180").style.display = 'none'
        document.getElementById("q181").style.display = 'none'
      }
    });
});

const q185radios = document.querySelectorAll('input[name="21-q185"]')

q185radios.forEach((radio) => {
    radio.addEventListener('change', (event) => {
      const selectedValue = event.target.value; // Get the value of the selected radio button
      if(selectedValue === '2') {
        document.getElementById("q186").style.display = 'block'
        document.getElementById("q187").style.display = 'block'
      } else {
        document.getElementById("q186").style.display = 'none'
        document.getElementById("q187").style.display = 'none'
      }
    });
});