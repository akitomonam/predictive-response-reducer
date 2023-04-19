import json
import openai

# 対話制御クラス
class Dialog:
    def __init__(self, user_continuation_instruction:str, system_generation_instruction:str) -> None:
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
            messages=prompt
        )
        return result.choices[0].message.content
    
    # 対話を実行する関数
    def run(self):
        while True:
            user_input = input("user: ")
            if user_input == "exit":
                break
            user_output = self.user_continuation(user_input)
            print("user_continuation: ", user_output)
            user_utt = user_input + user_output
            system_output = self.system_generation(user_utt)
            print("system: ", system_output)


# 実行プログラム
if __name__ == "__main__":
    user_continuation_instruction = "以下の発話の続きを考えてください。"
    system_generation_instruction = "以下の対話に対する応答を考えてください。"
    dialog = Dialog(user_continuation_instruction, system_generation_instruction)
    dialog.run()
    