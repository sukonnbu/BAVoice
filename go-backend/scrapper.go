package main

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/chromedp/chromedp"
	_ "github.com/mattn/go-sqlite3"
)

type BrowserPool struct {
	allocCtx context.Context
	cancel   context.CancelFunc
	db       *sql.DB
}

type StudentData struct {
	Name        string `json:"name"`
	Rank        int    `json:"rank"`
	SchoolName  string `json:"schoolName"`
	ClubName    string `json:"clubName"`
	AttackType  string `json:"attackType"`
	DefenceType string `json:"defenceType"`
	IsGlobal    bool   `json:"isGlobal"`
	ImageURL    string `json:"imageUrl"`
}

func NewBrowserPool(cachePath string) *BrowserPool {
	// FOR PRODUCTION
	opts := append(chromedp.DefaultExecAllocatorOptions[:], chromedp.NoFirstRun, chromedp.NoDefaultBrowserCheck)
	// FOR DEBUG
	// opts := append(chromedp.DefaultExecAllocatorOptions[:], chromedp.Flag("headless", false), chromedp.NoFirstRun, chromedp.NoDefaultBrowserCheck)
	allocCtx, cancelAlloc := chromedp.NewExecAllocator(context.Background(), opts...)

	db, err := sql.Open("sqlite3", cachePath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to open database: %v\n", err)
		os.Exit(1)
	}

	statement, err := db.Prepare("CREATE TABLE IF NOT EXISTS image_cache (student_name TEXT PRIMARY KEY, image_url TEXT)")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to prepare table creation statement: %v\n", err)
		os.Exit(1)
	}
	_, err = statement.Exec()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to create table: %v\n", err)
		os.Exit(1)
	}

	// fmt.Println("Headless Browser session started.")
	return &BrowserPool{
		allocCtx: allocCtx,
		cancel:   cancelAlloc,
		db:       db,
	}
}

func (b *BrowserPool) Close() {
	b.cancel()
	if err := b.db.Close(); err != nil {
		fmt.Fprintf(os.Stderr, "Failed to close database: %v\n", err)
	}
	// fmt.Println("Headless Browser session closed")
}

func (b *BrowserPool) FetchClubMap(mainURL string) (map[string]string, error) {
	ctx, cancel := chromedp.NewContext(b.allocCtx)
	defer cancel()

	taskCtx, taskCancel := context.WithTimeout(ctx, 10*time.Second)
	defer taskCancel()

	studentURL, err := url.JoinPath(mainURL, "wiki", "Azusa")
	if err != nil {
		return nil, fmt.Errorf("could not resolve student URL: %v", err)
	}

	if err := chromedp.Run(taskCtx,
		chromedp.Navigate(studentURL),
		chromedp.WaitVisible("div.navbox[aria-labelledby='Kivotos']", chromedp.ByQuery),
	); err != nil {
		return nil, fmt.Errorf("failed to load page: %v", err)
	}

	var data map[string]string
	script := `(function() {
		const clubMap = {};

		const schoolList = document.querySelectorAll("div.navbox[aria-labelledby='Kivotos'] > table > tbody > tr > td");
		const schoolArray = [...schoolList];
		schoolArray.slice(0, 13).forEach(school => {
			const clubList = school.querySelectorAll("table.navbox-subgroup > tbody > tr");
			const clubArray = [...clubList];
			clubArray.slice(1).forEach(club => {
				const clubHeader = club.querySelector("th.navbox-group");
				const clubLink = clubHeader.querySelector("a");

				let clubName;
				if (clubLink) {
					clubName = clubLink.textContent.trim();
				} else {
					clubName = clubHeader.textContent.trim();
				}

				const students = club.querySelectorAll("div.character-list-item");
				students.forEach(student => {
					const studentName = student.querySelector("td.student-name > a").textContent.trim();
					clubMap[studentName] = clubName;
				});
			});
		});

		return clubMap;
	})()`

	if err := chromedp.Run(taskCtx, chromedp.Evaluate(script, &data)); err != nil {
		return nil, fmt.Errorf("failed to evaluate script: %v", err)
	}

	if data == nil {
		return nil, fmt.Errorf("failed to fetch club data")
	}

	return data, nil
}

func DownloadAudio(audioURL string, audioName string, downloadPath string) error {
	client := http.Client{Timeout: 10 * time.Second}

	req, err := http.NewRequest("GET", audioURL, nil)
	if err != nil {
		return fmt.Errorf("failed to create request: %v", err)
	}

	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

	res, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to download audio: %v", err)
	}
	defer func(Body io.ReadCloser) {
		_ = Body.Close()
	}(res.Body)

	if res.StatusCode != http.StatusOK {
		return fmt.Errorf("failed to download audio, status code: %v", res.StatusCode)
	}

	audioFilePath := filepath.Join(downloadPath, audioName)

	out, err := os.Create(audioFilePath)
	if err != nil {
		return fmt.Errorf("failed to create audio: %v", err)
	}
	defer func() {
		_ = out.Close()
	}()

	_, err = io.Copy(out, res.Body)
	if err != nil {
		return fmt.Errorf("failed to download audio: %v", err)
	}

	return nil
}

