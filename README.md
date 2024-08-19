# ECC-MVP
ECC Project

## Steps To Run Locally (After Cloning)

#### Step one  
- Create Virtual Environment with python version 10:
- `$ python3.10 -m venv env`

#### Step two
- Activate Environment
-`$ source env/bin/activate`

#### Step Three
- install packages in requirements.txt
- `$ pip install -r requirements.txt`

#### Get Environment Variables
- As defined in the .env.sample file

#### DB Migrations (With Alembic) 
- `$ alembic revision --autogenerate -m "Initial Mirgration"`
- `$ alembic upgrade head`

NOTE: We're not "init-ing" the `migrations` folder with alembic because it already exists

#### Start Server
- $ `./run`

# NOTE: DO NOT PUSH TO THE MAIN BRANCH DIRECTLY, ALWAYS CREATE A PR
