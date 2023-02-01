import functions_framework
import os
import requests
import jwt
from datetime import datetime as date
import openai
import re


# OpenAI constants
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "text-davinci-003"

# Ghost constants
GHOST_CONTENT_API_KEY = os.getenv("GHOST_CONTENT_API_KEY")
GHOST_ADMIN_API_KEY = os.getenv("GHOST_ADMIN_API_KEY")
GHOST_API_URL = os.getenv("GHOST_API_URL")
GHOST_API_PORT = os.getenv("GHOST_API_PORT")


def generate_title():
    prompt = "Come up with a new topic for an online magazine about sustainable living"

    response = openai.Completion.create(
        model=OPENAI_MODEL,
        prompt=prompt,
        temperature=0.75,  # lower - more accurate, higher - more creative
        max_tokens=2048,
    )
    return response.choices[0].text


def generate_post(topic):
    prompt = "Write a long comprehensive article for an online magazine about sustainable living on a topic: {}" \
        .format(topic)

    response = openai.Completion.create(
        model=OPENAI_MODEL,
        prompt=prompt,
        temperature=0.75,  # lower - more accurate, higher - more ideas
        max_tokens=2048,
    )

    response_text = response.choices[0].text
    body = "<p>{}</p>".format(str(response_text).replace("\n", "</p><p>"))

    return body


def generate_prompt_for_image(topic):
    prompt = "How would you describe a featured image for an article about {} in less than 10 words".format(topic)

    response = openai.Completion.create(
        model=OPENAI_MODEL,
        prompt=prompt,
        temperature=0.25,  # lower - more accurate, higher - more ideas
        max_tokens=100,
    )

    response_text = response.choices[0].text
    m = re.search('^.+:(.+?)', response_text)
    if m:
        result = m.group(1)
    else:
        result = response_text

    return "{}, digital art".format(result.replace("\n", ", "))


def generate_image(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024",
        response_format="url"  # "b64_json",
    )
    return response['data'][0]['url']  # ['b64_json']


def create_ghost_auth_token():
    # Split the key into ID and SECRET
    ghost_admin_id, ghost_admin_secret = GHOST_ADMIN_API_KEY.split(':')

    # Prepare header and payload
    iat = int(date.now().timestamp())
    header = {'alg': 'HS256', 'typ': 'JWT', 'kid': ghost_admin_id}
    payload = {
        'iat': iat,
        'exp': iat + 5 * 60,
        'aud': '/admin/'
    }

    # Create the token (including decoding secret)
    return jwt.encode(payload, bytes.fromhex(ghost_admin_secret), algorithm='HS256', headers=header)


def upload_image(token, image_b64_json):
    # Make an authenticated request to upload the image
    url = '{}:{}/ghost/api/admin/images/upload/'.format(GHOST_API_URL, str(GHOST_API_PORT))
    headers = {'Authorization': 'Ghost {}'.format(token), 'Content-Type': 'multipart/form-data;'}
    r = requests.post(url, files=dict(file=image_b64_json), headers=headers)
    return r.json()


def submit_post():
    token = create_ghost_auth_token()

    title = generate_title()
    body = generate_post(title)
    image_prompt = generate_prompt_for_image(title)
    image_url = generate_image(image_prompt)

    # Make an authenticated request to create a post
    url = '{}:{}/ghost/api/admin/posts/?source=html'.format(GHOST_API_URL, str(GHOST_API_PORT))
    headers = {'Authorization': 'Ghost {}'.format(token)}
    body = {'posts': [{'title': title,
                       'html': body,
                       'status': 'published',
                       'feature_image': image_url,
                       'feature_image_caption': image_prompt,
                       'feature_image_alt': image_prompt,
                       }]}
    r = requests.post(url, json=body, headers=headers)

    return r.text


@functions_framework.http
def main(request):
    return submit_post()
