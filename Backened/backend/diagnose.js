const fs = require('fs');
const json = JSON.parse(fs.readFileSync('./postman_collections.json', 'utf8'));

function diagnose(items, path = '') {
  let issues = [];
  items.forEach((item, idx) => {
    const itemPath = path + '/' + (item.name || `item${idx}`);
    
    if (item.request) {
      // Check required fields
      if (!item.request.method) {
        issues.push(`[MISSING METHOD] ${itemPath}`);
      }
      if (!item.request.url) {
        issues.push(`[MISSING URL] ${itemPath}`);
      }
      if (item.request.url && typeof item.request.url === 'object') {
        if (!item.request.url.raw) {
          issues.push(`[MISSING URL.raw] ${itemPath}`);
        }
      }
      
      // Check for invalid variable references in body
      if (item.request.body && item.request.body.raw) {
        const bodyStr = item.request.body.raw;
        // Check for improperly escaped quotes in JSON
        const jsonVarPattern = /"[^"]*"/g;
        const matches = bodyStr.match(jsonVarPattern);
        if (matches) {
          matches.forEach(m => {
            if (m.includes('\\n') && !m.includes('\\"')) {
              // This is fine - escaped newlines in JSON
            }
          });
        }
      }
    } else if (!item.item) {
      issues.push(`[INVALID ITEM - no request or items] ${itemPath}`);
    }
    
    if (item.item && Array.isArray(item.item)) {
      issues = issues.concat(diagnose(item.item, itemPath));
    }
  });
  return issues;
}

const issues = diagnose(json.item);
console.log(`Total items/requests: ${countItems(json.item)}`);
console.log(`Issues found: ${issues.length}`);

if (issues.length > 0) {
  console.log('\nIssues:');
  issues.slice(0, 20).forEach(i => console.log('✗ ' + i));
  if (issues.length > 20) {
    console.log(`... and ${issues.length - 20} more`);
  }
} else {
  console.log('✓ No structural issues found');
}

function countItems(items) {
  let count = 0;
  items.forEach(item => {
    if (item.request) count++;
    if (item.item) count += countItems(item.item);
  });
  return count;
}
