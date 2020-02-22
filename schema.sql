drop table if exists notifications;

create table notifications (
    "id" integer primary key,
    "timestamp" datetime default current_timestamp not null,
    "title" text not null,
    "body" text not null
);

create index "notifications_title_idx" on notifications (title asc);
create index "notifications_body_idx" on notifications (body asc);



drop table if exists workspace;

create table workspace (
    "id" integer primary key,
--     "subscription_token" text not null unique,
    "access_token" text not null unique
);

create index "workspace_access_token" on workspace (access_token asc);


drop table if exists message;

create table message (
    "id" integer primary key,
    "timestamp" datetime default current_timestamp not null,
    "workspace" text not null,
    "channel" text not null,
    "user" text not null,
    "msg" text not null
);

create index "message_timestamp" on message (timestamp asc);
create index "message_workspace" on message (workspace asc);
create index "message_channel" on message (channel asc);
create index "message_user" on message (user asc);
create index "message_msg" on message (msg asc);


drop table if exists auth_user;

create table auth_user (
    "id" integer primary key,
    "authed_user_id" text not null unique,
    "access_token" text not null
);

create index "auth_user_authed_user_id" on auth_user (authed_user_id asc);
create index "auth_user_access_token" on auth_user (access_token asc);


drop table if exists user_info;

create table user_info (
    "id" integer primary key,
    "user_id" text not null unique,
    "display_name" text not null
);

create index "user_info_user_id" on user_info (user_id asc);
create index "user_info_display_name" on user_info (display_name asc);

