package aws_cloudwatch_monitor

import (
	"github.com/guillermo/go.procmeminfo"
	"syscall"
	"errors"
	"fmt"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/awserr"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/autoscaling"
)

// Memory Usage(percent of used, bytes of Used, Avaliable and Total)
func memoryUsage() (memUtil, memUsed, memAvail, swapUtil, swapUsed float64, err error) {
	meminfo := &procmeminfo.MemInfo{}
	meminfo.Update()

	_memUsed := float64(meminfo.Used())
	_memAvail := float64(meminfo.Available())
	_memTotal := float64(meminfo.Total())
	_memUtil := (_memUsed / _memTotal) * 100
	_swapUtil := float64(meminfo.Swap())
	_swapUsed := float64((*meminfo)["SwapCached"])

	return Round(_memUtil), _memUsed, _memAvail, Round(_swapUtil), _swapUsed, err
}

// Disk Space total and free bytes available for path like "df command"
func DiskSpace(path string) (diskspaceUtil float64, diskspaceUsed, diskspaceAvail int, diskinodesUtil float64, err error) {
	s := syscall.Statfs_t{}
	err = syscall.Statfs(path, &s)
	if err != nil {
		return 0, 0, 0, 0, err
	}
	_total := int(s.Bsize) * int(s.Blocks)
	_avail := int(s.Bsize) * int(s.Bavail)
	_used := _total - _avail
	_diskspaceUtil := (float64(_used) / float64(_total)) * 100

	_inodesTotal := int(s.Files)
	_inodesFree := int(s.Ffree)
	_inodesUtil := 100 * (1 - float64(_inodesFree)/float64(_inodesTotal))
	return Round(_diskspaceUtil), _used, _avail, Round(_inodesUtil), err
}

func getAutoscalingGroup(instanceId string, region string) (*string, error) {
	session := session.New(&aws.Config{Region: &region})
	svc := autoscaling.New(session)

	params := &autoscaling.DescribeAutoScalingInstancesInput{
		InstanceIds: []*string{&instanceId},
		MaxRecords:  aws.Int64(1),
	}

	resp, err := svc.DescribeAutoScalingInstances(params)
	if err != nil {
		if awsErr, ok := err.(awserr.Error); ok {
			return nil, fmt.Errorf("[%s] %s", awsErr.Code, awsErr.Message)
		} else if err != nil {
			return nil, err
		}
	}

	if len(resp.AutoScalingInstances) == 0 {
		return nil, errors.New("No autoscaling group found")
	}

	return resp.AutoScalingInstances[0].AutoScalingGroupName, nil
}
