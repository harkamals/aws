package aws_cloudwatch_monitor

import (
	"encoding/json"
	"fmt"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/awserr"
	"github.com/aws/aws-sdk-go/aws/awsutil"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/cloudwatch"
	"io/ioutil"
	"log"
	"net/http"
	"math"
)

func Round(f float64) float64 {
	return math.Floor(f + .5)
}

func RoundPlus(f float64, places int) float64 {
	shift := math.Pow(10, float64(places))
	return Round(f*shift) / shift
}

func getInstanceMetadata() (metadata map[string]string, err error) {
	var data map[string]string
	resp, err := http.Get("http://169.254.169.254/latest/dynamic/instance-identity/document")
	if err != nil {
		return data, fmt.Errorf("can't reach metadata endpoint - %s", err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return data, fmt.Errorf("can't read metadata response body - %s", err)
	}

	json.Unmarshal(body, &data)

	return data, err
}

func addMetric(name, unit string, value float64, dimensions []*cloudwatch.Dimension, metricData []*cloudwatch.MetricDatum) (ret []*cloudwatch.MetricDatum, err error) {
	_metric := cloudwatch.MetricDatum{
		MetricName: aws.String(name),
		Unit:       aws.String(unit),
		Value:      aws.Float64(value),
		Dimensions: dimensions,
	}
	metricData = append(metricData, &_metric)
	return metricData, nil
}

func putMetric(metricdata []*cloudwatch.MetricDatum, namespace, region string) error {

	session2 := session.New(&aws.Config{Region: &region})
	svc := cloudwatch.New(session2)

	metric_input := &cloudwatch.PutMetricDataInput{
		MetricData: metricdata,
		Namespace:  aws.String(namespace),
	}

	resp, err := svc.PutMetricData(metric_input)
	if err != nil {
		if awsErr, ok := err.(awserr.Error); ok {
			return fmt.Errorf("[%s] %s", awsErr.Code, awsErr.Message)
		} else if err != nil {
			return err
		}
	}
	log.Println(awsutil.StringValue(resp))
	return nil
}

func getDimensions(metadata map[string]string) (ret []*cloudwatch.Dimension) {

	var _ret []*cloudwatch.Dimension

	instanceIdName := "InstanceId"
	instanceIdValue, ok := metadata["instanceId"]
	if ok {
		dim := cloudwatch.Dimension{
			Name:  aws.String(instanceIdName),
			Value: aws.String(instanceIdValue),
		}
		_ret = append(_ret, &dim)
	}

	imageIdName := "ImageId"
	imageIdValue, ok := metadata["imageId"]
	if ok {
		dim := cloudwatch.Dimension{
			Name:  aws.String(imageIdName),
			Value: aws.String(imageIdValue),
		}
		_ret = append(_ret, &dim)
	}

	instanceTypeName := "InstanceType"
	instanceTypeValue, ok := metadata["instanceType"]
	if ok {
		dim := cloudwatch.Dimension{
			Name:  aws.String(instanceTypeName),
			Value: aws.String(instanceTypeValue),
		}
		_ret = append(_ret, &dim)
	}

	fileSystemName := "FileSystem"
	fileSystemValue, ok := metadata["fileSystem"]
	if ok {
		dim := cloudwatch.Dimension{
			Name:  aws.String(fileSystemName),
			Value: aws.String(fileSystemValue),
		}
		_ret = append(_ret, &dim)
	}

	return _ret
}
