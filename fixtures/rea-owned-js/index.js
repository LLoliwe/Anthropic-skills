const { format } = require('./format.js');
function status() { return format('ok'); }
module.exports = { status };
