import mysql.connector
import json
import time
import requests
import io
import base64
from PIL import Image, PngImagePlugin
import base64
from io import BytesIO

cnx = mysql.connector.connect(user='test', password='test123', host='localhost', database='mynode')

processed = 0
id = 0
n = 0
while n < 1000:
    cnx.start_transaction()
    cursor = cnx.cursor(buffered=True)
    query = ("SELECT id, name, parameters FROM files WHERE processed = %s LIMIT 1")
    cursor.execute(query, (processed,))

    if cursor.rowcount > 0:
        for (id, filename, parameters) in cursor:
            j = json.loads(parameters)
            if "set1" in j:
                set1 = 1
            else:
                set1 = 0
            set2 = int(j["set2"])
            set3 = int(j["set3"])
            set4 = int(j["set4"])
            set5 = int(j["set5"])
            print("File id:", id)
            print("Filename:", filename)
            print("Params:", set1, set2, set3, set4, set5)

        query = ("UPDATE files SET processed = 1 WHERE id = %s")
        cursor.execute(query, (id,))
        cnx.commit()

        print("Starting Stable diffusion process...")

        url = "http://127.0.0.1:7860"
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
        
        with open("uploads/" + filename, "rb") as image_file:
            data = base64.b64encode(image_file.read())

        payload = {
            "prompt": prompt,
            "steps": 10,
#            "denoising_strength": 0.3,
            "init_images": [data.decode('utf-8')]
        }

        response = requests.post(url=f'{url}/sdapi/v1/img2img', json=payload)

        r = response.json()

        for i in r['images']:
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))

            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(
                url=f'{url}/sdapi/v1/png-info', json=png_payload)

            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", response2.json().get("info"))
            image.save('results/'+filename, pnginfo=pnginfo)

        print("Processing finished")
        sd_code = 0
        if sd_code == 0:
            query = ("UPDATE files SET processed = 2 WHERE id = %s")
            cursor.execute(query, (id,))
            cnx.commit()
            print("Successully completed")
        else:
            cnx.rollback()
            print("Error")
    else:
        cnx.commit()
        print("No new files in the queue")
    n += 1
    cursor.close()
    print("[", n, "] Waiting for the next file...")
    time.sleep(5)  # delay before next image

cnx.close()
