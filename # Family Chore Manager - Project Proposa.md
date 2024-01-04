# Family Chore Manager - Project Proposal

### Intro:

Family Chore Manager is a simple tool to allow parents to track the progress of chores assigned to their children. Basic functionality will include ability to register an account, manage family profiles, and assign, track and manage chores. Included with each week's schedule will also be an indication of the allowance owed by week-end.

### Sections:

1. [Dabase Design](#database-design)
2. [Internal API](#internal-api) (no third party API used)
3. [User Flows](#user-flows)
4. [Technical Details](#technical-details)
5. [User Data and AuthN/AuthZ](#user-data-and-authnauthz)

## Database Design

This project will utilize Postgres w/ a relational database. Tables will include
Family, CHILDREN (lookup for user to user matches), CHORES

![Database Design](/Miro%20Design.png)

## Internal API

The following operations are possible:

1. Signup / Login: user credentials hashed encoded w/ bcrypt
   1. /signup (POST)
   2. /login (POST)
2. Family members: App interface is for "parents", build view and manay family associations here
   1. /family/<id> (GET) - show family name and childrens' names
   2. /family/<id> (PUT) - Update the family profile
   3. /family/<id>/child (GET) - list children
   4. /family/<id>/child (POST) - Create a child profile
   5. /family/<id>/child/<id> (PUT) - Update a child profile
   6. /family/<id>/child/<id> (DELETE) - Remove a child
3. Assign/manage chores
   1. /family/<id>/chores (GET) - List all chores
   2. /family/<id>/chores (POST) - Create a new chore
   3. /family/<id>/chores/<id> (PUT) - Update a chore
   4. /family/<id>/chores/<id> (DELETE) - Remove a chore

## User Flows

The following options describe user interaction with this application:

1. (Route: /) Home page describes app and prompts for Register. Login button also visible in anv
2. Regsiter/Login family name, and password
3. Once registered/logged in, session is updated to check authorization and continued session auth.
4. Logged in user to view this week's schedule of chores on the post-login screen.
5. Here a user can either configure a child or view the progress of chores throughout the week.
6. Adding a new child will require building a brief profile with child's name
7. If user has a child or children, each child will show their schedule and chore completion. Below that there will be allowance total for the week.
8. Chores can be managed from within each member's partial view
   1. A chores detail may need editting
   2. A chore may be removed or added
      1. Chore detail will include the title, optional description, pay-rate per time

## Technical Details

- Database - Postgres Relational DB
- Server - Python, Flask, SQLAlchemy
- Client - HTML with Jinja for server side view logic, CSS, Javascript

## User data and AuthN/AuthZ

When parents login, encryption of password is handled by bcrypt and password is stored hashed and encrypted. Authorization is only handled by session token.
