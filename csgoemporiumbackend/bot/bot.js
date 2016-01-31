var Steam = require('steam'),
    fs = require('fs'),
    redis = require('redis'),
    imap = require('imap');

function updateSentryHash(conn, bot, hash, cb) {
  conn.client(function (client, finish) {
    client.query("UPDATE accounts SET sentry=$1 WHERE id=$2", [hash, bot.id], function (err, result) {
      finish();
      if (err) throw err;
      cb(hash);
    });
  });
}

function firstTimeSetup(conn, bot, cb) {
  // Fake a login
  new Bot(bot.username, bot.password, {
    authCode: "",
    onLogin: function (err) {
      if (!err) {
        console.error("Failed to firstTimeSetup, login worked?");
        return;
      }

      var count = 0;

      function waitForCode() {
        if (count > 12) {
          console.error("Failed to get first time steam-guard code!");
          return;
        }

        conn.client(function (client, finish) {
          // TODO: ordering
          client.query("SELECT * FROM steam_guard_codes WHERE username=$1", [bot.username], function (err, result) {
            finish();
            if (result.rows.length) {
              new Bot(bot.username, bot.password, {
                authCode: result.rows[0].code,
                onSentry: function (data) {
                  updateSentryHash(conn, bot, data, cb);
                  this.steam.logOff();
                },
                onLogin: function (err) {
                  if (err) {
                    console.error("Failed to login with first time steam-guard code!");
                    throw err;
                  }
                }
              });
            } else {
              setTimeout(waitForCode, 5000);
            }
          });
        });
      }

      console.log("Login failed as expected, waiting for code...");
      waitForCode();
    }
  });
}

exports.firstTimeSetup = firstTimeSetup;

Bot = function (user, pass, options) {
  options = options || {};
  this.username = user;
  this.password = pass;
  this.steam = new Steam.SteamClient();
  this.redis = redis.createClient();
  this.running = true;
  this.loggedOn = false;

  this.authCode = options.authCode || null;
  this.sentrySHA = options.sentrySHA || null;

  this.options = options;

  this.login();
}

Bot.prototype.createTradeOffer = function (data) {
  steam.webLogOn((function (newCookie) {
    this.webCookie = newCookie;

    offers.setup({
      sessionID: this.webSessionID,
      webCookie: this.webCookie,
    }, (function (err) {
      if (err) throw err;
      this.waitForOffer();
    }).bind(this));
  }).bind(this));
}

Bot.prototype.waitForOffer = function () {
  this.redis.blpop("trade-offers", 0, (function (err, res) {
    this.waitForOffer();

    var data = JSON.parse(res[1].toString());
    this.createTradeOffer(data);
  }).bind(this));
}

Bot.prototype.setup = function () {
  console.log("Setting up callbacks");
  this.steam.on("debug", console.log);
  this.steam.on("error", this.eventError.bind(this));
  this.steam.on("loggedOn", this.eventLoggedOn.bind(this));
  this.steam.on("sentry", this.eventSentry.bind(this));
  this.steam.on("webSessionID", this.eventWebSessionID.bind(this));

  this.redis.on("error", function (err) {
    if (err) throw err;
  });
}

Bot.prototype.login = function () {
  console.log("Attempting login...");

  // We setup our event handlers
  this.setup();

  var loginDetails = {
    accountName: this.username,
    password: this.password,
  };

  if (this.authCode) {
    loginDetails.authCode = this.authCode;
  }

  if (this.sentrySHA) {
    loginDetails.shaSentryfile = this.sentrySHA;
  }

  // Ask node-steam to login
  this.steam.logOn(loginDetails);

  return true;
}

Bot.prototype.eventLoggedOn = function (data) {
  console.log("Logged on!");

  this.loggedOn = true;
  if (this.options.onLogin) {
    this.options.onLogin(null);
  }
}

Bot.prototype.eventError = function (err) {
  if (!this.loggedOn && this.options.onLogin) {
    this.options.onLogin(err);
  }
  console.log(err);
};

Bot.prototype.eventSentry = function (data) {
  if (this.options.onSentry) {
    this.options.onSentry(data);
  }
}

Bot.prototype.eventWebSessionID = function (data) {
  this.webSessionID = data;
  this.waitForOffer();
}

exports.Bot = Bot;

function main() {
  // Stubbed
  var user = "csgoemporium1",
      pass = "BlueSky489!";

  var bot = new Bot(user, pass);
}

if (require.main === module) {
  main();
}
