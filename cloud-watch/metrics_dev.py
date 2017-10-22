"""
This will get some useful stats that are not currently in cloudwatch,
so as to allow them to be monitored and alerted.
Useage:
- Requires crontab that will look like this:
    * * * * * . $HOME/.bash_profile; python /opt/aws/cloudwatch.py

"""
from collections import namedtuple
import os
import psutil
import boto3
from boto.utils import get_instance_metadata


class Metric():
    """
    This is the metric class that is used as a data structure as well as for
    the formatting and sending of cloudwatch metrics.
    """
    _metrics = {}

    def add_metric(self, key, value, unit='Percent'):
        """This will get the format the metrics correctly for cloudwatch."""
        if unit not in self._metrics:
            self._metrics[unit] = {}
        self._metrics[unit].update({key: value})

    def get_auto_scaling_group_name(self, instance_id, region):
        """This will get the autoscaling data to send to cloudwatch."""
        autoscale = boto3.client('autoscaling', region_name=region)
        response = autoscale.describe_auto_scaling_instances(
            InstanceIds=[
                instance_id,
            ]
        )
        if len(response) > 0:
            for key in response['AutoScalingInstances']:
                return key['AutoScalingGroupName']

    def send(self):
        """This will send the data to cloudwatch."""
        metadata = get_instance_metadata()
        instance_id = metadata['instance-id']
        region = metadata['placement']['availability-zone'][0:-1]
        cloudwatch = boto3.client('cloudwatch', region_name=region)

        group = self.get_auto_scaling_group_name(instance_id, region)

        for (unit, metrics) in self._metrics.items():
            for key in metrics.keys():
                response = cloudwatch.put_metric_data(
                    Namespace='EC2',
                    MetricData=[
                        {
                            'MetricName': key,
                            'Dimensions': [
                                {
                                    'Name': 'InstanceId',
                                    'Value': instance_id
                                },
                            ],
                            'Value': metrics[key],
                            'Unit': unit
                        },
                    ]
                )

                if group:
                    response = cloudwatch.put_metric_data(
                        Namespace='EC2',
                        MetricData=[
                            {
                                'MetricName': key,
                                'Dimensions': [
                                    {
                                        'Name': 'AutoScalingGroup',
                                        'Value': group
                                    },
                                ],
                                'Value': metrics[key],
                                'Unit': unit
                            },
                        ]
                    )


def disk_partitions(disk_ntuple, all=False):
    """Return all mountd partitions as a named tuple.
    If all == False return physical partitions only.
    """
    phydevs = []
    if os.path.exists('/proc/filesystems'):
        my_file = open('/proc/filesystems', 'r')
        for line in my_file:
            if not line.startswith('nodev'):
                phydevs.append(line.strip())
    else:
        print ('path does not exist: /proc/filesystems')

    retlist = []

    if os.path.exists('/etc/mtab'):
        my_file = open('/etc/mtab', 'r')
        for line in my_file:
            if not all and line.startswith('none'):
                continue
            fields = line.split()
            device = fields[0]
            mountpoint = fields[1]
            fstype = fields[2]
            if not all and fstype not in phydevs:
                continue
            if device == 'none':
                device = ''
            ntuple = disk_ntuple(device, mountpoint, fstype)
            retlist.append(ntuple)
    else:
        print ('path does not exist: /etc/mtab')

    return retlist


def disk_usage(path, usage_ntuple):
    """Return disk usage associated with path."""
    my_fs_stats = os.statvfs(path)
    free = (my_fs_stats.f_bavail * my_fs_stats.f_frsize)
    total = (my_fs_stats.f_blocks * my_fs_stats.f_frsize)
    used = (my_fs_stats.f_blocks - my_fs_stats.f_bfree) * my_fs_stats.f_frsize
    try:
        percent = (float(used) / total) * 100
    except ZeroDivisionError:
        percent = 0
    # NB: the percentage is -5% than what shown by df due to
    # reserved blocks that we are currently not considering:
    # http://goo.gl/sWGbH
    return usage_ntuple(total, used, free, round(percent, 1))


def get_process_state(process_name):
    for process in psutil.pids():
        p = psutil.Process(process)
        if p.name() == process_name:
            print (process_name + ":" + p.status())
            return p.status()

    print process_name + ":missing"
    return "missing"


def get_mount_usage(mount_name):
    if os.path.exists(mount_name):
        # print (mount_name + ":", psutil.disk_usage(mount_name))

        usage = psutil.disk_usage(mount_name).percent
        print (mount_name + ": %.2f" % usage)
        return "%.2f" % usage
    else:
        print (mount_name + ": missing")
        return 0.00


