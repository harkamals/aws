package aws_cloudwatch_monitor

import (
	"fmt"
	"io/ioutil"
	"encoding/json"
	"net/http"
	_ "github.com/aws/aws-sdk-go/aws"
	_ "github.com/aws/aws-sdk-go/service/cloudwatch"
)

func GetMetaData() (metadata map[string]string, err error) {

	var data map[string]string
	resp, err := http.Get("http://169.254.169.254/latest/dynamic/instance-identity/document")
	if err != nil {
		return data, fmt.Errorf("cannot reach endpoint: %s", err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return data, fmt.Errorf("can't read metadata response: %s", err)
	}

	json.Unmarshal(body, &data)
	return data, err
}
