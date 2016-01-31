// The arbiter's task is to spin up a set of bot accounts
var argv = require('yargs').argv,
    db = require('./db'),
    bot = require('./bot');

var conn = null;

function findAvailBots(count, cb) {
  conn.client(function (client, finish) {
    client.query(
      "SELECT * FROM accounts WHERE " +
      "status='AVAIL' AND active=true LIMIT $1", [count], function (err, result) {
        if (err) throw err;
        finish();
        cb(result.rows);
      });
  });
}

function main() {
  var accounts = [];
  var opts = {
    accounts: 1,
  };

  opts.accounts = argv.accounts || opts.accounts;

  var crypter = new db.Crypter(function () {
    conn = new db.Connection(function () {
      findAvailBots(opts.accounts, function (bots) {
        // TODO: length

        for (var boto in bots) {
          boto = bots[boto];
          console.log(boto.row);
          boto.password = crypter.decrypt(boto.password);
          console.log(boto.password);


          // This bot is not setup with our authcode, lets get it working
          if (!bot.sentry) {
            bot.firstTimeSetup(conn, boto, function (sentry) {
              accounts.push(new bot.Bot(boto.username, boto.password, {
                sentrySHA: sentry,
              }));
            });
          } else {
            accounts.push(new bot.Bot(boto.username, boto.password, {
              sentrySHA: boto.sentry
            }));
          }
        }
      });
    });
  });



  /*
  db.setupDatabase(function () {
    opts.accounts = argv.accounts || opts.accounts;

    findAvailBots(opts.accounts, function (bots) {
      console.log(bots)
      if (bots.length != opts.accounts) {
        console.error("Failed to find enough bot accounts to start");
        return process.exit(1);
      }


      for (bot in bots) {
        if (bot.
        accounts.push(new Bot(bot.username, bot.password));
      }
    });
  }, true);
  */
}

if (require.main === module) {
  main()
}

