#!/usr/bin/env python
"""jenkins_release - release ohWafHelpers to linn public (openhome) artifacts
"""
import os
import sys
import tarfile
try:
    import boto3
except:
    print('\nAWS fetch requires boto3 module')
    print("Please install this using 'pip install boto3'\n")
else:
    # create AWS credentials file (if not already present)
    home = None
    if 'HOMEPATH' in os.environ and 'HOMEDRIVE' in os.environ:
        home = os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
    elif 'HOME' in os.environ:
        home = os.environ['HOME']
    if home:
        awsCreds = os.path.join(home, '.aws', 'credentials')
        if not os.path.exists(awsCreds):
            if sys.version_info[0] == 2:
                from urllib2 import urlopen
            else:
                from urllib.request import urlopen
            try:
                os.mkdir(os.path.join(home, '.aws'))
            except:
                pass
            credsFile = urlopen('http://core.linn.co.uk/~artifacts/artifacts/aws-credentials' )
            creds = credsFile.read()
            with open(awsCreds, 'wt') as f:
                f.write(creds)

excludes = ['.git',
            '.gitignore',
            'jenkins_release.py']

jobName = 'ohWafHelpers'
if 'JOB_NAME' in os.environ:
    jobName  = os.environ['JOB_NAME']

publishVersion = '0.0.0'
if 'PUBLISH_VERSION' in os.environ:
    publishVersion  = os.environ['PUBLISH_VERSION']

items = os.listdir('.')
tarName = '%s-%s.tar.gz' % (jobName, publishVersion)
print('Creating %s' % tarName)
tar = tarfile.open(name=tarName, mode='w:gz')
for item in items:
    if item not in excludes:
        print('    adding %s' % item)
        tar.add(item, arcname='ohWafHelpers/%s' % item)
tar.close()

awsBucket = 'linn.artifacts.public'
resource = boto3.resource('s3')
print('Publish %s -> s3://%s/artifacts/%s/%s' % (tarName, awsBucket, jobName, tarName))
bucket = resource.Bucket( awsBucket )
with open(tarName, 'rb') as data:
    bucket.upload_fileobj(data, 'artifacts/%s/%s' % (jobName, tarName))
