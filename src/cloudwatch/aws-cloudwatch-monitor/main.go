package main

import (
	"fmt"
)

func main() {
	fmt.Println("Hello World")

	_, err := getMetaData()

	if err != nil {
		fmt.Println(err)
	}

}
