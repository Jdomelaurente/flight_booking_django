const fs = require('fs');

function checkTags(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const openDiv = (content.match(/<div/g) || []).length;
    const closeDiv = (content.match(/<\/div>/g) || []).length;
    const openTemplate = (content.match(/<template/g) || []).length;
    const closeTemplate = (content.match(/<\/template>/g) || []).length;
    const openAside = (content.match(/<aside/g) || []).length;
    const closeAside = (content.match(/<\/aside>/g) || []).length;
    const openMain = (content.match(/<main/g) || []).length;
    const closeMain = (content.match(/<\/main>/g) || []).length;
    const openSection = (content.match(/<section/g) || []).length;
    const closeSection = (content.match(/<\/section>/g) || []).length;

    console.log(`File: ${filePath}`);
    console.log(`  div: ${openDiv} ${openDiv === closeDiv ? '✅' : '❌'} (O: ${openDiv}, C: ${closeDiv})`);
    console.log(`  template: ${openTemplate} ${openTemplate === closeTemplate ? '✅' : '❌'} (O: ${openTemplate}, C: ${closeTemplate})`);
    console.log(`  aside: ${openAside} ${openAside === closeAside ? '✅' : '❌'} (O: ${openAside}, C: ${closeAside})`);
    console.log(`  main: ${openMain} ${openMain === closeMain ? '✅' : '❌'} (O: ${openMain}, C: ${closeMain})`);
    console.log(`  section: ${openSection} ${openSection === closeSection ? '✅' : '❌'} (O: ${openSection}, C: ${closeSection})`);
}

const files = [
    'c:/Users/Crissaunt/Documents/GitHub/fbs-vue/bookingapp/src/views/booking/AddonsView.vue',
    'c:/Users/Crissaunt/Documents/GitHub/fbs-vue/bookingapp/src/views/booking/SeatSelectionView.vue',
    'c:/Users/Crissaunt/Documents/GitHub/fbs-vue/bookingapp/src/views/booking/PaymentView.vue'
];

files.forEach(checkTags);