func (b *BrowserPool) processAudioJob(mainURL string, audioInfoURL string) (string, string, error) {
	audioMainURL, err := url.JoinPath(mainURL, audioInfoURL)

	if err != nil {
		return "", "", fmt.Errorf("failed to resolve audio URL: %v", err)
	}

	ctx, cancel := chromedp.NewContext(b.allocCtx)
	defer cancel()

	taskCtx, taskCancel := context.WithTimeout(ctx, 15*time.Second)
	defer taskCancel()

	var data map[string]interface{}
	if err = chromedp.Run(taskCtx,
		chromedp.Navigate(audioMainURL),
		chromedp.WaitVisible("a.internal", chromedp.ByQuery),
		chromedp.Evaluate(`(function() {
				const audio_link = document.querySelector('a.internal')
				const audio_URL = audio_link.getAttribute("href");
				const audio_name = audio_link.getAttribute("title");
				
				return {"audio_URL": audio_URL, "audio_name": audio_name};
			})()`, &data),
	); err != nil {
		return "", "", fmt.Errorf("failed to get audio URL")
	}

	audioURL, ok := data["audio_URL"].(string)
	if !ok {
		return "", "", fmt.Errorf("failed to resolve audio URL")
	}

	if strings.HasPrefix(audioURL, "//") {
		audioURL = "https:" + audioURL
	}

	audioName, ok := data["audio_name"].(string)
	if !ok {
		return "", "", fmt.Errorf("failed to resolve audio name")
	}

	return audioURL, audioName, nil
}

func (b *BrowserPool) audioWorker(mainURL string, downloadPath string, jobs <-chan string, wg *sync.WaitGroup) {
	defer wg.Done()
	for audioInfoURL := range jobs {
		audioURL, audioName, err := b.processAudioJob(mainURL, audioInfoURL)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Failed to fetch audio URL for %s: %v\n", audioInfoURL, err)
			continue
		}

		if err := DownloadAudio(audioURL, audioName, downloadPath); err != nil {
			fmt.Fprintf(os.Stderr, "Failed to download audio %s: %v\n", audioName, err)
			continue
		}
	}
}

func (b *BrowserPool) imageWorker(mainURL string, jobs <-chan StudentData, results chan<- StudentData, wg *sync.WaitGroup) {
	defer wg.Done()
	for student := range jobs {
		imageURL, err := b.FetchStudentImageURL(mainURL, student.Name)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Failed to fetch image for %s: %v\n", student.Name, err)
			student.ImageURL = ""
		} else {
			student.ImageURL = imageURL
		}
		results <- student
	}
}

func (b *BrowserPool) FetchStudentAudio(
	mainURL string, studentName string, downloadBasePath string,
) error {
	fmt.Println("Fetching student audio")

	ctx, cancel := chromedp.NewContext(b.allocCtx)
	defer cancel()

	studentListURL, err := url.JoinPath(mainURL, "wiki", studentName, "audio")
	if err != nil {
		return fmt.Errorf("could not resolve student audio URL: %v", err)
	}

	if err := chromedp.Run(ctx,
		chromedp.Navigate(studentListURL),
		chromedp.WaitVisible("body", chromedp.ByQuery),
	); err != nil {
		return fmt.Errorf("failed to load page: %v", err)
	}

	var audioCount int
	if err := chromedp.Run(ctx,
		chromedp.Evaluate(`document.querySelectorAll("span.audio > a").length`, &audioCount),
	); err != nil {
		return fmt.Errorf("failed to count audios")
	}

	jobs := make(chan string, audioCount)

	downloadPath := filepath.Join(downloadBasePath, studentName)
	if err = os.MkdirAll(downloadPath, 0755); err != nil {
		return fmt.Errorf("failed to create download directory")
	}

	var wg sync.WaitGroup
	for w := 1; w <= 3; w++ {
		wg.Add(1)
		go b.audioWorker(mainURL, downloadPath, jobs, &wg)
	}

	for i := 0; i < audioCount; i++ {
		var audioInfoURL string
		script := fmt.Sprintf(`(function() {
			const audio_list = document.querySelectorAll("span.audio > a");
			const audio = audio_list[%d];

			const href = audio.getAttribute("href") || "";

			return href;
		})()`, i)

		err := chromedp.Run(ctx, chromedp.Evaluate(script, &audioInfoURL))
		if err != nil {
			fmt.Fprintf(os.Stderr, "Failed to pull %dth audio URL: %v\n", i+1, err)
			continue
		}

		if audioInfoURL == "" {
			continue
		}

		jobs <- audioInfoURL
	}
	close(jobs)

	wg.Wait()

	return nil
}

