# Good Blast API Case Study

## Table of Contents
- [Instructions](#instructions)
- [Implementation Details](#implementation-details)
- [API Design](#api-design)
    - [API Endpoints](#api-endpoints)
- [Technologies](#technologies)
- [Testing](#testing)
  - [Last Test Execution Coverage Report](#last-test-execution-coverage-report)
- [Further Improvements](#further-improvements)


## Instructions
- Service is deployed to `Google Cloud App Engine` and can be accessed at: `https://good-blast-413306.uc.r.appspot.com/`
- Source code has a `Dockerfile` and `docker-compose.yml` to run the service in a container. API can be run with `docker-compose up` command.
- Service can be run locally with `python manage.py runserver` command after setting `SECRET_KEY`, `DEBUG`, `DATABASE_URL` environment variables. 
  - Local Environment Requirements:
    - `Python 3.11`
    - `PostgreSQL 14`


## Implementation Details
- Users can register and login to the system. 
- After login, users can access endpoints via JWT tokens. 
- Users can enter daily tournaments that are created daily.
- Users will be assigned to a group with level bucket strategy.
- Users with different current levels will be assigned to different groups.
- This can be useful to prevent high level users to compete with low level users.
- Tournaments created with a cron job a day before it starts. 
- Users can claim rewards if they are elligible for it. 
- If a user progress levels in a tournament with update progress endpoint it will increase their tournament score.
- If user enters a tournament, they will be added to the first group that has space.
- Users can see their progress in the tournament and their ranking in the leaderboard.


## API Design
API is publicly available at: `https://good-blast-413306.uc.r.appspot.com/`

### API Endpoints
- **/api/users/**
  - **POST**: Create a new user with username, country code and password.
- **/api/users/token**
  - **POST**: Get jwt access and refresh tokens for a user with username and password.
- **/api/users/token/refresh**
  - **POST**: Get new access token with refresh token.
- **/api/users/{username}**
  - **GET**: Get user details.
  - **DELETE**: Delete user with username.
- **/api/users/{username}/progress**
  - **POST**: User completes current level.
  
- **/api/tournament/enter**
  - **POST**: User enters the tournament.
- **/api/tournament/claim-reward?tournament={tournament_id}**
  - **POST**: User claims reward for a tournament if user is in a reward bucket. Query parameter is optional. If it is not provided, user will claim non-collected rewards of all passed tournaments.
- **/api/tournament/{tournament_id}**
  - **GET**: Get users tournament progress details.

- **/api/leaderboard/global**
    - **GET**: Get global leaderboard maximum of 1000 users.
- **/api/leaderboard/country**
    - **GET**: Get country leaderboard maximum of 1000 users.
- **/api/leaderboard/group**
    - **GET**: Get group leaderboard of the user.
- **/api/leaderboard/rank**
    - **GET**: Get users ranking in the tournament group.


## Technologies
- `Django`
- `Django Rest Framework`
- `JWT` for authentication.
- `Cron Job` for tournament creation.
- `Google Cloud SQL` PostgreSQL Instance.
- `Google Cloud App Engine` for deployment.
- `Docker`


## Testing
Tests can be run in the container or local environment after installation with:
```shell
(venv)$ coverage run --source=leaderboard,tournament,user manage.py test 
```
Coverage report can be generated with:
```shell
(venv)$ coverage report
```

### Last Test Execution Coverage Report
```sh
Name                                                                  Stmts   Miss  Cover
-----------------------------------------------------------------------------------------
leaderboard/__init__.py                                                   0      0   100%
leaderboard/apps.py                                                       4      4     0%
leaderboard/migrations/__init__.py                                        0      0   100%
leaderboard/serializers.py                                                9      0   100%
leaderboard/tests/__init__.py                                             0      0   100%
leaderboard/tests/test_serializers.py                                    12      0   100%
leaderboard/tests/test_views.py                                          85      0   100%
leaderboard/urls.py                                                       3      0   100%
leaderboard/views.py                                                     45      0   100%
tournament/__init__.py                                                    0      0   100%
tournament/admin.py                                                       1      0   100%
tournament/apps.py                                                        7      0   100%
tournament/migrations/0001_initial.py                                     7      0   100%
tournament/migrations/0002_remove_usertournamentgroup_entered_at.py       4      0   100%
tournament/migrations/0003_tournamentgroup_level_bucket.py                4      0   100%
tournament/migrations/__init__.py                                         0      0   100%
tournament/models.py                                                     74      1    99%
tournament/scheduler.py                                                  21      9    57%
tournament/serializer.py                                                  8      0   100%
tournament/tests/__init__.py                                              0      0   100%
tournament/tests/test_models.py                                          72      0   100%
tournament/tests/test_serializers.py                                     14      0   100%
tournament/tests/test_views.py                                          166      0   100%
tournament/urls.py                                                        3      0   100%
tournament/views.py                                                      56      2    96%
user/__init__.py                                                          0      0   100%
user/admin.py                                                             3      0   100%
user/apps.py                                                              4      0   100%
user/migrations/0001_initial.py                                           6      0   100%
user/migrations/__init__.py                                               0      0   100%
user/models.py                                                           44      5    89%
user/permissions.py                                                       6      0   100%
user/serializers.py                                                      15      0   100%
user/tests/__init__.py                                                    0      0   100%
user/tests/test_models.py                                                39      0   100%
user/tests/test_serializers.py                                           26      0   100%
user/tests/test_views.py                                                120      0   100%
user/urls.py                                                              4      0   100%
user/views.py                                                            29      0   100%
-----------------------------------------------------------------------------------------
TOTAL                                                                   891     21    98%
```


## Further Improvements
- Tournament level buckets can be dynamic sized.
- Number of users that are attending to a tournament can be estimated and groups can be distributed more equivalently.
- Leaderboard can be paginated.