const fs = require('fs');
const json = JSON.parse(fs.readFileSync('./postman_collections.json', 'utf8'));

function convertURLs(items) {
  items.forEach(item => {
    if (item.request && typeof item.request.url === 'string') {
      item.request.url = { raw: item.request.url };
    }
    if (item.item && Array.isArray(item.item)) {
      convertURLs(item.item);
    }
  });
}

convertURLs(json.item);
fs.writeFileSync('./postman_collections.json', JSON.stringify(json, null, 2));
console.log('✓ Converted all URLs to proper Postman format');
