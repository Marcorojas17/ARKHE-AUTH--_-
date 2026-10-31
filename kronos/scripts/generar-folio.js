// Folio determinista: timestamp + hash de payload
const crypto = require('node:crypto');
function generarFolio(payload) {
  const ts = Date.now().toString(36).toUpperCase();
  const h = crypto.createHash('sha256')
    .update(JSON.stringify(payload)).digest('hex').slice(0, 8).toUpperCase();
  return `KR-${ts}-${h}`;
}
if (require.main === module) {
  const payload = process.argv[2] ? JSON.parse(process.argv[2]) : { sample: true };
  console.log(generarFolio(payload));
}
module.exports = { generarFolio };
