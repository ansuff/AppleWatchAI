# Apple Watch Fitness AI
A small project to create a fitness AI for the Apple Watch.

The goal is to see if I can predict which time of the day is best to do a workout based on the user's heart rate, sleep, and activity data. Later on, I will try to predict the type of workout that the user should do based on the same data.

Also, I will try to predict the best day of the week to do a workout based on the same data.

More to come...

## Setup Instructions

To get started with this project, you can use the `init_setup.sh` script to install all necessary dependencies. This script will:

- Check if Homebrew is installed and install it if necessary.
- Install Poetry using Homebrew.
- Install npm using Homebrew.
- Install nodemon globally using npm.

To run the setup script, use the following command in your terminal:

```sh
./init_setup.sh
```

After running the setup script, you need to install the project dependencies using Poetry. Run the following command in your terminal:

```sh
poetry install
```

This will install all the dependencies specified in the pyproject.toml file.

You are now ready to start working on the project! 🚀