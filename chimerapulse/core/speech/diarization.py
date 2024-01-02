"""Module that contains 'diarization' logic call to Azure speech service

Reference:
    https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-stt-diarization?tabs=macos&pivots=programming-language-python#diarization-from-file-with-conversation-transcription

Example:
    python -m chimerapulse.core.speech diarization <args>
    chi speech diarization -p
"""
import os
from tkinter import filedialog
import time

import click
from dotenv import load_dotenv

# Import Azure speech SDK
import azure.cognitiveservices.speech as speechsdk

# Load env vars
load_dotenv()

# Declare global variables
conversations = []
verbose = False


"""
Validation fxns
"""
def get_conversation_file_path(ctx, param, value):
    """Retrieves conversation file path

    Args:
        ctx (obj): Context
        param (str): Parameter
        value (Any): Value

    Return:
        (str): File path
    """
    filepath = ''
    print('Collecting conversation...')

    # Open file dialog if path is empty
    if value == 'flag':
        filepath = filedialog.askopenfilename()
    else:
        filepath = os.path.relpath(value, os.getcwd())


    # TODO: Verify file is an audio file here
    # Validate file path if value is provided
    if not os.path.isfile(filepath):
        raise ValueError(f'ERROR: Cannot find file at: {filepath}. Exiting...')

    print(f'Conversation audio file path: {filepath}')
    return filepath

"""
Private fxns
"""
def __authenticate_client():
    """Authenticates speech client

    Return:
        (SpeechConfig): Speech client
    """
    # Get Configuration Settings
    speechkey = os.getenv('SPEECH_SERVICE_KEY')
    speechregion = os.getenv('SPEECH_SERVICE_REGION')

    # Connect to Azure Language Service
    return speechsdk.SpeechConfig(speechkey, speechregion)


def __vprint(text):
    global verbose

    if (verbose):
        print(text)


def conversation_transcriber_recognition_canceled_cb(evt: speechsdk.SessionEventArgs):
    """Callback fxns for recognition canceled
        
    Args:
        evt (speechsdk.SessionEventArgs): Session event args
    """
    print('Canceled event')


def conversation_transcriber_session_stopped_cb(evt: speechsdk.SessionEventArgs):
    """Callback fxns for session stopped
        
    Args:
        evt (speechsdk.SessionEventArgs): Session event args
    """
    print('SessionStopped event')


def conversation_transcriber_transcribed_cb(evt: speechsdk.SpeechRecognitionEventArgs):
    """Callback fxns for transcribed chunk
        
    Args:
        evt (speechsdk.SessionEventArgs): Session event args
    """
    # Access global variables
    global conversations

    __vprint('TRANSCRIBED:')
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        __vprint('\tText={}'.format(evt.result.text))
        __vprint('\tSpeaker ID={}'.format(evt.result.speaker_id))

        conversations.append({
            "text": evt.result.text,
            "id": len(conversations) + 1,
            "role": evt.result.speaker_id[:-2],
            "participantId": evt.result.speaker_id
        })

    elif evt.result.reason == speechsdk.ResultReason.NoMatch:
        print('\tNOMATCH: Speech could not be TRANSCRIBED: {}'.format(evt.result.no_match_details))


def conversation_transcriber_session_started_cb(evt: speechsdk.SessionEventArgs):
    """Callback fxns for session start
        
    Args:
        evt (speechsdk.SessionEventArgs): Session event args
    """
    print('SessionStarted event')


# TODO: add json flag to return JSON object instead of print to terminal
@click.command()
@click.option('-p', '--file-path', required=True, callback=get_conversation_file_path, flag_value='flag', is_flag=False, help='Path to audio file')
@click.option('-v', '--verbose-print', is_flag=True, flag_value=True, default=False, help='Prints response instead of returning as JSON object')
def diarization(file_path, verbose_print):
    """Speech diarization on audio files with mono channel

    Args:
        file_path (str): Path to conversation audio file
    """
    global verbose

    verbose = verbose_print
    speech_diarization(file_path)


# TODO: Return conversation transcription in JSON to be used in conversation summarization
def speech_diarization(filepath):
    global verbose

    speech_config = __authenticate_client()
    # TODO: Possible use of languag identification
    speech_config.speech_recognition_language='en-US'

    audio_config = speechsdk.audio.AudioConfig(filename=filepath)
    conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)

    transcribing_stop = False

    def stop_cb(evt: speechsdk.SessionEventArgs):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal transcribing_stop
        transcribing_stop = True

    # Connect callbacks to the events fired by the conversation transcriber
    conversation_transcriber.transcribed.connect(conversation_transcriber_transcribed_cb)
    conversation_transcriber.session_started.connect(conversation_transcriber_session_started_cb)
    conversation_transcriber.session_stopped.connect(conversation_transcriber_session_stopped_cb)
    conversation_transcriber.canceled.connect(conversation_transcriber_recognition_canceled_cb)
    # stop transcribing on either session stopped or canceled events
    conversation_transcriber.session_stopped.connect(stop_cb)
    conversation_transcriber.canceled.connect(stop_cb)

    conversation_transcriber.start_transcribing_async()

    # Waits for completion.
    while not transcribing_stop:
        time.sleep(.5)

    conversation_transcriber.stop_transcribing_async()

    if not verbose:
        return conversations
