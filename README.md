# Light Strava Client 🏃🚴‍♂️

A lightweight, hackable Python wrapper for the Strava API that simplifies authentication and data access. Perfect for developers who want to build custom Strava applications without the complexity of full-featured clients.

## 🚀 Getting started

The project is published on PyPI and can be installed using pip:

```bash
pip install strava-client
```

or using `uv`:

```bash
uv add strava-client
```

---

## 📝 Strava Application

A Strava application is an entity registered in your account which allows you to interact with the Strava API. You can use it to access your data, upload new activities, and perform other operations. 

### Properties

A Strava application is characterized by the following essential properties:

- `client_id`: the id of the application.
- `client_secret`: a secret code assigned to the application.
- `access_token`: a token that allows the application to access your data.

These information are created and provided as soon as the application is created. However, you still need to authorize the application to access your data. Specifically, you need to interact with the Strava API to request an authorization code for specific [scopes](https://developers.strava.com/docs/authentication/#detailsaboutrequestingaccess), which will then be exchanged for a new access token and a refresh token. 

This process is well described in the [Strava API documentation](https://developers.strava.com/docs/getting-started). What is relevant is that these steps will generate 3 new important pieces of information:

- `access_token`: a new authorized token that allows the application to access your data.
- `refresh_token`: a token that allows the application to refresh the access token.
- `expires_at`: the time at which the access token expires.

## 💻 Usage

The Light Strava Client can help you accelerate the authentication process and provide you with an easy template that you can extend to interact with the Strava API.

### 🔐 Authentication

Once you have created the application, you should insert its information in a file called `.strava.secrets`. You can find an example of the file in the repo. Notice that you can change the default name name of the settings file by changing the related variable in the `constants.py` file.

Then, you can instantiate the client as follows:

```python
from strava_client.client import StravaClient

# Initialize with default scopes (read, activity:read_all)
client = StravaClient()

# Or customize your scopes
client = StravaClient(scopes=['read', 'activity:read_all', 'profile:read_all'])
```

Upon instantiation, the secrets will be automatically loaded from the file. We leverage the [pydantic_settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) package to handle the configuration. You can find the definition of the model and the expected types in the `strava_client/models/settings.py` file.

If the refresh token is provided, the client will assume that the authentication process was already completed and no more steps are needed to interact with the API.

Otherwise, it will guide you through the authentication process, which will be automatically initiated. This process is the same described in the documentation, but you only need to authorize the application and paste the callback url in the terminal. The client will take care of the rest.
When the process is completed, the client will save the new access token and the refresh token in the `.strava.secrets` file, so that you can reuse them in the future.

### 💁 Interacting with the API

Once the client is authenticated, you can start interacting with the API. 

Before making a request, the client checks if the access token is still valid. If not, it will automatically refresh it, using the refresh token, and save the new access token in the settings file.

Currently, only one method is implemented, `get_activities`, which allows you to retrieve the activities of the authenticated user. You can use it as follows:

```python
# Get all activities
activities = client.get_activities()

# Activities are returned as typed StravaActivity objects
for activity in activities:
    print(f"{activity.name}: {activity.distance}m on {activity.start_date}")
```

Activities will be a list of `StravaActivity` objects, which contain the information of the activities. You can find the definition of the model in the `strava_client/models/api.py` file.

If you need other endpoints, let me know and I will be happy to implement them! Or you can do that yourself, following the instructions in the next section.

## Development

We use `UV` as package manager. You can install it following the [documentation](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer). Then, once you have cloned the repo, you can run the following command to create the environment and install the dependencies:

```bash
make dev-sync
```

### 🛠️ Extending the Client
The client is designed to be easily extended. You can add new API endpoints by first creating the appropriate Pydantic model for the response and then adding a new method to the `StravaClient` class. You can leverage the existing authentication and request infrastructure to streamline the process.

---

## Disclaimer

This project is just meant to be a simple and lightweight wrapper around the Strava API. It is not meant to be a full-fledged production-ready client, but rather a starting point that you can extend to fit your needs. If you need more functionalities, you can checkout the awesome library [stravalib](https://github.com/stravalib/stravalib).