const express = require('express');
const multer = require('multer');
const cors = require('cors');
const { exec } = require('child_process');
const app = express();
const port = 5000;

// Setup CORS
app.use(cors());

// // Setup middleware
// app.use(cors()); // Enable CORS for all routes
app.use(express.json()); // Parse JSON bodies

// // Configure Multer (Adjust storage as needed)
// const storage = multer.diskStorage({
//   destination: function (req, file, cb) {
//     cb(null, 'uploads/'); // Set upload directory
//   },
//   filename: function (req, file, cb) {
//     cb(null, file.fieldname + '-' + Date.now() + '-' + file.originalname);
//   },
// });
const storage = multer.diskStorage({
  destination: function(req, file, cb) {
    cb(null, 'uploads/');  // Destination folder
  },
  filename: function(req, file, cb) {
    // Construct filename with original name and extension
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + file.originalname);
  }
});

// Configure Multer with custom storage
const upload = multer({ storage: storage });


app.post('/upload', upload.any(), (req, res) => {
  console.log('Files received:', req.files);  // Correct: req.files is an array

  if (req.files.length === 0) {
      return res.status(400).send('No files uploaded.');
  }

  const firstFilePath = req.files[0].path;
  console.log('First file path:', firstFilePath);

  const country = req.body.country;
  if (!country) {
      return res.status(400).send('Country not specified.');
  }

  const command = `python model_api.py "${firstFilePath}" "${country}"`;

  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Execution error: ${error}`);
      return res.status(500).send(`Execution error: ${error}`);
    }
  
    if (stderr) {
      console.error(`Python stderr: ${stderr}`);
    }
  
    // Assuming the output file is named 'text.txt' and located in the same directory
        try {

          const startIndex = stdout.indexOf('{');
          if (startIndex === -1) {
              console.error('No JSON found in the file.');
              return res.status(500).send('No JSON found in the output file.');
          }
  
          const jsonString = stdout.substring(startIndex);

          const parsedData = JSON.parse(jsonString);

          const reformattedData = Object.keys(parsedData).reduce((acc, key) => {
              const aspectData = parsedData[key];
              acc[key] = {
                  summary: aspectData.summary.text,
                  strategies: aspectData.strategies.replace(/\\n/g, "\n")
              };
              return acc;
          }, {});

            console.log('Reformatted Data:', reformattedData);
            res.json(reformattedData); // Send the reformatted data as response
        } catch (parseError) {
            console.error('Error parsing JSON:', parseError);
            res.status(500).send('Error parsing JSON from output file.');
        }
    });
});


app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});

