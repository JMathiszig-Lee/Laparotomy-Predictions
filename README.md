# Laparotomy-Predictions
Repo for the deployment of the model created by our work in https://github.com/finncatling/lap-risk

The full paper is available open access at https://www.nature.com/articles/s41746-022-00616-7


# Technical
This repo deploys the final output from the work to Laparotomy-risk.com
Any pushes to master are built and deployed so long as tests pass


Raising any issues you find is highly encouraged and pull requests are welcome

The website deploys both a form version of the calculator and an API based on FastAPI

when developing please use pipenv and run the server with

```
uvicorn app.main:api --reload
```

to ensure consistency when deploying