const mongoose = require('mongoose');

const courseSchema = new mongoose.Schema({
  code: String,
  title: String,
  lecturer: String
});

module.exports = mongoose.model('Course', courseSchema);
