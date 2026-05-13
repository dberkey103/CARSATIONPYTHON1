create table users (
  id bigint generated always as identity primary key,
  first text not null,
  last text not null,
  username text unique not null,
  password text not null,
  role text default 'sales',
  active boolean default true,
  created_at timestamp default now()
);

-- Insert default users
insert into users (first, last, username, password, role, active) values
  ('Admin', 'User', 'admin', 'admin123', 'admin', true),
  ('Sales', 'Rep', 'sales', 'sales123', 'sales', true),
  ('Finance', 'Manager', 'finance', 'finance123', 'finance', true);
