import json
import time
import requests
import io
import base64
from PIL import Image, PngImagePlugin
import base64
from io import BytesIO

server_url = "http://localhost:3000"
next_url = server_url + "/get-next"
res_url = server_url + "/upload-result"

processed = 0
id = 0
n = 0
while n < 1000:
    payload = {
    "login": "bae4",
    "password": "891a32"
    }
    response = requests.post(url=next_url, json=payload)
    r = response.json()
    print(r['result'])

    if r['result'] == 'ok':
        id = r['id']
        filename = r['name']
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
        # sd working ...
        time.sleep(1)  # emulate sd
        print("Processing finished")
        sd_code = 0
        if sd_code == 0:
            filename = "dataFile-1682346022653.jpg"
            dfile = open("local_results/" + filename, "rb")
            test_res = requests.post(url=res_url, files = {"dataFile": dfile}, data = {"id": id})
            if test_res.ok:
                print("Successully completed")
                #r2 = test_res.json()
                #print(r2)
            else:
                print("Result upload failed")   
        else:
            print("Error processing image in Stable Diffusion")
    else:
        print("No new files in the queue")
    n += 1
    print("[", n, "] Waiting for the next file...")
    time.sleep(5)  # delay before next image
