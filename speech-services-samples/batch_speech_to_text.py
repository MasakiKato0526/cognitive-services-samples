from typing import List
import logging
import sys
import requests
import time

# Swaggerによるクライアントライブラリを生成
# 1. https://editor.swagger.io.
# 2. File -> Import URLで、https://<your-region>.cris.ai/docs/v2.0/swaggerを指定
# 3. Generate Client -> Python
# 4. 生成されたクライアントライブラリを展開して、python-clientモジュールをパスに追加するか、pipでインストール    
#
# Swagger-codegen 2.3.1の場合はUknown Issueあり  
# https://github.com/swagger-api/swagger-codegen/issues/7541

sys.path.append("python-client")
import swagger_client as cris_client

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(message)s")

# サブスクリプションキー、リージョン、ロケールの指定
SUBSCRIPTION_KEY = "<subscription key>"
SERVICE_REGION = "<region>"
LOCALE = "<locale>"

# 処理名の指定
NAME = "Batch transcription"
DESCRIPTION = "Batch Transcrition"

# ファイルを保管しているBlob storageのSAS URIの指定
RECORDINGS_BLOB_URI="<SAS URI>"

# バッチ文字起こし処理
def transcribe():
    logging.info("Starting transcription client...")

    # APIキー認証の構成
    configuration = cris_client.Configuration()
    configuration.api_key["Ocp-Apim-Subscription-Key"] = SUBSCRIPTION_KEY
    configuration.host = "https://{}.cris.ai".format(SERVICE_REGION)

    # clientオブジェクトの生成
    client = cris_client.ApiClient(configuration)

    # transcription apiクラスのインスタンス生成
    transcription_api = cris_client.CustomSpeechTranscriptionsApi(api_client=client)

    # ベースモデルを使ったtranscriptionの定義
    transcription_definition = cris_client.TranscriptionDefinition(
        name=NAME, description=DESCRIPTION, locale=LOCALE, recordings_url=RECORDINGS_BLOB_URI
    )

    data, status, headers = transcription_api.create_transcription_with_http_info(transcription_definition)

    # locationの取得
    transcription_location: str = headers["location"]
    
    # transcription idの取得
    created_transcription: str = transcription_location.split("/")[-1]

    logging.info("Created new transcription with id {}".format(created_transcription))

    logging.info("Checking status...")

    completed = False

    while not completed:
        running, not_started = 0, 0

        # transcriptionの実行
        transcriptions: List[cris_client.Transcription] = transcription_api.get_transcriptions()

        for transcription in transcriptions:
            if transcription.status in ("Failed", "Succeeded"):
                if created_transcription != transcription.id:
                    continue

                completed = True

                if transcription.status == "Succeeded":
                    results_uri = transcription.results_urls["channel_0"]
                    results = requests.get(results_uri)
                    logging.info("Transcription succeeded. Results: ")
                    logging.info(results.content.decode("utf-8"))
                else:
                    logging.info("Transaction failed :{}.".format(transcription.status_message))
                
                break
            elif transcription.status == "Running":
                running += 1
            elif transcription.status == "NotStarted":
                not_started += 1
        
        logging.info("Transctions status: "
                "completed (this transcription): {}, {} running, {} not started yet".format(
                    completed, running, not_started))

        time.sleep(5)

    input("Press any key...")

# バッチ文字起こし処理の実行
if __name__ == "__main__":
    transcribe()
