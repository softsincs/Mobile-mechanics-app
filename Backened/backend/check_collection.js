const fs = require('fs');
const json = JSON.parse(fs.readFileSync('./postman_collections.json', 'utf8'));

function checkCollection(items, path = '') {
  let errors = [];
  items.forEach((item, idx) => {
    const itemPath = path + '/' + (item.name || 'unnamed');
    
    if (item.request) {
      if (!item.request.url) {
        errors.push('Missing url in request: ' + itemPath);
      }
      if (!item.request.method) {
        errors.push('Missing method in request: ' + itemPath);
      }
    } else if (!item.item) {
      errors.push('No request or item in: ' + itemPath);
    }
    
    if (item.item && Array.isArray(item.item)) {
      errors = errors.concat(checkCollection(item.item, itemPath));
    }
  });
  return errors;
}

const errors = checkCollection(json.item);
if (errors.length > 0) {
  console.log('Found ' + errors.length + ' issues:');
  errors.slice(0, 15).forEach(e => console.log('✗ ' + e));
  if (errors.length > 15) {
    console.log('... and ' + (errors.length - 15) + ' more');
  }
} else {
  console.log('✓ Collection structure looks good');
}
