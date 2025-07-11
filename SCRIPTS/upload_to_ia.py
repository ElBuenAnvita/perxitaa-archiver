import json
import requests
import re
import os, subprocess
from datetime import datetime, timedelta
import winsound
from internetarchive import get_item

from termcolor import colored
os.system('color')

cls = lambda: os.system('cls' if os.name=='nt' else 'clear')

CLI_PATH = '"C:\\Users\\USER\\Videos\\perxitaa-archiver\\SCRIPTS\\TwitchDownloaderCLI.exe"'
EPOCH_TIME = datetime(1970, 1, 1)
TEXT_FILE = "C:/Users/USER/Videos/perxitaa-archiver/Streams Perxitaa.txt"
# REGEX_VOD_HAS_CUT = r"\[([a-zA-Z]{3})\]\[#([0-9]+\.[0-9]+)\]\[([0-9]+)\]\[([0-9]+:[0-9]+:[0-9]+)\] (.*) - ([0-9]+)\((.*)\)"
REGEX_VOD_CUT = r"\[([a-zA-Z]{3})\]\[#([0-9]+\.[0-9]+)\]\[([0-9]+)\]\[([0-9]+:[0-9]+:[0-9]+)\] (.*) - ([0-9]+)\((.*)-(.*)\)"
REGEX_VOD_NOCUT =  r"\[([a-zA-Z]{3})\]\[#([0-9]+\.[0-9]+)\]\[([0-9]+)\]\[([0-9]+:[0-9]+:[0-9]+)\] (.*) - ([0-9]+)"

def get_vod_info(videoId):
    video_info_json = {
        "query":"query{video(id:\"" + str(videoId) + "\"){title,thumbnailURLs(height:1080,width:1920),createdAt,lengthSeconds,owner{id,displayName}}}",
        "variables":{}
    }
    video_info_req = requests.post("https://gql.twitch.tv/gql", json = video_info_json, headers = {"Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko"})
    return json.loads(video_info_req.text)

def get_vod_qualities(vod_id):
    video_token_json = {
        "operationName":"PlaybackAccessToken_Template",
        "query":"query PlaybackAccessToken_Template($login: String!, $isLive: Boolean!, $vodID: ID!, $isVod: Boolean!, $playerType: String!) {  streamPlaybackAccessToken(channelName: $login, params: {platform: \"web\", playerBackend: \"mediaplayer\", playerType: $playerType}) @include(if: $isLive) {    value    signature    __typename  }  videoPlaybackAccessToken(id: $vodID, params: {platform: \"web\", playerBackend: \"mediaplayer\", playerType: $playerType}) @include(if: $isVod) {    value    signature    __typename  }}",
        "variables": {
            "isLive": False,
            "login":"",
            "isVod": True,
            "vodID":"" + str(vod_id) + "",
            "playerType":"embed"
        }
    }
    video_token_req = requests.post("https://gql.twitch.tv/gql", json = video_token_json, headers = {"Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko"})
    video_token_res = json.loads(video_token_req.text)

    # print(video_token_res)
    # print("____")

    playback_token = video_token_res['data']['videoPlaybackAccessToken']['value']
    playback_signature = video_token_res['data']['videoPlaybackAccessToken']['signature']

    # print("VIDEO TOKEN: " + playback_token + "; SIGNATURE: " + playback_signature) # Good

    # video_playlist_req = requests.get("http://usher.twitch.tv/vod/{0}?nauth={1}&nauthsig={2}&allow_source=true&player=twitchweb".format(str(vod_id), playback_token, playback_signature), headers = {"Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko"})
    video_playlist_req = requests.get("http://usher.ttvnw.net/vod/{0}?nauth={1}&nauthsig={2}&allow_source=true&player=twitchweb".format(str(vod_id), playback_token, playback_signature), headers = {"Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko"})
    video_playlist_res = video_playlist_req.text.split('\n')

    video_qualities = []
    for playlist in video_playlist_res:
        # print(playlist) # Good

        quality_search = re.search('NAME="(.*)"', playlist)
        if (quality_search != None):
            video_qualities.append(quality_search.group(1))

    return video_qualities

def get_chat_size(quality_selected: str):
        if (quality_selected == "720p") or (quality_selected == "720p60"):
            return { "width": 350, "height": 720 }
        else:
            quality_selected = quality_selected[:quality_selected.index("p")]
            return { "width": int((350/720)*int(quality_selected)), "height": int(quality_selected) }

