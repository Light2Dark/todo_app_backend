
# To-do App

The backend of a fullstack to-do app dabbling in microservices architecture.

## Features

- Database for todo's
- Auth for users


## Development

The project uses a dockerized backend. This is the repo for that backend. 
The docker image is run by Google's Cloud Run, a fully managed architecture to deploy containers.

The project also uses Firebase Auth but what needs to be improved is allowing third-party sign ins.
## Deployment

The backend requires Python's FastAPI and Firebase SDK. To edit the backend, yo would need to download this repo and provide environment variables for the Firebase URL's.


