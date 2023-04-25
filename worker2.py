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
        image = Image.open(BytesIO(response.content))
        image.save('local_uploads/' + r['filename'])

        parameters = json.loads(r['parameters'])

        print("Processing file " + filename)
        if "set1" in parameters:
            set1 = 1
        else:
            set1 = 0
        set2 = int(parameters["set2"])
        set3 = int(parameters["set3"])
        set4 = int(parameters["set4"])
        set5 = int(parameters["set5"])
        print("File id:", id)
        print("Filename:", filename)
        print("Params:", set1, set2, set3, set4, set5)
        print("Starting Stable diffusion process...")

        prompt = "photorealistic, masterpiece"

        if set1 == 1:
            prompt += ", A black and white portrait"
        print(set2)
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
        print("Prompt:", prompt)

        with open("local_uploads/" + filename, "rb") as image_file:
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
            image.save('local_results/' + filename, pnginfo=pnginfo)

        print("Processing finished")
        print("Uploadnig file...")

        test_file = open("local_results/" + filename, "rb")
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
