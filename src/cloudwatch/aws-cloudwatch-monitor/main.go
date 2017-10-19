package main

import (
	"fmt"
	_ "github.com/aws/aws-sdk-go/aws"
	_ "github.com/aws/aws-sdk-go/service/cloudwatch"
)

func main() {
	fmt.Println("Hello World")

}
