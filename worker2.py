import json
import time
import requests
import io
import base64
from PIL import Image, PngImagePlugin
import base64
from io import BytesIO

# server_url = "http://191.101.241.123:3001"
server_url = "http://localhost:3001"
next_url = server_url + "/get-next"
res_url = server_url + "/upload-result"
sd_url = "http://127.0.0.1:7861"

def makePrompt(initPrompt, params):
    prompt = initPrompt

    if "set1" in params:
        set1 = 1
    else:
        set1 = 0
    set2 = int(params["set2"])
    set3 = int(params["set3"])
    set4 = int(params["set4"])
    set5 = int(params["set5"])

    if set1 == 1:
        prompt += ", a black and white portrait"
    if set2 == 2:
        prompt += ", bald"
    if set2 == 3:
        prompt += ", curly hair"
    if set3 == 2:
        prompt += ", in glasses"
    if set4 == 2:
        prompt += ", black hair"
    if set5 == 2:
        prompt += ", mustache"
    if set5 == 3:
        prompt += ", beard"

    return prompt

processed = 0
id = 0
n = 0
while n < 1000:
    payload = {
        "login": "bae4",
        "password": "891a32"
    }
    response = requests.post(url=next_url, json=payload)
    r = response.headers
    #print(r)

    if r['result'] == 'ok':
        id = r['id']
        filename = r['filename']

        print("Processing file " + filename)
        print("File id:", id)

        image = Image.open(BytesIO(response.content))
        image.save('worker_input/' + r['filename'])

        parameters = json.loads(r['parameters'])
        prompt = makePrompt("photorealistic, masterpiece", parameters)
        print("Prompt:", prompt)

        print("Starting Stable diffusion process...")

        with open("worker_input/" + filename, "rb") as image_file:
            data = base64.b64encode(image_file.read())

        payload = {
            "prompt": prompt,
            "steps": 5,
            "init_images": [data.decode('utf-8')]
        }
        
        response = requests.post(url=f'{sd_url}/sdapi/v1/img2img', json=payload)

        r = response.json()

        for i in r['images']:
            image = Image.open(io.BytesIO(
                base64.b64decode(i.split(",", 1)[0])))

            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(
                url=f'{sd_url}/sdapi/v1/png-info', json=png_payload)

            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", response2.json().get("info"))
            image.save('worker_output/' + filename, pnginfo=pnginfo)

        print("Processing finished")
        print("Uploadnig file...")

        test_file = open("worker_output/" + filename, "rb")
        headers = {
            "id": id,
            "filename": filename,
            "prompt": prompt
        }
        test_response = requests.post(res_url, files = {"dataFile": test_file}, headers=headers)

    elif r['result'] == 'error':
        print("Error: " + r['message'])
        quit()
    else:
        print("No new files in the queue")
    n += 1
    print("[", n, "] Waiting for the next file...")
    quit()
    time.sleep(5)  # delay before next image
