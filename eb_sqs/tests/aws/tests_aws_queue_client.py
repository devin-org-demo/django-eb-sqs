from __future__ import absolute_import, unicode_literals

import time
from unittest import TestCase
from mock import patch, MagicMock

import boto3
from botocore.exceptions import ClientError
from moto import mock_sqs

from eb_sqs import settings
from eb_sqs.aws.sqs_queue_client import SqsQueueClient
from eb_sqs.worker.queue_client import QueueDoesNotExistException


class AwsQueueClientTest(TestCase):
    def setUp(self):
        settings.QUEUE_PREFIX = 'eb-sqs-'

    @mock_sqs()
    def test_add_message(self):
        sqs = boto3.resource('sqs',
                             region_name=settings.AWS_REGION)
        queue = sqs.create_queue(QueueName='eb-sqs-default')

        queue_client = SqsQueueClient()

        queue_client.add_message('default', 'msg', 0)

        queue.reload()
        self.assertEqual(queue.attributes["ApproximateNumberOfMessages"], '1')

    @mock_sqs()
    def test_add_message_delayed(self):
        delay = 1
        sqs = boto3.resource('sqs',
                             region_name=settings.AWS_REGION)
        queue = sqs.create_queue(QueueName='eb-sqs-default')
        queue_client = SqsQueueClient()

        queue_client.add_message('default', 'msg', delay)

        queue.reload()
        self.assertEqual(queue.attributes["ApproximateNumberOfMessages"], '0')

        time.sleep(delay + 0.1)

        queue.reload()
        self.assertEqual(queue.attributes["ApproximateNumberOfMessages"], '1')

    @mock_sqs()
    def test_add_message_wrong_queue(self):
        sqs = boto3.resource('sqs',
                             region_name=settings.AWS_REGION)
        sqs.create_queue(QueueName='default')
        queue_client = SqsQueueClient()

        with self.assertRaises(QueueDoesNotExistException):
            queue_client.add_message('invalid', 'msg', 0)

    @mock_sqs()
    def test_auto_add_queue(self):
        settings.AUTO_ADD_QUEUE = True

        queue_name = 'test-queue'

        sqs = boto3.resource('sqs',
                             region_name=settings.AWS_REGION)

        queue_client = SqsQueueClient()

        queue_client.add_message(queue_name, 'msg', 0)

        full_queue_name = settings.QUEUE_PREFIX + queue_name

        queue = sqs.get_queue_by_name(QueueName=full_queue_name)

        self.assertEqual(queue.attributes["ApproximateNumberOfMessages"], '1')

        queue.delete()

        # moto throws exception inconsistent with boto, thus the patching
        with patch.object(queue_client.queue_cache[full_queue_name], 'send_message') as send_message_fn:
            send_message_fn.side_effect = ClientError({'Error': {'Code': 'AWS.SimpleQueueService.NonExistentQueue'}}, None)

            queue_client.add_message(queue_name, 'msg', 0)

        queue = sqs.get_queue_by_name(QueueName=full_queue_name)

        self.assertEqual(queue.attributes["ApproximateNumberOfMessages"], '1')

        settings.AUTO_ADD_QUEUE = False

    @patch('eb_sqs.aws.sqs_queue_client.boto3.resource')
    @patch('os.environ', {})
    def test_metadata_service_timeout_config(self, mock_boto3_resource):
        import os
        original_timeout = settings.AWS_METADATA_SERVICE_TIMEOUT
        settings.AWS_METADATA_SERVICE_TIMEOUT = 60
        
        try:
            SqsQueueClient()
            
            mock_boto3_resource.assert_called_once()
            self.assertEqual(os.environ.get('AWS_METADATA_SERVICE_TIMEOUT'), '60')
        finally:
            settings.AWS_METADATA_SERVICE_TIMEOUT = original_timeout
            os.environ.pop('AWS_METADATA_SERVICE_TIMEOUT', None)

    @patch('eb_sqs.aws.sqs_queue_client.boto3.resource')
    @patch('os.environ', {})
    def test_metadata_service_num_attempts_config(self, mock_boto3_resource):
        import os
        original_attempts = settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS
        settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS = 3
        
        try:
            SqsQueueClient()
            
            mock_boto3_resource.assert_called_once()
            self.assertEqual(os.environ.get('AWS_METADATA_SERVICE_NUM_ATTEMPTS'), '3')
        finally:
            settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS = original_attempts
            os.environ.pop('AWS_METADATA_SERVICE_NUM_ATTEMPTS', None)

    @patch('eb_sqs.aws.sqs_queue_client.boto3.resource')
    @patch('os.environ', {})
    def test_metadata_service_config_none_values(self, mock_boto3_resource):
        import os
        original_timeout = settings.AWS_METADATA_SERVICE_TIMEOUT
        original_attempts = settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS
        settings.AWS_METADATA_SERVICE_TIMEOUT = None
        settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS = None
        
        try:
            SqsQueueClient()
            
            mock_boto3_resource.assert_called_once()
            self.assertIsNone(os.environ.get('AWS_METADATA_SERVICE_TIMEOUT'))
            self.assertIsNone(os.environ.get('AWS_METADATA_SERVICE_NUM_ATTEMPTS'))
        finally:
            settings.AWS_METADATA_SERVICE_TIMEOUT = original_timeout
            settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS = original_attempts

    @patch('eb_sqs.aws.sqs_queue_client.boto3.resource')
    @patch('os.environ', {})
    def test_metadata_service_config_both_set(self, mock_boto3_resource):
        import os
        original_timeout = settings.AWS_METADATA_SERVICE_TIMEOUT
        original_attempts = settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS
        settings.AWS_METADATA_SERVICE_TIMEOUT = 45
        settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS = 5
        
        try:
            SqsQueueClient()
            
            mock_boto3_resource.assert_called_once()
            self.assertEqual(os.environ.get('AWS_METADATA_SERVICE_TIMEOUT'), '45')
            self.assertEqual(os.environ.get('AWS_METADATA_SERVICE_NUM_ATTEMPTS'), '5')
        finally:
            settings.AWS_METADATA_SERVICE_TIMEOUT = original_timeout
            settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS = original_attempts
            os.environ.pop('AWS_METADATA_SERVICE_TIMEOUT', None)
            os.environ.pop('AWS_METADATA_SERVICE_NUM_ATTEMPTS', None)
