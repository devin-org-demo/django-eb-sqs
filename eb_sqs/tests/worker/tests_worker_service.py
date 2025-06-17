from __future__ import absolute_import, unicode_literals

from unittest import TestCase
from mock import patch

from eb_sqs import settings
from eb_sqs.worker.service import WorkerService


class WorkerServiceTest(TestCase):
    def setUp(self):
        self.worker_service = WorkerService()

    @patch('eb_sqs.worker.service.boto3.resource')
    @patch('eb_sqs.worker.service.WorkerFactory.default')
    @patch('eb_sqs.worker.service.signal.signal')
    @patch('os.environ', {})
    def test_metadata_service_timeout_config(self, mock_signal, mock_worker_factory, mock_boto3_resource):
        import os
        original_timeout = settings.AWS_METADATA_SERVICE_TIMEOUT
        settings.AWS_METADATA_SERVICE_TIMEOUT = 60
        
        mock_worker = patch('eb_sqs.worker.service.Worker').start()
        mock_worker_factory.return_value.create.return_value = mock_worker
        
        try:
            self.worker_service.process_queues(['test-queue'])
            
            mock_boto3_resource.assert_called_once()
            self.assertEqual(os.environ.get('AWS_METADATA_SERVICE_TIMEOUT'), '60')
        finally:
            settings.AWS_METADATA_SERVICE_TIMEOUT = original_timeout
            os.environ.pop('AWS_METADATA_SERVICE_TIMEOUT', None)
            patch.stopall()

    @patch('eb_sqs.worker.service.boto3.resource')
    @patch('eb_sqs.worker.service.WorkerFactory.default')
    @patch('eb_sqs.worker.service.signal.signal')
    @patch('os.environ', {})
    def test_metadata_service_num_attempts_config(self, mock_signal, mock_worker_factory, mock_boto3_resource):
        import os
        original_attempts = settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS
        settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS = 3
        
        mock_worker = patch('eb_sqs.worker.service.Worker').start()
        mock_worker_factory.return_value.create.return_value = mock_worker
        
        try:
            self.worker_service.process_queues(['test-queue'])
            
            mock_boto3_resource.assert_called_once()
            self.assertEqual(os.environ.get('AWS_METADATA_SERVICE_NUM_ATTEMPTS'), '3')
        finally:
            settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS = original_attempts
            os.environ.pop('AWS_METADATA_SERVICE_NUM_ATTEMPTS', None)
            patch.stopall()

    @patch('eb_sqs.worker.service.boto3.resource')
    @patch('eb_sqs.worker.service.WorkerFactory.default')
    @patch('eb_sqs.worker.service.signal.signal')
    @patch('os.environ', {})
    def test_metadata_service_config_none_values(self, mock_signal, mock_worker_factory, mock_boto3_resource):
        import os
        original_timeout = settings.AWS_METADATA_SERVICE_TIMEOUT
        original_attempts = settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS
        settings.AWS_METADATA_SERVICE_TIMEOUT = None
        settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS = None
        
        mock_worker = patch('eb_sqs.worker.service.Worker').start()
        mock_worker_factory.return_value.create.return_value = mock_worker
        
        try:
            self.worker_service.process_queues(['test-queue'])
            
            mock_boto3_resource.assert_called_once()
            self.assertIsNone(os.environ.get('AWS_METADATA_SERVICE_TIMEOUT'))
            self.assertIsNone(os.environ.get('AWS_METADATA_SERVICE_NUM_ATTEMPTS'))
        finally:
            settings.AWS_METADATA_SERVICE_TIMEOUT = original_timeout
            settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS = original_attempts
            patch.stopall()

    @patch('eb_sqs.worker.service.boto3.resource')
    @patch('eb_sqs.worker.service.WorkerFactory.default')
    @patch('eb_sqs.worker.service.signal.signal')
    @patch('os.environ', {})
    def test_metadata_service_config_both_set(self, mock_signal, mock_worker_factory, mock_boto3_resource):
        import os
        original_timeout = settings.AWS_METADATA_SERVICE_TIMEOUT
        original_attempts = settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS
        settings.AWS_METADATA_SERVICE_TIMEOUT = 45
        settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS = 5
        
        mock_worker = patch('eb_sqs.worker.service.Worker').start()
        mock_worker_factory.return_value.create.return_value = mock_worker
        
        try:
            self.worker_service.process_queues(['test-queue'])
            
            mock_boto3_resource.assert_called_once()
            self.assertEqual(os.environ.get('AWS_METADATA_SERVICE_TIMEOUT'), '45')
            self.assertEqual(os.environ.get('AWS_METADATA_SERVICE_NUM_ATTEMPTS'), '5')
        finally:
            settings.AWS_METADATA_SERVICE_TIMEOUT = original_timeout
            settings.AWS_METADATA_SERVICE_NUM_ATTEMPTS = original_attempts
            os.environ.pop('AWS_METADATA_SERVICE_TIMEOUT', None)
            os.environ.pop('AWS_METADATA_SERVICE_NUM_ATTEMPTS', None)
            patch.stopall()
