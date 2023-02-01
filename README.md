# auto-blogging-with-chatgpt
Experimental project that uses Large Language Model (GPT-3, think ChatGPT) to programmatically create new blog posts (text) and images for it.
It works fully autonomously, creating new posts on a schedule, e.g. new post every Monday.

## Installation instructions
### Bring up GCP Compute instance
This is the server that will host your web site / blog.

- Create a new general purpose instance: https://console.cloud.google.com/compute/instancesAdd
- Make sure to check "Allow HTTPS traffic"

### Install Ghost blogging platform
Ghost is a blogging platform that allows you to programmatically create posts.

- SSH into your newly created instance
- Follow the steps here to install necessary components and the Ghost platform: https://ghost.org/docs/install/ubuntu/
- Once you have the Ghost platform up and running, make sure you can access your website by ip address of your GCP Compute instance
- For additional platform setup use http://<instance-ip>/ghost

#### Create a Ghost custom integration
Ghost custom integration is the way to interact with the Ghost platform programmatically. It allows to access [Admin API](https://ghost.org/docs/admin-api/) and [Content API](https://ghost.org/docs/content-api/) with lots of different functions.

- Create a new Ghost custom integration: http://104.199.126.46/ghost/#/settings/integrations/new/
- Notice the API keys generated for you:
  - Content API key
  - Admin API key
  - API URL

### Setup Cloud function
- Create a new Cloud function: https://console.cloud.google.com/functions/add
  - Environment: 2nd gen
  - Trigger type: HTTPS
- Add environment variables:
  - OPENAI_API_KEY: get it from https://platform.openai.com/account/api-keys
  - GHOST_CONTENT_API_KEY: get it from your Ghost custom integration: http://104.199.126.46/ghost/#/settings/integrations/
  - GHOST_ADMIN_API_KEY: get it from your Ghost custom integration: http://104.199.126.46/ghost/#/settings/integrations/
  - GHOST_API_URL: get it from your Ghost custom integration: http://104.199.126.46/ghost/#/settings/integrations/
  - GHOST_API_PORT: use default port 2368 (unless you changed it during the Ghost installation
- Use Python 3.9 for execution environment

### Setup Cloud scheduler
- Create a new job: https://console.cloud.google.com/cloudscheduler/jobs/new
- Define frequency, e.g. every Monday at 7am: 0 7 * * 1
- Configure execution:
  - Target type: HTTP
  - URL: that's the URL of the Cloud function you created on the previous step
  - HTTP method: POST
- HTTP Headers:
  - Content-Type: application/json