def get_metrics():
    """This function will gather the main components to send to cloudwatch."""
    disk_ntuple = namedtuple('partition', 'device mountpoint fstype')
    usage_ntuple = namedtuple('usage', 'total used free percent')

    # This is due to cron not having access to the normal environment variables.
    # os.environ['HTTP_PROXY'] = 'http://10.192.116.73:8080/'
    # os.environ['HTTPS_PROXY'] = 'http://10.192.116.73:8080/'
    # os.environ['NO_PROXY'] = '169.254.169.254,127.0.0.1,localhost'

    cpu_load_1_sec = psutil.cpu_percent(interval=1)
    cpu_load_5_sec = psutil.cpu_percent(interval=5)
    # cpu_load_15_sec = psutil.cpu_percent(interval=15)
    # cpu_load_60_sec = psutil.cpu_percent(interval=60)

    mem_total = psutil.virtual_memory().total / 1024 / 1024
    mem_used = psutil.virtual_memory().used / 1024 / 1024
    mem_utilized = psutil.virtual_memory().percent

    swap_total = psutil.swap_memory().total / 1024 / 1024
    swap_used = psutil.swap_memory().used / 1024 / 1024
    swap_utilized = psutil.swap_memory().percent

    print ("CPU1s  : %s" % cpu_load_1_sec)
    print ("CPU5s  : %s" % cpu_load_5_sec)
    # print ("CPU15s : %s" % cpu_load_15_sec)
    # print ("CPU60s : %s" % cpu_load_60_sec)

    print ("Memory_total: %s" % mem_total)
    print ("Memory_used: %s" % mem_used)
    print ("Memory_utilized: %s" % mem_utilized)

    print ("Swap_total: %s" % swap_total)
    print ("Swap_used: %s" % swap_used)
    print ("Swap_utilized: %s" % swap_utilized)

    # for p in psutil.disk_partitions():
    #    get_mount_usage(p.mountpoint)



    my_metrics = Metric()

    my_metrics.add_metric('CPU_1s', cpu_load_1_sec)
    my_metrics.add_metric('CPU_5s', cpu_load_5_sec)
    # my_metrics.add_metric('CPU_15s', cpu_load_15_sec)
    # my_metrics.add_metric('CPU_60s', cpu_load_60_sec)

    my_metrics.add_metric('Memory_total', mem_total)
    my_metrics.add_metric('Memory_user', mem_used)
    my_metrics.add_metric('Memory_utilized', mem_utilized)

    my_metrics.add_metric('Swap_total', swap_total)
    my_metrics.add_metric('Swap_used', swap_used)
    my_metrics.add_metric('Swap_utilized', swap_utilized)

    my_metrics.add_metric('Mount_root_total', psutil.disk_usage("/").total)
    my_metrics.add_metric('Mount_root_available', psutil.disk_usage("/").free)
    my_metrics.add_metric('Mount_root_used', psutil.disk_usage("/").used)
    my_metrics.add_metric('Mount_root_utilized', get_mount_usage("/"))
        
    my_metrics.add_metric('Mount_/boot', get_mount_usage("/boot"))
    my_metrics.add_metric('Mount_/home', get_mount_usage("/home"))
    my_metrics.add_metric('Mount_/opt', get_mount_usage("/opt"))
    my_metrics.add_metric('Mount_/usr/gems', get_mount_usage("/usr/gems"))
    my_metrics.add_metric('Mount_/usr/openv', get_mount_usage("/usr/openv"))
    my_metrics.add_metric('Mount_/var', get_mount_usage("/var"))
    my_metrics.add_metric('Mount_/dev', get_mount_usage("/dev"))
    my_metrics.add_metric('Mount_/net', get_mount_usage("/net"))


    my_metrics.add_metric('Process_ntpd', get_process_state("ntpd"))
    my_metrics.add_metric('Process_sshd', get_process_state("sshd"))
    my_metrics.add_metric('Process_crond', get_process_state("crond"))
    my_metrics.add_metric('Process_syslogd', get_process_state("syslogd"))
    my_metrics.add_metric('Process_xinetd', get_process_state("xinetd"))

    for part in disk_partitions(disk_ntuple):
        mountpoint = part.mountpoint
        metrics_key = 'DiskUsage_' + mountpoint
        my_metrics.add_metric(metrics_key,
                              disk_usage(mountpoint, usage_ntuple).percent)

        # my_metrics.send()


if __name__ == '__main__':
    get_metrics()
