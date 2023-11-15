import os


def convert_to(path, exp_type: str):
    if os.path.isdir(path) and exp_type != ".ogg":
        src_list = os.listdir(path)

        for audio in src_list:
            try:
                os.system(f"ffmpeg.exe -i ./{path}/{audio} ./{path}/{audio[:-4]}{exp_type}")
                os.remove(f"./{path}/{audio}")
                print(f"./{path}/{audio} 파일 삭제")
            except Exception as e:
                print("파일 변환중 오류 발생... 오류 메시지: ", e)