def get_pending_vod():
    """
    Get the first finished VOD found with `[--UPLDIN--]` starting the line.
    Must follow any of the two REGEX of VODs

    :return: Dictionary of the pending VOD found. May or may not contain `cut_start` and `cut_end`
    """

    file = open(TEXT_FILE, "r", encoding="utf-8-sig")

    pending_vod = None
    replaced_content = ""
    i = 0
    for line in file:
        line = line.strip()
        new_line = line
        
        print("checking line ... " + line)

        if line.startswith("[--UPLDIN--]") and pending_vod == None:
            print("Line starting with pending found...")
            if (re.search(REGEX_VOD_CUT, line)): # If this line is a VOD that has to be cut, then...
                result = re.search(REGEX_VOD_CUT, line)
                pending_vod = {
                    "show_code": result.group(1), # [COD]: El código de la SERIE (3 LETRAS)
                    "episode_number": result.group(2), # [#10.0]: El número del episodio
                    "timestamp": result.group(3),
                    "duration": result.group(4),
                    "episode_name": result.group(5),
                    "vod_id": result.group(6),
                    "cut_start": result.group(7),
                    "cut_end": result.group(8)
                }
                # new_line = line.replace("[--PENDNG--]", "[--QUEUED--]")
            elif (re.search(REGEX_VOD_NOCUT, line)):
                result = re.search(REGEX_VOD_NOCUT, line)
                pending_vod = {
                    "show_code": result.group(1), # [COD]: El código de la SERIE (3 LETRAS)
                    "episode_number": result.group(2), # [#10.0]: El número del episodio
                    "timestamp": result.group(3),
                    "duration": result.group(4),
                    "episode_name": result.group(5),
                    "vod_id": result.group(6)
                }
                # new_line = line.replace("[--PENDNG--]", "[--QUEUED--]")
        
        new_line = line
        replaced_content = replaced_content + new_line + "\n"

        i += 1

    file.close()

    # print(pending_vod)

    write_file = open(TEXT_FILE, "w", encoding="utf-8-sig")
    write_file.write(replaced_content)
    write_file.close()

    if (pending_vod == None):
        print(colored("\tERROR:", "red"), "No pending VODs to UPLOAD were found!")
        exit()
    
    return pending_vod

def get_show_name_from_code(codigo):
    """
    Devuelve el nombre asociado al código proporcionado (INF => Infames RP)
    Si no es encontrado, se devuelve None.
    """
    # Cargar el contenido del archivo JSON
    with open('shows.json', 'r') as archivo_json:
        contenido_json = json.load(archivo_json)
    
    # Buscar el nombre correspondiente al código
    shows = contenido_json['shows']
    for show in shows:
        if show['code'] == codigo:
            return show['name']
    
    # Si no se encuentra el código, retornar None
    return None

def main():
    print("** UPLOAD TO IA FINISHED VOD **")
    print("")

    pending_vod = get_pending_vod()
    vod_info = get_vod_info(int(pending_vod["vod_id"]))["data"]["video"]
    print(colored("\tFound", "green"))
    # print(pending_vod)
    print("")

    if (vod_info == None):
        print(colored("\tWARN:", "yellow"), "No VOD info found on the TwitchAPI. Probably got deleted already.")
        print("\tYou'll have to input the title of the VOD manually by yourself. It's the only thing we need.")
        print("")
        print( colored("\t\tHINT:", "green"), "The title must be the same as in the VOD+CHAT name.")
        print("")
        vod_info = {}

        vod_info["title"] = input("Please type here the title of the VOD >> ")

    must_cut = False
    cut_start = None
    cut_end = None
    if ("cut_start" in pending_vod) and ("cut_end" in pending_vod):
        must_cut = True
        datetime_start = datetime.strptime(pending_vod["cut_start"], "%Hh%Mm%Ss")
        cut_start = int(timedelta(hours=datetime_start.hour, minutes=datetime_start.minute, seconds=datetime_start.second).total_seconds())

        datetime_end = datetime.strptime(pending_vod["cut_end"], "%Hh%Mm%Ss")
        cut_end = int(timedelta(hours=datetime_end.hour, minutes=datetime_end.minute, seconds=datetime_end.second).total_seconds())
    
    date = datetime.utcfromtimestamp(int(pending_vod["timestamp"])).strftime('%d-%m-%y')
    vod_download_name = re.sub(r'[\\/*?:"<>|]',"","[{0}][#{1}] ({2}) {3} - {4}".format(pending_vod["show_code"], pending_vod["episode_number"], date, "Perxitaa", vod_info["title"]))
    chat_download_name = re.sub(r'[\\/*?:"<>|]',"","[{0}][#{1}] ({2}) [CHAT] {3} - {4}".format(pending_vod["show_code"], pending_vod["episode_number"], date, "Perxitaa", vod_info["title"]))
    vodchat_download_name = re.sub(r'[\\/*?:"<>|]',"","[{0}][#{1}] ({2}) [VOD+CHAT] {3} - {4}".format(pending_vod["show_code"], pending_vod["episode_number"], date, "Perxitaa", vod_info["title"]))

    print("VOD NAME:", vod_download_name)
    print("CHAT NAME", chat_download_name)
    print("VOD+CHAT NAME:", vodchat_download_name)
    print("")

    vod_chat_path = os.path.join(os.getcwd(), "VOD+CHAT/" + vodchat_download_name + ".mp4")
    if not os.path.exists(vod_chat_path):
        print("")
        print(colored("\tERROR:", "red"), "No VOD info found on VOD+CHAT folder. Check if you write the name correctly or if it was deleted.")
        exit()
    
    vod_id = pending_vod["vod_id"]
    print(colored("\tUploading VOD+CHAT to Internet Archive...", "yellow"))
    
    upload_to_ia(pending_vod=pending_vod, vod_info=vod_info, vod_id=vod_id, vodchat_download_name=vodchat_download_name, cut_end=cut_end, cut_start=cut_start)

    print(colored("\tVOD+CHAT was uploaded to Internet Archive!", "green"))
    print("")

    print(colored("\t** Finished all tasks for this VOD... **", "green"))
    winsound.Beep(2500, 500)

    menu()

