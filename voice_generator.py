from boto3 import Session
from contextlib import closing
from botocore.exceptions import BotoCoreError, ClientError
import logging, os

default_profile_name = "content-management"
default_region_name = "us-east-1"
# default_local_file_storage = '/storage'
default_local_file_storage = "/Users/vbudichenko/development/go/src/github.com/boodyvo/videogeneration/storage"


class VoiceGenerator:
    def __init__(self,
                 profile_name=default_profile_name,
                 region_name=default_region_name,
                 local_storage=default_local_file_storage,
                 ):
        session = Session(profile_name=profile_name, region_name=region_name)
        self.polly = session.client('polly')
        self.s3_client = session.client('s3')
        self.local_storage = local_storage
        self.voice_file_storage = '{}/audio/voice'.format(self.local_storage)
        # initialize the voice file storage if not exists
        os.makedirs(self.voice_file_storage, exist_ok=True)

    def generate_text_audio(self, text, speech, output_file_name):
        processing_text = '''<speak><prosody rate="80%">{}</prosody></speak>'''.format(text)

        try:
            response = self.polly.synthesize_speech(
                Text=processing_text,
                OutputFormat="mp3",
                VoiceId=speech['voice'],
                TextType="ssml",
                Engine="neural",
                LanguageCode=speech['language'],
            )
        except (BotoCoreError, ClientError) as error:
            logging.error(error)

            raise error

        if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                output = output_file_name

                try:
                    # Open a file for writing the output as a binary stream
                    with open(output, "wb") as file:
                        file.write(stream.read())
                except IOError as error:
                    logging.error(error)

                    raise error

        return
