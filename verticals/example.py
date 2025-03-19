import os
from google.cloud import secretmanager

# If running locally, set this to your service account JSON key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.environ["HOME"],"sistemap-msg-94b79caf0427.json")

def access_secret(project_id, secret_id, version_id="latest"):
    # Create the Secret Manager client
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version
    response = client.access_secret_version(request={"name": name})

    # Get the secret payload
    secret_value = response.payload.data.decode("UTF-8")

    return secret_value

# Example usage
if __name__ == "__main__":
    project_id = "sistemap-msg"

    secret_ids = ["wa-verify-token", "wa-phone-id", "wa-access-token"]    
    
    for secret_id in secret_ids:
        secret_value = access_secret(project_id, secret_id)
        print(f"The secret value of {secret_id} is: {secret_value}")
