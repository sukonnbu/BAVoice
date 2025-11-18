# Blue Archive Voice Downloader

Blue Archive Voice Downloader는 [블루 아카이브 Wiki](https://bluearchive.wiki)에서 학생(캐릭터)의 음성 파일을 쉽게 다운로드할 수 있도록 제작된 데스크톱 애플리케이션입니다.

![logo](logo.png)

## ✨ 주요 기능

*   **학생 목록 조회**: 게임 내 모든 학생의 프로필 이미지를 포함한 목록을 불러옵니다.
*   **상세 필터링**: 소속 학교, 동아리, 공격 타입, 방어 타입 등 다양한 조건으로 학생을 필터링할 수 있습니다.
*   **다중 선택 및 다운로드**: 여러 학생을 동시에 선택하여 음성 파일을 한 번에 다운로드할 수 있습니다.
*   **자동 저장**: 다운로드된 음성 파일은 사용자의 '다운로드' 폴더에 학생 이름으로된 폴더 내에 자동으로 정리되어 저장됩니다.

## 🛠️ 기술 스택

*   **프레임워크**: [Tauri](https://tauri.app/) (Rust)
*   **프론트엔드**: [Vue.js](https://vuejs.org/) (with TypeScript), [Pinia](https://pinia.vuejs.org/)
*   **백엔드 (사이드카)**: [Go](https://go.dev/)
*   **패키지 매니저**: [pnpm](https://pnpm.io/)

## ⚙️ 작동 방식

이 애플리케이션은 Tauri 프레임워크를 기반으로 하며, 웹 기술(Vue.js)로 UI를 구현합니다. 데이터 스크래핑을 담당하는 Go 프로그램을 사이드카(Sidecar)로 실행하여 학생 데이터를 가져오고 음성 파일을 다운로드합니다.

1.  앱이 시작되면 Rust 기반의 Tauri 백엔드가 Go로 작성된 스크래핑 서버를 백그라운드에서 실행합니다.
2.  Go 서버는 [블루 아카이브 Wiki](https://bluearchive.wiki)에서 학생 목록과 음성 파일 URL을 스크래핑하여 로컬 API 형태로 제공합니다.
3.  Vue.js 프론트엔드는 이 로컬 API를 호출하여 학생 목록을 표시하고, 사용자의 상호작용을 처리합니다.
4.  사용자가 다운로드를 요청하면, 프론트엔드는 Tauri 백엔드에 선택된 학생 목록을 전달하고, 백엔드는 다시 Go 서버에 요청하여 음성 파일을 사용자의 PC에 저장합니다.

## 🚀 개발 환경 설정

프로젝트를 로컬 환경에서 실행하려면 다음 절차를 따르세요.

**요구사항:**
*   [Node.js](https://nodejs.org/ko) (v18 이상)
*   [Rust](https://www.rust-lang.org/tools/install)
*   [Go](https://go.dev/doc/install)
*   [pnpm](https://pnpm.io/installation)

1.  **저장소 복제**
    ```bash
    git clone https://github.com/your-username/ba-downloader.git
    cd ba-downloader
    ```

2.  **의존성 설치**
    ```bash
    pnpm install
    ```

3.  **Go 백엔드 빌드**
    Go로 작성된 사이드카를 빌드합니다. 이 명령은 `go-backend` 디렉토리의 소스를 컴파일하여 Tauri가 사용할 수 있는 `src-tauri/binaries` 폴더로 실행 파일을 옮깁니다.
    ```bash
    pnpm go:build
    ```

4.  **개발 서버 실행**
    Tauri 개발 서버를 시작합니다.
    ```bash
    pnpm tauri dev
    ```

## 📦 프로덕션 빌드

애플리케이션을 배포용으로 빌드하려면 다음 명령을 실행하세요. 빌드가 완료되면 `src-tauri/target/release/bundle` 디렉토리에서 설치 파일을 찾을 수 있습니다.

```bash
pnpm tauri build
```
