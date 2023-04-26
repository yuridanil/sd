var express = require('express');
var path = require('path');
var cors = require('cors');
var bodyParser = require('body-parser');
var multer = require('multer')
var db = require('./database');
var app = express();
var port = 3001;

// enable CORS
app.use(cors());
// parse application/json
app.use(bodyParser.json());
// parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: true }));
// serving static files
app.use('/uploads', express.static('uploads'));
app.use('/results', express.static('results'));

// request handlers
app.get('/', (req, res) => {
   res.send('Node js file upload rest apis');
});

// handle storage using multer
var storage = multer.diskStorage({
   destination: function (req, file, cb) {
      cb(null, 'uploads');
   },
   filename: function (req, file, cb) {
      cb(null, `${file.fieldname}-${Date.now()}${path.extname(file.originalname)}`);
   }
});

var upload = multer({ storage: storage });

// handle storage using multer
var storage_res = multer.diskStorage({
   destination: function (req, file, cb) {
      cb(null, 'results');
   },
   filename: function (req, file, cb) {
      //console.log(req.headers);
      cb(null, req.headers.filename);
   }
});

var upload_res = multer({ storage: storage_res });

// handle single file upload
app.post('/upload-avatar', upload.single('dataFile'), (req, res, next) => {
   // console.log(req)
   const file = req.file;
   if (!file) {
      return res.status(400).send({ message: 'Please upload a file.' });
   }
   var sql = "INSERT INTO `files`(`name`, `parameters`) VALUES (?, ?)";
   var values = [req.file.filename, JSON.stringify(req.body)];
   var query = db.query(sql, values, function (err, result) {
      if (err) {
         return res.send({ message: err, file });
      } else {
         return res.send("Файл успешно загружен id = " + result.insertId + ".<br>Для просмотра очереди нажмите <a href='/queue'>здесь</a><br>Для загрузки нового файла нажмите <a href='/upload'>здесь</a>");
      }
   });
});

app.get("/upload", (req, res) => {
   res.sendFile('upload.html', { root: __dirname })
});

app.post("/get-queue", (req, res) => {
   var sql;
   if (req.body.filter == '0' || req.body.filter == '1' || req.body.filter == '2') {
      sql = "select * from files where processed = ? order by id desc limit ?";
      var values = [parseInt(req.body.filter), parseInt(req.body.limit)];
   }
   else {
      sql = "select * from files order by id desc limit ?";
      var values = [parseInt(req.body.limit),];
   }

   var query = db.query(sql, values, function (err, result) {
      if (err) {
         return res.send({ message: err });
      } else {
         return res.send(result);
      }
   });
});

app.get("/queue", (req, res) => {
   res.sendFile('queue.html', { root: __dirname })
});

app.post("/get-next", (req, res) => {
   var sql = "CALL get_next(?, ?)";
   var values = [req.body.login, req.body.password];
   var query = db.query(sql, values, function (err, results) {
      if (err) {
         return res.send({ message: err });
      } else {
         r = results[0][0]
         if (r.result === 'ok' ) {
            res.header('result', r.result)
            res.header('message', r.message)
            res.header('id', r.id || '')
            res.header('filename', r.name || '')
            res.header('parameters', r.parameters || '')
            res.sendFile(path.join(__dirname, './uploads', r.name))
         }
         else {
            res.header('result', r.result)
            res.header('message', r.message)
            return res.send(r);
         }
      }``
   });
});

// handle upload results
app.post('/upload-result', upload_res.single('dataFile'), (req, res, next) => {
   const file = req.file;
   if (!file) {
      return res.status(400).send({ message: 'Please upload a result file.' });
   }

   var sql = "UPDATE files f SET f.processed = 2 WHERE id = ?";
   var values = [parseInt(req.headers.id),];
   var query = db.query(sql, values, function (err, result) {
      if (err) {
         return res.send({ message: err, file });
      } else {
         return res.send({ "result": "ok" });
      }
   });
});

app.listen(port, () => {
   console.log('Server started on: ' + port);
});
