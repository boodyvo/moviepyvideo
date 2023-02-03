import urllib
import requests
import moviepy.editor as mp
from moviepy.audio.fx.volumex import volumex
import zoom_effect
import voice_generator
import os, tempfile, logging

default_size = (1080, 1920)
full_text_size = (720, 900)
full_text_position = (140, 280)

# default_local_file_storage = "/storage"
default_local_file_storage = "/Users/vbudichenko/development/go/src/github.com/boodyvo/moviepyvideos/storage"

sound_storage = os.path.join(default_local_file_storage, 'audio', 'music', 'Horror Stories', 'Sounds')

preview = False


def generate_story_fragment(
        text,
        voice_clip,
        music_clip,
        video_clip,
        duration,
        sound_clips=None,
        text_size=full_text_size,
        text_position=full_text_position,
):
    print('Generating video cut for text {}'.format(text))

    video_cut = video_clip.subclip(0, duration).resize(default_size)

    print('text clip creation', text)

    text_clip = (
        mp.TextClip(
            txt=text,
            fontsize=60,
            bg_color='black',
            color='white',
            method='caption',
            size=text_size,
            stroke_width=1,
            stroke_color='white'
        )
        .set_opacity(0.7)
        .set_position('center')
        .set_duration(duration)
        .margin(top=20, bottom=20, left=20, right=20, opacity=0)
    )

    result_video_clip = mp.CompositeVideoClip([video_cut, text_clip])

    clips_audio = [voice_clip, music_clip]
    if sound_clips is not None:
        clips_audio += sound_clips

    print('clips_audio', clips_audio)

    result_video_clip.audio = mp.CompositeAudioClip(clips_audio)

    return result_video_clip


class StoryGenerator:
    def __init__(self,
                 voice_audio_generator,
                 local_storage=default_local_file_storage,
                 ):
        self.local_storage = local_storage
        self.voice_audio_generator = voice_audio_generator
        self.generated_video_file_storage = '{}/video/generated'.format(self.local_storage)

        os.makedirs(self.generated_video_file_storage, exist_ok=True)

    def generate_video(
            self,
            project_id,
            title,
            paragraphs,
            background_music,
            speech,
    ):
        fragments = []

        music_clip = mp.AudioFileClip(background_music['path']).fx(volumex, 0.3)
        temp_dir = tempfile.TemporaryDirectory()
        print('temp dir {}'.format(temp_dir.name))

        latest_duration_music = background_music['start'] if 'start' in background_music else 0

        for i in range(len(paragraphs)):
            print('start elements', i)
            text_audios = []
            video_duration = 0
            for j in range(len(paragraphs[i]['text'])):
                print('start text', j)
                text = paragraphs[i]['text'][j]['text']
                voice_file_name = '{}/{}_{}_voice.mp3'.format(temp_dir.name, i, j)
                self.voice_audio_generator.generate_text_audio(text, speech, voice_file_name)
                voice_clip = mp.AudioFileClip(voice_file_name)
                text_audios.append(voice_clip)

                video_duration += voice_clip.duration + 1

            print('going to generate video from image')

            video_clip = zoom_effect.clip_from_image(paragraphs[i]['image'], video_duration, size=default_size)
            latest_duration_video = 0

            print('going to generate video')

            for j in range(len(paragraphs[i]['text'])):
                print('going to generate video part', j)
                duration = text_audios[j].duration + 1
                sound_clips = []

                # if 'sound' in paragraphs[i]['text'][j]:
                #     for sound_name in paragraphs[i]['text'][j]['sound']:
                #         print('sound_name', sound_name)
                #         sound_clip = mp.AudioFileClip(os.path.join(sound_storage, '{}.mp3'.format(sound_name))).fx(
                #             volumex,
                #             0.5)
                #         if sound_clip.duration > text_audios[j].duration:
                #             sound_clip = sound_clip.subclip(0, duration)
                #
                #         sound_clips.append(sound_clip)

                if len(sound_clips) == 0:
                    sound_clips = None

                fragment = generate_story_fragment(
                    text=paragraphs[i]['text'][j]['text'],
                    voice_clip=text_audios[j],
                    music_clip=music_clip.subclip(latest_duration_music, latest_duration_music + duration),
                    video_clip=video_clip.subclip(latest_duration_video, latest_duration_video + duration),
                    duration=duration,
                    sound_clips=sound_clips,
                )
                fragments.append(fragment)

                latest_duration_music += duration
                latest_duration_video += duration

        print('Concatenating fragments')

        final_clip = mp.concatenate_videoclips(fragments, method="compose")

        print('Saving the file')

        self.process_final_video_clip(final_clip, project_id, title)
        final_clip.close()
        temp_dir.cleanup()

    def process_final_video_clip(self, video_clip, project_id, title):
        if preview:
            aud = video_clip.audio.set_fps(44100)
            preview_clip = video_clip.without_audio().set_audio(aud)
            preview_clip.preview()

            return

        os.makedirs("{}/{}".format(self.generated_video_file_storage, project_id), exist_ok=True)
        file_path = "{}/{}/{}.mp4".format(self.generated_video_file_storage, project_id, title)

        # final_video.write_videofile(video_dir + 'myoutfile.mp4', threads = 8, fps=24)

        video_clip.write_videofile(
            file_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            threads = 4,
            fps=24
        )


