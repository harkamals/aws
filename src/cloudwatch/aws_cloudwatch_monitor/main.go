package aws_cloudwatch_monitor

import "fmt"

func Main()  {
	fmt.Println("aws_cloudwatch_monitor is starting")

	_, err := GetMetaData()

	if err != nil {
		fmt.Println(err)
	}
}
