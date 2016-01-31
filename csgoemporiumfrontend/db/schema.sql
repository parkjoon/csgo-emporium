/*
    CSGO Emporium Backend Database Schema
*/

CREATE TYPE steam_item AS (
  item_id integer,
  class_id integer,
  instance_id integer,
  item_meta jsonb
);


/*
  Represents steam items in the database
*/

CREATE TABLE items (
  id SERIAL PRIMARY KEY,
  name text NOT NULL UNIQUE,
  price decimal,
  meta jsonb
);

CREATE INDEX ON items (name);


/*
  Represents a single user in the system
    steamid: the users steamid
    email: the users email (if set)
    active: a boolean value if the user is active
    join_date: the date the user joined
    last_login: the last time the user logged in
    ugroup: the users group (enum)
    settings: the users settings (json)
*/

CREATE TYPE user_group AS ENUM ('normal', 'moderator', 'admin', 'super');

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  steamid character varying(255) NOT NULL UNIQUE,
  email character varying(255) UNIQUE,
  active boolean,
  join_date timestamp with time zone,
  last_login timestamp with time zone,
  ugroup user_group,
  settings jsonb
);

CREATE INDEX ON users (steamid);


/*
  Represents a single steam bot-account
    steamid: the bots steamid
    username: the bots steam username (NOT profile name)
    password: the bots AES-256-CTR encrypted password
    sentry: the bots AES-256-CTR encrypted sentry SHA
    status: the bot status (enum)
    last_activity: the last time something happened on this bot
    active: whether this bot can be used
*/

CREATE TYPE bot_status AS ENUM ('COOLDOWN', 'NOAUTH', 'AVAIL', 'USED');

CREATE TABLE bots (
    id SERIAL PRIMARY KEY,
    steamid character varying(255),
    username character varying(255),
    password character varying(255),
    sentry bytea,
    status bot_status,
    inventory steam_item[],
    last_activity timestamp with time zone,
    active boolean
);

CREATE INDEX ON bots (inventory);


/*
  Represents crawled steam_guard_codes
    email: the email the steam_guard_code was sent too
    username: the username the steam_guard_code is for
    code: the actual code
*/

CREATE TABLE steam_guard_codes (
    id SERIAL PRIMARY KEY,
    email character varying(255),
    username character varying(255),
    code character varying(5)
);


/*
  Represents a game on which matches can be played
    name: the game name to be used in titles/etc
    meta: holds game metadata (links, rules, etc)
    appid: the steam appid
    view_perm: the user group that can view this
    active: whether this is active
    created_by: user created by
    created_at: when this was created
*/

CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    name character varying(255) NOT NULL,
    meta jsonb,
    appid integer,
    view_perm user_group,
    active boolean,
    created_by integer REFERENCES users(id),
    created_at timestamp with time zone
);


/*
  Represents a team
*/

CREATE TABLE teams (
  id SERIAL PRIMARY KEY,
  tag varchar(24) UNIQUE,
  name text,
  logo text,
  meta jsonb,
  created_by integer REFERENCES users(id),
  created_at timestamp with time zone
);


/*
  Represents a match played on a game for which there is a result and bets
    game: the game reference
    teams: a list of NON-FOREIGN references to teams
    players: a list of NON-FOREIGN references to users
    meta: metadata (e.g. media, streams)
    lock_date: when this match will lock bets
    match_date: when this match is actually being played
    public_date: when this match goes public
    view_perm: what user group can view this
    active: whether this is active
    created_by: user created by
    created_at: when this was created
*/

CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    game integer REFERENCES games(id),
    teams integer[],
    meta jsonb,
    results jsonb,
    max_value_item decimal,
    max_value_total decimal,
    lock_date timestamp with time zone,
    match_date timestamp with time zone,
    public_date timestamp with time zone,
    view_perm user_group,
    active boolean,
    created_by integer REFERENCES users(id),
    created_at timestamp with time zone,
    results_by integer REFERENCES users(id),
    results_at timestamp with time zone,
    items_at timestamp with time zone,
    draft_started_at timestamp with time zone,
    draft_finished_at timestamp with time zone
);


/*
  Represents a bet placed on a match
*/

CREATE TYPE bet_state AS ENUM ('offered', 'confirmed', 'won', 'lost');

CREATE TABLE bets (
    id SERIAL PRIMARY KEY,
    better integer REFERENCES users(id),
    match integer REFERENCES matches(id),
    team integer,
    value integer,
    items steam_item[],
    winnings steam_item[],
    state bet_state,
    created_at timestamp with time zone
);

CREATE INDEX ON bets (items);
CREATE INDEX ON bets (winnings);
CREATE INDEX on bets (state);

/*
  Represents steam trades in the database
*/

CREATE TYPE trade_type AS ENUM ('returns', 'winnings');
CREATE TYPE trade_state AS ENUM ('offered', 'declined', 'accepted', 'cancelled');

CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    account integer REFERENCES bots(id),
    trader integer REFERENCES users(id),
    bet integer REFERENCES bets(id),
    bot_out steam_item[],
    bot_in steam_item[],
    state trade_state,
    ttype trade_type,
    created_at timestamp with time zone
);


/*
  Represents the result of a fraud run for a match
*/

CREATE TABLE fraud_result (
    id SERIAL PRIMARY KEY,
    match integer REFERENCES matches(id),
    data jsonb,
    created_at timestamp with time zone
);

