import re

def getSpeechBlocks(whispered, silence_time=2):
    text_blocks, (st, et, txt) = [], (0,0,"")
    for i, seg in enumerate(whispered['segments']):
        if seg['start'] - et > silence_time:
            if txt: text_blocks.append([[st, et], txt])
            (st, et, txt) = (seg['start'], seg['end'], seg['text'])
        else: 
            et, txt = seg['end'], txt + seg['text']

    if txt: text_blocks.append([[st, et], txt]) # For last text block

    return text_blocks

def cleanWord(word):
    return re.sub(r'[^\w\s\-_"\'\']', '', word)

def interpolateTimeFromDict(word_position, d):
    for key, value in d.items():
        if key[0] <= word_position <= key[1]:
            return value
    return None

def getTimestampMapping(whisper_analysis):
    index = 0
    locationToTimestamp = {}
    for segment in whisper_analysis['segments']:
        for word in segment['words']:
            newIndex = index + len(word['text'])+1
            locationToTimestamp[(index, newIndex)] = word['end']
            index = newIndex
    return locationToTimestamp


def splitWordsBySize(words, maxCaptionSize):
    halfCaptionSize = maxCaptionSize / 2
    captions = []
    while words:
        caption = words[0]
        words = words[1:]
        while words and len(caption + ' ' + words[0]) <= maxCaptionSize:
            caption += ' ' + words[0]
            words = words[1:]
            if len(caption) >= halfCaptionSize and words:
                break
        captions.append(caption)
    return captions

def getCaptionsWithTime(whisper_analysis, considerPunctuation=True):
    wordLocationToTime = getTimestampMapping(whisper_analysis)
    CaptionsPairs = []
    text = whisper_analysis['text']
    
    if considerPunctuation:
        sentences = re.split(r'(?<=[.!?]) +', text)
        words = [word for sentence in sentences for word in sentence.split()]
    else:
        words = text.split()
        words = [cleanWord(word) for word in words]
    
    start_time = None  # Inicialize o tempo de início como None
    for word in words:
        end_time = interpolateTimeFromDict(len(word), wordLocationToTime)
        if end_time and word:
            # Crie uma legenda para cada palavra
            if start_time is not None:
                CaptionsPairs.append(((start_time, end_time), word))
            start_time = end_time

    return CaptionsPairs
