package main

import (
	"fmt"
	"log"
	"net/http"
)

func main() {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "Hello from the Go sample app")
	})
	log.Println("Listening on port 8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
