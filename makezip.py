import os
import zipfile


# 파일 압축
def make_zip(path: str, set_log, exp_type: str):
    # 압축파일 생성
    zip_file = zipfile.ZipFile(path + f"/{path[2:-1]}.zip", "w")

    for audio in os.listdir(path):
        try:
            if audio.endswith(exp_type):
                # 음성 파일 추가
                zip_file.write(os.path.join(path, audio), compress_type=zipfile.ZIP_DEFLATED)
                set_log(f".zip에 {audio} 파일 추가됨")

                os.remove(os.path.join(path, audio))
                set_log(f"{audio} 파일 삭제됨")

        except Exception as e:
            set_log(f".zip 생성 중 오류 발생...\n오류메시지: {e}")

    zip_file.close()

    set_log(".zip 파일 생성 완료")
