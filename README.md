# progress-timer
A minimalist timer that also tracks the progress of your project. Start, work, track, repeat. 🔁

## Basic Usage
### Set up the project
This will start a dialog to initialize the project. Input the project name, progress trackers (as many as you want!) and their total amounts. Input an empty progress tracker to finish initialization.
```
python main.py switch
```
### Start
This will start the timer and start a new work session. Now start working!
```
python main.py start
```
### Stop
This will stop the timer and end the work session. Call it a day! Input the completed amount of each progress tracker. Enjoy the progress and remaining hours update.
```
python main.py stop
```

## Advance Usage
### Pause
This will pause the timer and pause the work session. Come back in a while to resume working, or to just stop the session. It's alright.
```
python main.py pause
```
### Unpause
This will unpause the timer and unpause the work session. Welcome back to work.
```
python main.py unpause
```
### Summary
This will just show the latest status of the project. Enjoy the progress and remaining hours forecast.
```
python main.py stats
```

## Contribution
### Environment setup
```
uv sync
```
### Format before pushing
```
uv run ruff format
uv run ruff check --fix
```