def upload_to_ia(pending_vod, vod_info, vod_id, vodchat_download_name, cut_start, cut_end):
    result_name = get_show_name_from_code(pending_vod["show_code"])
    show_name = result_name if result_name is not None else ""

    item_ia = get_item('perxitaa_' + vod_id)
    
    while item_ia.exists:
        print("")
        print(colored("\tNOTICE:", "yellow"), "The item with this identifier/VOD ID already exists in IA.")
        print("\t\tThis may be caused because two (or more) episodes come from a same VOD. If you want to continue, you must change the item id.")
        print("")
        print("\t\tBefore proceeding, please check manually if THIS SAME EPISODE hasn't been uploaded to IA by accessing this link:")
        print("\t\thttps://archive.org/details/"+item_ia.identifier)
        print("")
        print("\t\tDo you want to change the identifier in order to upload this VOD with a different identifier?")
        print("\t\tIf you select no, then you'll exit this script and this VOD won't be uploaded.")
        print("")
        change_id = input('Change identifier? [y/n] >> ').lower().strip() == 'y'
        if change_id:
            new_id = input('Please type the new identifier >> ')
            item_ia = get_item(new_id)
            print("")
        else:
            set_uploaded = input('Should we set this VOD as uploaded? [y/n] >> ').lower().strip() == 'y'
            if set_uploaded:
                change_state(pending_vod["show_code"], pending_vod["episode_number"], "UPLDIN", "UPLDED")
            print("")
            exit()

    """ if item_ia.exists:
        print("")
        print(colored("\tERROR:", "red"), " The item already exists in IA.")
        print("\t\tBefore deleting, please check manually if the item is correctly uploaded in IA by accessing this link:")
        print("\t\thttps://archive.org/details/perxitaa_"+vod_id)
        print("")
        print("\t\tNow changing state of this VOD as Uploaded.")
        change_state(pending_vod["show_code"], pending_vod["episode_number"], "UPLDIN", "UPLDED")
        print("")
        print("\tExiting...")
        exit() """

    md = {
        'title': 'Perxitaa - ' + show_name + ': "' + pending_vod["episode_name"] + '"',
        'mediatype': 'movies',
        'collection': 'opensource_movies',
        'date': datetime.fromtimestamp(int(pending_vod["timestamp"])).strftime("%Y-%m-%d"),
        'description': 'Pexitaa Twitch VOD with ID ' + vod_id + "<br /><br />Original Stream title: " + vod_info["title"] + "<br />Simplified title: " + pending_vod["episode_name"] + "<br />Stream timestamp UTC: " + datetime.fromtimestamp(int(pending_vod["timestamp"])).isoformat() + "<br />VOD cut start: " + str(cut_start) + "<br />VOD cut end: " + str(cut_end),
        'subject': ['twitch', 'perxitaa', 'stream', 'roleplay', 'gta rp', 'grand theft auto roleplay'],
        'creator': 'Perxitaa',
        'language': 'Spanish'
    }
    request_ia = item_ia.upload('VOD+CHAT/' + vodchat_download_name + ".mp4", metadata=md, verbose=True)
    print("")
    print(request_ia)

    change_state(pending_vod["show_code"], pending_vod["episode_number"], "UPLDIN", "UPLDED")

def change_state(show_code, episode_number, current_state, new_state):
    """
    Changes line with state found with vod_id requested
    """
    file = open(TEXT_FILE, "r", encoding="utf-8-sig")

    vod_found = False
    replaced_content = ""
    i = 0
    for line in file:
        line = line.strip()
        new_line = line

        if line.startswith("[--") and vod_found == False:
            # print("Line starting with pending found...")

            if (re.search(REGEX_VOD_NOCUT, line)):
                result = re.search(REGEX_VOD_NOCUT, line)
                if ((show_code == result.group(1)) and (episode_number == result.group(2))):
                    new_line = line.replace("[--"+ current_state +"--]", "[--" + new_state + "--]")

        replaced_content = replaced_content + new_line + "\n"

        i += 1

    file.close()

    write_file = open(TEXT_FILE, "w", encoding="utf-8-sig")
    write_file.write(replaced_content)
    write_file.close()

def menu():
    print("")
    print("What to do next?")
    print("0 - Exit")
    print("1 - Continue with next pending VOD in list")
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