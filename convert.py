import os


def convert_to(path: str, set_prg_bar, set_log, exp_type: str):
    if exp_type != ".ogg":
        src_list = os.listdir(path)

        for i in range(0, len(src_list)):
            try:
                # 파일 변환
                os.system(f"ffmpeg.exe -i ./{path}/{src_list[i]} ./{path}/{src_list[i][:-4]}{exp_type} -loglevel quiet")
                set_log(f"{path}/{src_list[i]} 파일 변환 성공")

                os.remove(f"./{path}/{src_list[i]}")
                set_log(f"{path}/{src_list[i]} 파일 삭제")

            except Exception as e:
                set_log(f"파일 변환중 오류 발생...\n오류메시지: {e}")

            set_prg_bar("sub", i/len(src_list)*100)
