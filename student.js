const mongoose = require('mongoose');

const studentSchema = new mongoose.Schema({
  name: String,
  regNo: String,
  course: String
});

module.exports = mongoose.model('Student', studentSchema);