func (b *BrowserPool) FetchStudentList(
	mainURL string,
) ([]StudentData, error) {
	fmt.Println("Fetching club map")
	clubMap, err := b.FetchClubMap(mainURL)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch club map: %v", err)
	}
	fmt.Println("Fetching student list")

	ctx, cancel := chromedp.NewContext(b.allocCtx)
	defer cancel()

	studentListURL, err := url.JoinPath(mainURL, "wiki", "Characters")
	if err != nil {
		return nil, fmt.Errorf("could not resolve student list URL: %v", err)
	}

	if err := chromedp.Run(ctx,
		chromedp.Navigate(studentListURL),
		chromedp.WaitVisible("charactertable", chromedp.ByID),
	); err != nil {
		return nil, fmt.Errorf("failed to load page: %v", err)
	}

	var rowCount int
	if err := chromedp.Run(ctx,
		chromedp.Evaluate(`document.querySelectorAll("#charactertable tbody tr").length`, &rowCount),
	); err != nil {
		return nil, fmt.Errorf("failed to count students")
	}

	jobs := make(chan StudentData, rowCount)
	results := make(chan StudentData, rowCount)

	var wg sync.WaitGroup
	for w := 1; w <= 3; w++ {
		wg.Add(1)
		go b.imageWorker(mainURL, jobs, results, &wg)
	}

	for i := 0; i < rowCount; i++ {
		var data map[string]interface{}
		script := fmt.Sprintf(`(function() {
			const studentRows = document.querySelectorAll("table#charactertable > tbody > tr");
			const studentRow = studentRows[%d];
			if (!studentRow) return null;

			const rank = studentRow.getAttribute("data-rarity") || "0";
			const school = studentRow.getAttribute("data-school") || "";
			const attack = studentRow.getAttribute("data-attack") || "";
			const defence = studentRow.getAttribute("data-armor") || "";

			const isGlobal = studentRow.getAttribute("data-releasedate-gl") !== "";

			const studentData = studentRow.querySelectorAll("td");
			const nameLink = studentData[1].querySelector("a");
			const name = nameLink.textContent.trim() || "";

			return {
				"name": name,
				"rank": rank,
				"schoolName": school,
				"attackType": attack,
				"defenceType": defence,
				"isGlobal": isGlobal,
			};
		})()`, i)

		err := chromedp.Run(ctx, chromedp.Evaluate(script, &data))
		if err != nil {
			fmt.Fprintf(os.Stderr, "Failed to pull %dth student data: %v\n", i+1, err)
			continue
		}

		if data == nil {
			continue
		}

		rank, err := strconv.Atoi(data["rank"].(string))
		if err != nil {
			fmt.Fprintf(os.Stderr, "Failed to convert rank to int: %v\n", err)
			continue
		}

		name := data["name"].(string)
		plainName := strings.Split(name, " (")[0]
		clubName := clubMap[plainName]

		student := StudentData{
			Name:        name,
			Rank:        rank,
			SchoolName:  data["schoolName"].(string),
			ClubName:    clubName,
			AttackType:  data["attackType"].(string),
			DefenceType: data["defenceType"].(string),
			IsGlobal:    data["isGlobal"].(bool),
		}
		jobs <- student
	}
	close(jobs)

	go func() {
		wg.Wait()
		close(results)
	}()

	var finalResults []StudentData
	for result := range results {
		finalResults = append(finalResults, result)
	}

	return finalResults, nil
}

func (b *BrowserPool) FetchStudentImageURL(mainURL string, studentName string) (string, error) {
	var cachedURL string
	err := b.db.QueryRow("SELECT image_url FROM image_cache WHERE student_name = ?", studentName).Scan(&cachedURL)
	if err == nil {
		// fmt.Printf("Cache hit for %s\n", studentName)
		return cachedURL, nil
	} else if !errors.Is(err, sql.ErrNoRows) {
		fmt.Fprintf(os.Stderr, "Failed to query cache for %s: %v", studentName, err)
	}

	fmt.Printf("Cache miss for %s, fetching from web\n", studentName)
	ctx, cancel := chromedp.NewContext(b.allocCtx)
	defer cancel()

	taskCtx, taskCancel := context.WithTimeout(ctx, 10*time.Second)
	defer taskCancel()

	studentURL, _ := url.JoinPath(mainURL, "wiki", studentName)

	var imageURL string
	err = chromedp.Run(taskCtx,
		chromedp.Navigate(studentURL),
		chromedp.WaitVisible("table.character", chromedp.ByQuery),
		chromedp.Evaluate(`(function() {
			const image = document.querySelector('table.character article#tabber-Profile_Image img');
			const imageURLSet = image.getAttribute("srcset") || "";
			
			if (!imageURLSet) return null;

			const entry = imageURLSet.split(",")[1];
			const imageURL = entry.trim().split(" ")[0];

			return imageURL;
		})()`, &imageURL),
	)

	if err != nil {
		return "", fmt.Errorf("failed to fetch image for %s: %v", studentName, err)
	}

	stmt, err := b.db.Prepare("INSERT INTO image_cache (student_name, image_url) VALUES (?, ?)")
	if err != nil {
		return "", fmt.Errorf("failed to prepare insert statement for %s: %v", studentName, err)
	} else {
		_, err := stmt.Exec(studentName, imageURL)
		if err != nil {
			return "", fmt.Errorf("failed to cache image URL for %s: %v", studentName, err)
		} else {
			fmt.Printf("Cached new image URL for %s\n", studentName)
		}
	}

	return imageURL, nil
}