def generate_story_video_from_config(videos_config):
    download_files_from_config_and_update_config(videos_config)

    text_voice_generator = voice_generator.VoiceGenerator()
    story_generator = StoryGenerator(text_voice_generator)
    try:
        story_generator.generate_video(
            project_id=videos_config['project_id'],
            title=videos_config['title'],
            paragraphs=videos_config['paragraphs'],
            background_music=videos_config['background_sound'],
            speech=videos_config['speech'],
        )
    except Exception as e:
        logging.error('error during generation story video: {}'.format(e))


def download_files_from_config_and_update_config(videos_config):
    for i in range(len(videos_config['paragraphs'])):
        image_url = videos_config['paragraphs'][i]['image']
        image_title = videos_config['paragraphs'][i]['image_title']
        image_file_name = '{}/{}/{}.png'.format(default_local_file_storage, "images", image_title)
        print('image_file_name', image_file_name)
        if not os.path.exists(image_file_name):
            print('downloading image', image_url)
            urllib.request.urlretrieve(image_url, image_file_name)

        videos_config['paragraphs'][i]['image'] = image_file_name

    music_url = videos_config['background_sound']['path']
    parts = music_url.split("/")
    last_part = parts[-1].split("?")[0]
    print('last_part', last_part)
    music_file_name = '{}/{}/{}/{}'.format(default_local_file_storage, "audio", "background", last_part)

    url = music_url
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        if not os.path.exists(image_file_name):
            with open(music_file_name, "wb") as f:
                f.write(response.content)
            print("File downloaded successfully.")

        videos_config['background_sound']['path'] = music_file_name
    else:
        print("Error downloading file. Status code:", response.status_code)


    # print('music_file_name', music_file_name)
    # if not os.path.exists(music_file_name):
    #     print('downloading image', music_url)
    #     urllib.request.urlretrieve(music_url, music_file_name)

if __name__ == "__main__":
    config = {
        "project_id": "8c3de4dd",
        "title": "Test",
        "background_sound": {
            "path": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_3ad65087c4.mp3?filename=thriller-ambient-14563.mp3",
            "start": 40,
        },
        "speech": {
            "language": "en-US",
            "voice": "Matthew"
        },
        "paragraphs": [
            {
                "image_title": "dark and foreboding mansion with cracked walls and overgrown foliage",
                "image": "https://replicate.delivery/pbxt/AHrvFfe3eEd9fSNhicwGnSKgFFyFkW8voegIqAmzox2e93nGE/out-0.png",
                "text": [
                    {
                        "sound": ["thunder"],
                        "text": "The storm was loud and scary, and I couldn't help but feel like I was being watched as I walked up the long driveway to the mansion."
                    },
                    {
                        "text": "The air was heavy with the smell of decay and must, and I couldn't shake the feeling that something terrible was waiting for me inside.",
                    },
                    {
                        "sound": ["door creek"],
                        "text": "As I approached the front door, I hesitated for a moment, wondering if I should turn back.",
                    },
                    {
                        "text": "But my curiosity won out and I pushed the door open, stepping into the darkness beyond.",
                    },
                ]
            },
            {
                "image_title": "creepy hallway with broken chandelier and shadowy figures",
                "image": "https://replicate.delivery/pbxt/WtCfp8htkg2yEK0osaCeRH8vbW3FMgSPVaqRTE9yrimwfepBB/out-0.png",
                "text": [
                    {
                        "text": "As I moved further into the mansion, the air grew colder and the shadows seemed to stretch out and claw at me.",
                    },
                    {
                        "sound": ["concrete footsteps"],
                        "text": "The sound of my own footsteps echoing off the walls did little to comfort me, and I couldn't shake the feeling that I was being followed.",
                    },
                    {
                        "sound": ["whispers"],
                        "text": "I could hear faint whispers in the distance"
                    },
                    {
                        "sound": ["dark sitar"],
                        "text": "and every once in a while, the sound of a dark sitar would drift through the air, sending shivers down my spine.",
                    }
                ]
            },
        ]
    }

    generate_story_video_from_config(config)
