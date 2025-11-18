package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
)

func handleStudentList(pool *BrowserPool, mainURL string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		fmt.Println("Start fetching student list")
		studentData, err := pool.FetchStudentList(mainURL)

		if err != nil {
			http.Error(w, "Failed to fetch student list", http.StatusInternalServerError)
			fmt.Fprintf(os.Stderr, "Failed to fetch student list: %v\n", err)
			return
		}

		fmt.Printf("Successfully fetched data for %d students\n", len(studentData))

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(studentData); err != nil {
			http.Error(w, "Failed to encode student data", http.StatusInternalServerError)
			fmt.Fprintf(os.Stderr, "Failed to encode student data: %v\n", err)
			return
		}
	}
}

func handleAudioDownload(pool *BrowserPool, mainURL string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		studentName := r.URL.Query().Get("studentName")
		if studentName == "" {
			http.Error(w, "Please query student name", http.StatusInternalServerError)
			fmt.Fprintln(os.Stderr, "Failed to download student audio: please query student name")
			return
		}

		downloadBasePath := r.URL.Query().Get("downloadBasePath")
		if downloadBasePath == "" {
			http.Error(w, "Please query download path", http.StatusInternalServerError)
			fmt.Fprintln(os.Stderr, "Failed to download student audio: please query download path")
			return
		}

		fmt.Printf("Start fetching %s's audio\n", studentName)
		err := pool.FetchStudentAudio(mainURL, studentName, downloadBasePath)

		if err != nil {
			http.Error(w, "Failed to download student audio", http.StatusInternalServerError)
			fmt.Fprintf(os.Stderr, "Failed to download student audio: %v\n", err)
			return
		}

		fmt.Printf("Successfully downloaded %s's audio\n", studentName)
	}
}

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "Argument number must be one")
		os.Exit(1)
	}

	cachePath := os.Args[1]

	pool := NewBrowserPool(cachePath)
	mainURL := "https://bluearchive.wiki"

	defer pool.Close()

	http.HandleFunc("/api/students", handleStudentList(pool, mainURL))
	http.HandleFunc("/api/audio", handleAudioDownload(pool, mainURL))

	fmt.Println("Starting server on localhost:6221")
	if err := http.ListenAndServe(":6221", nil); err != nil {
		fmt.Fprintf(os.Stderr, "Failed to start server: %v\n", err)
		os.Exit(1)
	}
}
