const mongoose = require('mongoose');

const lecturerSchema = new mongoose.Schema({
  name: String,
  department: String
});

module.exports = mongoose.model('Lecturer', lecturerSchema);
