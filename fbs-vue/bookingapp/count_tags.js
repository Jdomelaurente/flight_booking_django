const fs = require('fs');
const content = fs.readFileSync('c:/Users/Crissaunt/Documents/GitHub/fbs-vue/bookingapp/src/views/booking/SeatSelectionView.vue', 'utf8');
const open = (content.match(/<div/g) || []).length;
const close = (content.match(/<\/div>/g) || []).length;
console.log('Open:', open);
console.log('Close:', close);
