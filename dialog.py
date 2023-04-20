import sys
import json
import requests
import argparse
import openai

# 対話制御クラス
class Dialog:
    def __init__(self, user_continuation_instruction:str, system_generation_instruction:str, args) -> None:
        self.args = args
        # jsonファイルでAPIキーの読み込み
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        self.api_key = config["open_ai_api_key"]
        openai.api_key = self.api_key
        # 対話制御のための指示文
        self.user_continuation_instruction = user_continuation_instruction
        self.system_generation_instruction = system_generation_instruction
        # 対話の初期化
        self.dialog_history = []
        
    # ユーザー発話の続きを生成する関数
    def user_continuation(self, content:str):
        return self.api_exec(self.user_continuation_instruction, content)
    
    # ユーザー発話の続きに対する応答の生成関数
    def system_generation(self, content:str):
        return self.api_exec(self.system_generation_instruction, content)

    # API実行関数
    def api_exec(self, instruction:str, content:str):
        prompt = []
        prompt.append({"role": "system", "content": instruction})
        prompt.append({"role": "user", "content":content})
        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt,
        )
        return result.choices[0].message.content
    
    
    # 対話(ユーザーの発話を予測する)を実行する関数
    def run_continual(self):
        while True:
            user_input = input("user: ")
            if user_input == "exit":
                break
            user_output = self.user_continuation(user_input)
            print("user_continuation: ", user_output)
            user_utt = user_input + user_output
            system_output = self.system_generation(user_utt)
            print("system: ", system_output)
    
    # 対話(デフォルト(通常の対話))を実行する関数
    def run(self):
        instruction = "対面で自然で喋っていてとても楽しい対話をしてください。"
        while True:
            user_input = input("user: ")
            if user_input == "exit":
                break
            system_output = self.completion(user_input, instruction)
            if not args.stream:
                print("system: ", system_output)

    def completion(self, new_message_text:str, settings_text:str = ''):
        if len(self.dialog_history) == 0 and len(settings_text) != 0:
            system = {"role": "system", "content": settings_text}
            self.dialog_history.append(system)
        new_message = {"role": "user", "content": new_message_text}
        self.dialog_history.append(new_message)

        if self.args.stream:
            result = self.request_stream_api_exec(self.dialog_history)
        else:
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.dialog_history
            ).choices[0].message.content
        response_message = {"role": "assistant", "content": result}
        self.dialog_history.append(response_message)
        response_message_text = result
        return response_message_text

    def request_stream_api_exec(self, dialog_history):
        # APIエンドポイント
        url = "https://api.openai.com/v1/chat/completions"
        # リクエストデータ
        data = {
            "model": "gpt-3.5-turbo",
            "messages": dialog_history,
            "temperature": 0.7,
            "stream": True
        }

        # リクエストヘッダー
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        # リクエスト送信
        response = requests.post(url, json=data, headers=headers, stream=True)
        # レスポンス出力
        # ストリーミングデータを受信
        res = ""
        print("system: ", end="")
        for line in response.iter_lines():
            if line:
                data = line.decode('utf-8')
             
                try:
                    data = json.loads(data.replace('data:', ''))
                    s = data["choices"][0]["delta"]["content"]
                    res += s
                    sys.stdout.flush() # 出力バッファリングを無効にする
                    print(s, end="")
                except (KeyError, json.decoder.JSONDecodeError):
                    continue
                if data == '[DONE]':
                    break
        print("\n")
        return res

# 実行プログラム
if __name__ == "__main__":
    # user_continuation_instruction = "以下の発話の続きを考えてください。"
    # system_generation_instruction = "以下の対話に対する応答を考えてください。"
    # dialog = Dialog(user_continuation_instruction, system_generation_instruction)
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description="Dialog System")
    parser.add_argument("--run_mode", type=str, default="default", help="Run mode: default or continual")
    parser.add_argument("--stream", action="store_true", help="Stream mode: stream flag")
    args = parser.parse_args()

    # Dialogクラスのインスタンス作成
    dialog = Dialog(user_continuation_instruction="ユーザー発話の続きを生成してください。",
                    system_generation_instruction="ユーザー発話の続きに対する応答を生成してください。", args=args)

    # --run_modeに応じてrun()かrun_continual()を実行
    if args.run_mode == "default":
        dialog.run()
    elif args.run_mode == "continual":
        dialog.run_continual()
    else:
        print("Invalid run mode. Please specify 'default' or 'continual'.")