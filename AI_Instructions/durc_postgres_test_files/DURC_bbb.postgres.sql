--
-- Table structure for table "vote"
--

SET search_path TO DURC_bbb;

DROP TABLE IF EXISTS "vote";
CREATE TABLE "vote" (
  id SERIAL PRIMARY KEY,
  post_id integer NOT NULL,
  votenum varchar(11) NOT NULL,
  updated_at timestamp NOT NULL,
  created_at timestamp NOT NULL
);