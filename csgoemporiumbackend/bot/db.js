var pg = require('pg');
    fernet = require('fernet'),
    read = require('read'),
    util = require('util');

var Connection = function (ready, username, password, options) {
  options = options || {};
  this.username = username || "emporium";
  this.password = password;
  this.host = options.host || "104.171.118.100";
  this.port = options.port || 50432;
  this.readyCallback = ready;

  if (!this.password) {
    read({
        prompt: "DB Password > ",
        silent: true,
      }, (function (err, password) {
        this.password = password;
        this.buildConnString(this.readyCallback);
      }).bind(this));
  }
}

Connection.prototype.buildConnString = function (cb) {
  this.connString = util.format("postgres://%s:%s@%s:%s/emporium",
      this.username, this.password, this.host, this.port);
  if (cb) {
    cb()
  }
}

Connection.prototype.client = function (cb) {
  pg.connect(this.connString, function (err, client, done) {
    if (err) throw err;

    cb(client, done)
  });
}

var Crypter = function (cb, masterPassword) {
  this.callback = cb;
  this.password = masterPassword;

  if (!this.password) {
    read({
      prompt: "Bot Encryption Password > ",
      silent: true,
    }, (function (err, password) {
      this.password = new fernet.Secret(password);
      this.callback();
    }).bind(this));
  } else {
    this.password = new fernet.Secret(this.password);
    this.callback();
  }
}

Crypter.prototype.encrypt = function (data) {
  var token = new fernet.Token({
    secret: this.password,
    time: new Date(),
    iv: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  });

  return token.encode(data);
}

Crypter.prototype.decrypt = function (data) {
  var token = new fernet.Token({
    secret: this.password,
    token: data,
    ttl: 0,
  });

  return token.decode();
}

exports.Connection = Connection;
exports.Crypter = Crypter;

