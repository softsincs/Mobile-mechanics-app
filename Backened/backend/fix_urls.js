const fs = require('fs');
const json = JSON.parse(fs.readFileSync('./postman_collections.json', 'utf8'));

function parseURL(urlString) {
  // Remove {{}} and parse the base URL
  let url = urlString.replace('{{base_url}}', 'http://localhost:8000');
  
  try {
    const urlObj = new URL(url);
    const pathParts = urlObj.pathname.split('/').filter(p => p);
    
    return {
      raw: urlString,
      protocol: urlObj.protocol.replace(':', ''),
      host: urlObj.hostname === 'localhost' ? ['localhost'] : urlObj.host.split('.'),
      port: urlObj.port || (urlObj.protocol === 'https:' ? '443' : '80'),
      path: pathParts
    };
  } catch (e) {
    return {
      raw: urlString
    };
  }
}

function convertURLStructure(items) {
  items.forEach(item => {
    if (item.request && item.request.url && typeof item.request.url === 'object' && item.request.url.raw) {
      const parsed = parseURL(item.request.url.raw);
      item.request.url = parsed;
    }
    if (item.item && Array.isArray(item.item)) {
      convertURLStructure(item.item);
    }
  });
}

convertURLStructure(json.item);
fs.writeFileSync('./postman_collections.json', JSON.stringify(json, null, 2));
console.log('✓ Converted URLs to full Postman structure with protocol, host, port, path');
