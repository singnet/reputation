

CREATE TABLE channel(
	channel_id	integer not null,
    nonce       integer not null,
    sender		varchar(50) not null,
    recipient	varchar(50) not null,
    amount 		bigint not null,
    open_time   integer,
    close_time  integer,
    PRIMARY KEY(channel_id, nonce)
)