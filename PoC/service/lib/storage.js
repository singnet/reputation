const nedb = require('nedb');


const storage = {};

storage.write = (document) => new Promise((resolve, reject) => {
  nedb()
})

module.exports = storage;
