use std::path::PathBuf;
use std::sync::{Mutex, MutexGuard};

use tauri::{async_runtime, AppHandle, Emitter, Manager, State, WindowEvent};
use tauri_plugin_shell::{process::CommandChild, process::CommandEvent, ShellExt};

use dirs_next::download_dir;
use tauri_plugin_shell::process::Command;
use tokio::sync::mpsc::Receiver;

fn get_download_path() -> Option<PathBuf> {
    download_dir()
}

struct AppState {
    child_process: Mutex<Option<CommandChild>>,
}

fn start_server(app: AppHandle, state: State<'_, AppState>) {
    let mut exe_dir: PathBuf;
    match std::env::current_dir() {
        Ok(path_buf) => exe_dir = path_buf,
        Err(e) => {
            eprintln!("ERROR: {}", e);
            return;
        }
    };

    exe_dir.push("cache.db");

    let cache_path: String = exe_dir.as_path().to_string_lossy().to_string();

    let sidecar: Command = app.shell().sidecar("backend").unwrap().args([cache_path]);
    let (mut rx, child): (Receiver<CommandEvent>, CommandChild) =
        sidecar.spawn().expect("failed to create backend api");

    let mut child_process: MutexGuard<Option<CommandChild>> =
        state.inner().child_process.lock().unwrap();
    *child_process = Some(child);

    let app_handle: AppHandle = app.clone();
    async_runtime::spawn(async move {
        loop {
            if let Some(event) = rx.recv().await {
                match event {
                    CommandEvent::Stdout(line) => {
                        if let Ok(decoded_string) = String::from_utf8(line) {
                            app_handle
                                .emit("sidecar-stdout", decoded_string.trim())
                                .expect("failed to emit stdout");
                        }
                    }
                    CommandEvent::Stderr(line) => {
                        if let Ok(decoded_string) = String::from_utf8(line) {
                            app_handle
                                .emit("sidecar-stderr", decoded_string.trim())
                                .expect("failed to emit stderr");
                        }
                    }
                    CommandEvent::Terminated(payload) => {
                        println!("[ba-downloader-api] Terminated with payload: {:?}", payload);
                        break;
                    }
                    _ => {}
                }
            }
        }
    });
}

#[derive(Debug, serde::Serialize, serde::Deserialize)]
#[serde(rename_all = "camelCase")]
struct StudentData {
    name: String,
    rank: i32,
    school_name: String,
    club_name: String,
    attack_type: String,
    defence_type: String,
    is_global: bool,
    image_url: String,
}

#[tauri::command]
async fn fetch_student_list() -> Result<Vec<StudentData>, String> {
    let url = "http://localhost:6221/api/students";

    match reqwest::get(url).await {
        Ok(response) => match response.json::<Vec<StudentData>>().await {
            Ok(student_list) => Ok(student_list),
            Err(e) => Err(format!("JSON deserialize failed: {}", e)),
        },
        Err(e) => Err(format!("HTTP request failed: {}", e)),
    }
}

#[tauri::command]
async fn download_voices(student_list: Vec<String>) -> Result<(), String> {
    let url = "http://localhost:6221/api/audio";
    let download_path = match get_download_path() {
        Some(path) => path,
        None => {
            return Err("Failed to get download directory".to_string());
        }
    };

    let download_path_str = download_path.as_path().to_string_lossy();

    let mut errors = Vec::new();

    for student in student_list.into_iter() {
        let student_url = format!(
            "{}?studentName={}&downloadBasePath={}",
            url, student, download_path_str
        );

        match reqwest::get(&student_url).await {
            Ok(response) => {
                if !response.status().is_success() {
                    let error_msg = format!(
                        "Failed to download voices for {}: Server returned status {}",
                        student,
                        response.status()
                    );
                    eprintln!("{}", error_msg);
                    errors.push(error_msg);
                }
            }
            Err(e) => {
                let error_msg = format!("Failed to send request for {}: {}", student, e);
                eprintln!("{}", error_msg);
                errors.push(error_msg);
            }
        }
    }

    if errors.is_empty() {
        Ok(())
    } else {
        Err(errors.join("\n"))
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(AppState {
            child_process: Mutex::new(None),
        })
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let handle = app.handle().clone();
            async_runtime::spawn(async move {
                let state = handle.state::<AppState>();
                start_server(handle.clone(), state)
            });
            Ok(())
        })
        .on_window_event(|window, event| {
            if let WindowEvent::Destroyed = event {
                let state = window.state::<AppState>();
                let mut child_process = state.child_process.lock().unwrap();
                if let Some(child) = child_process.take() {
                    child.kill().expect("failed to kill sidecar");
                }
            }
        })
        .invoke_handler(tauri::generate_handler![
            fetch_student_list,
            download_voices
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
