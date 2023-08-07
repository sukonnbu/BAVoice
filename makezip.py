import os
import zipfile
def make_zip(path):
    if os.path.isdir(path):
        zip_file = zipfile.ZipFile(path + f"/{path[2:-1]}.zip", "w")

        for file in os.listdir(path):
            try:
                if file.endswith(".wav"):
                    zip_file.write(os.path.join(path, file), compress_type = zipfile.ZIP_DEFLATED)
                    print(file + " 파일 추가")

                    os.remove(os.path.join(path, file))
                    print("디렉토리에서", file, "파일 삭제")
            except Exception as e:
                print("zip 파일 생성중 오류 발생...\n오류 메시지: ", e)

        zip_file.close()

        print("ZIP 파일 생성 완료")

if __name__ == "__main__":
    character = input("원하는 블루아카 캐릭터를 영문으로 입력하세요(예시: Azusa) : ")
    path = f"./{character.replace(' ', '_')}/"

    make_zip(path)
