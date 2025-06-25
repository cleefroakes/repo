const express = require('express');
const mongoose = require('mongoose');
require('dotenv').config();

const Student = require('./models/student');
const Course = require('./models/course');
const Lecturer = require('./models/lecturer');

const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());

// MongoDB connection
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true
}).then(() => console.log('MongoDB connected'))
  .catch(err => console.error(err));

// Routes
app.get('/students', async (req, res) => res.json(await Student.find()));
app.post('/students', async (req, res) => {
  const student = new Student(req.body);
  await student.save();
  res.status(201).json(student);
});

app.get('/courses', async (req, res) => res.json(await Course.find()));
app.post('/courses', async (req, res) => {
  const course = new Course(req.body);
  await course.save();
  res.status(201).json(course);
});

app.get('/lecturers', async (req, res) => res.json(await Lecturer.find()));
app.post('/lecturers', async (req, res) => {
  const lecturer = new Lecturer(req.body);
  await lecturer.save();
  res.status(201).json(lecturer);
});

// Start server
app.listen(port, () => console.log(`API running on http://localhost:${port}`));
