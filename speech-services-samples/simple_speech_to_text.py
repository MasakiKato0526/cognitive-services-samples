import azure.cognitiveservices.speech as speechsdk
import time

# サブスクリプションキー、リージョンの指定
speech_key = "<subscription key>"
service_region = "<region>"

# オーディオファイルの指定
wavfilename = "<audio file name>"

# Configurationの作成
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
# en-us以外の言語を使う場合
#language = "ja-jp"
#speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region, speech_recognition_language=language)

audio_config = speechsdk.audio.AudioConfig(filename=wavfilename)

# Recognizerの作成
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

# 短い発話の文字起こし処理
def speech_recognize_short_utterance():
    # Speech Recognizerの呼び出し
    result = speech_recognizer.recognize_once()

    # 結果のチェック
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

# 長い発話の文字起こし処理
def speech_recognize_continuous_from_file():
    # Speech Recognizerの呼び出し
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    done = False

    # 発話終了処理
    def stop_cb(evt):
        print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_continuous_recognition()
        nonlocal done
        done = True

    # イベントに応じた出力
    #speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))
    #speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    #speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    #speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))

    # 停止またはキャンセルイベントを受信した場合の処理
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # 結果の結合処理
    speech_recognizer.recognized.connect(handle_final_result)

    # Speech Recognitionの開始
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)

# 開始時間の取得
starttime = time.time()

# 短い発話の文字起こし処理実行
# speech_recognize_short_utterance()

# 長い発話の文字起こし処理実行
all_results_text = []

def handle_final_result(evt):
    offset = evt.result.offset
    duration = evt.result.duration
    text = evt.result.text
    result = str(offset) + "," + str(duration) + "," + str(text)
    all_results_text.append(result)

speech_recognize_continuous_from_file()

# 処理時間の取得
elapse_time = time.time() - starttime

# 最終結果の出力
# ファイルへの出力
outputfile = wavfilename + ".txt"
with open(outputfile, mode="w") as f:
    f.write("\n".join(map(str, all_results_text)))

print()
print("Printing all results: ")

# 全発話を接続して表示
#print(" ".join(all_results_text))

# 発話ごとにを改行して表示
print("\n".join(map(str, all_results_text)))
print()

# 処理時間を表示
print("Elapse time: {0}".format(elapse_time) + "[sec]")