var mysql = require('mysql');
var conn = mysql.createConnection({
  host: 'localhost', // Replace with your host name
  user: 'test',      // Replace with your database username
  password: 'test123',      // Replace with your database password
  database: 'mynode', //  Replace with your database Name
  port: 3306
}); 
conn.connect(function(err) {
  if (err) throw err;
  console.log('Database is connected successfully !');
});
module.exports = conn;
