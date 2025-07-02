import json
import os
import requests
import time
from datetime import datetime, timedelta
from decimal import Decimal

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from termcolor import colored
os.system('color')

cls = lambda: os.system('cls' if os.name=='nt' else 'clear')

TEXT_FILE = "C:/Users/USER/Documents/Streams Perxitaa.txt"

def main():
    print("** ADD VOD TO .TXT QUEUE **")

    vod_id = int(input("Ingrese el ID del VOD >> "))
    vod_info = get_vod_info(vod_id)["data"]["video"]

    video_utc_dt = datetime.strptime(vod_info["createdAt"], '%Y-%m-%dT%H:%M:%SZ')
    video_timestamp = int((video_utc_dt - datetime(1970, 1, 1)).total_seconds())
    video_full_length = timedelta(seconds=vod_info["lengthSeconds"])

    # print(vod_info)
    print(colored("\tTitle: " + vod_info["title"], "yellow"))
    print(colored("\tStreamer: " + vod_info["owner"]["displayName"], "yellow"))
    print(colored("\tTimestamp: " + str(video_timestamp), "yellow"))
    print(colored("\tFull length: " + str(video_full_length), "yellow"))
    print("")

    code = input("Ingrese el código del programa >> ")
    ep_no = Decimal(input("Ingrese el # episodio (use punto como decimal) >> "))
    final_title = input('Nombre del episodio >> ') or "Sin título"
    print(colored("\tEpisode title: " + final_title, "yellow"))
    print("")

    status = "[--PENDNG--]"
    prefix = "["+ code +"]" + "[#" + ("%04.1f" % (ep_no)) + "]" + "[" + str(video_timestamp) + "]"
    # print("Generated prefix: " +prefix)

    must_cut = input('¿Se debe cortar este directo? [y/n] >> ').lower().strip() == 'y'
    cut_start = None
    cut_end = None
    cut_str = None
    video_final_length = None
    if (must_cut):
        cut_start = input('Inicio del corte (Siga el formato HHhMMmSSs, ej: 01h02m23s) >> ') or "0h00m00s"
        input_start = datetime.strptime(cut_start, "%Hh%Mm%Ss")

        cut_end = input('Fin del corte (Siga el formato HHhMMmSSs, ej: 01h02m23s) >> ') or '{:02}h{:02}m{:02}s'.format(int(video_full_length.total_seconds()) // 3600, int(video_full_length.total_seconds()) % 3600 // 60, int(video_full_length.total_seconds()) % 60)
        input_end = datetime.strptime(cut_end, "%Hh%Mm%Ss")

        delta = input_end - input_start
        video_final_length = timedelta(seconds=delta.total_seconds())
        print(colored("\tFinal length: " + str(video_final_length), "yellow"))
        print("")
        cut_str = "(" + cut_start + "-" + cut_end + ")"
    else:
        video_final_length = video_full_length

    print("")
    index = select_image(vod_info["thumbnailURLs"])
    Image.open(BytesIO(requests.get(vod_info["thumbnailURLs"][index]).content)).save(os.path.join(os.path.dirname(__file__), '../SCREENSHOTS/'+prefix+'_'+str(vod_id)+'.png'))
    print(colored("\tThumnbnail #" + str(index) + " saved successfully", "green"))
    print("")

    final_line = status + " " + prefix + "[" + str(video_final_length) + "] " + final_title + " - " + str(vod_id) + (cut_str if must_cut else "")

    print("```")
    print("```")
    print(final_line)
    print("```")
    print("```")
    print("")

    print("\tTrying to add it inside 'Streams Perxitaa.txt'...")
    add_line_to_queue(final_line)

    menu()

def get_vod_info(videoId):
    video_info_json = {
        "query":"query{video(id:\"" + str(videoId) + "\"){title,thumbnailURLs(height:1080,width:1920),createdAt,lengthSeconds,owner{id,displayName}}}",
        "variables":{}
    }
    video_info_req = requests.post("https://gql.twitch.tv/gql", json = video_info_json, headers = {"Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko"})
    return json.loads(video_info_req.text)

def show_available_thumbnails(thumbnails):
    images = []
    for thumbnail in thumbnails:
        res = requests.get(thumbnail)
        ima = Image.open(BytesIO(res.content))
        # ima.show()
        images.append(ima)
    
    full_width = 0
    max_height = 0

    for image in images:
        full_width += image.width
        max_height = max(max_height, image.height)

    # dst = Image.new('RGB', (im1.width + im2.width, min(im1.height, im2.height)))
    dst = Image.new('RGB', (full_width, max_height))
    last_image_width = 0
    i=0
    # print("Full width", str(full_width))
    for image in images:
        font = ImageFont.truetype('C:\WINDOWS\FONTS\ARIAL.TTF', size=250)
        # ImageDraw.Draw(image).text((0,0), str(i), (255, 255, 255), font=font, stroke_fill='black', stroke_width=2)
        ImageDraw.Draw(image).text(
            (image.width//2,image.height//2),
            str(i),
            (255, 255, 255),
            font=font,
            stroke_fill='black',
            stroke_width=5
        )
        
        # print(last_image_width)
        dst.paste(image, (last_image_width, 0))
        last_image_width += image.width
        i+=1

    dst.show()
    # dst.paste(im1, (0, 0))
    # dst.paste(im2, (im1.width, (im1.height - im2.height) // 2))
    # return dst

def select_image(thumbnails):
    show_available_thumbnails(thumbnails)

    selected_index = -1
    while (selected_index < 0 or selected_index > (len(thumbnails) - 1)):
        selected_index = int(input("Selecciona la imagen [0-" +  str(len(thumbnails) - 1) + "] >> "))
    
    return selected_index

def add_line_to_queue(line_add):
    file = open(TEXT_FILE, "r", encoding="utf-8-sig")
    lastVodIndex = 0
    i = 0

    for line in file:
        line = line.strip()

        if line.startswith("[--"):
            lastVodIndex = i
        i += 1
    file.close()

    lastLineIndex = i
    file = open(TEXT_FILE, "r", encoding="utf-8-sig")
    i = 0
    replaced_content = ""
    for line in file:
        line = line.strip()
        new_line = line
        if (i == lastLineIndex-1):
            replaced_content = replaced_content + "Última vez actualizado: " + time.strftime('%d/%m/%Y %X (%Z)')
        else:
            replaced_content = replaced_content + new_line + "\n"
        
        if (i == lastVodIndex):
            replaced_content = replaced_content + line_add + "\n"
        i += 1
    file.close()

    write_file = open(TEXT_FILE, "w", encoding="utf-8-sig")
    write_file.write(replaced_content)
    write_file.close()

def menu():
    print("")
    print("What to do next?")
    print("0 - Exit")
    print("1 - Add new VOD")
    print("")
    opt = int(input("Select option >> "))

    if (opt == 0):
        print("\tBye")
        exit()
    elif (opt == 1):
        cls()
        print("")
        main()

main()