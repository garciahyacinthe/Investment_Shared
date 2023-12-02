import json
import logging
from enum import Enum

import requests
from requests import Response


class HTTPMethods(Enum):
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'
    PATCH = 'patch'
    HEAD = 'head'
    OPTIONS = 'options'


class Environnement(Enum):
    PROD = 'prod'
    DEV = 'dev'
    TEST = 'test'


class ClientApp:

    def __init__(self,
                 client_id: str = '',
                 client_secret: str = '',
                 environnement: Environnement = Environnement.DEV,
                 ):
        self.client_id = str(client_id)
        self.client_secret = str(client_secret)
        if str(environnement).upper() in ['PRD', 'PROD', 'PRODUCTION']:
            self.environnement = Environnement.PROD
        elif str(environnement).upper() in ['DEV', 'HOM', 'UAT', 'DEVELOPMENT']:
            self.environnement = Environnement.DEV
        else:
            self.environnement = str(environnement).upper()


class ServiceManager:

    def __init__(self,
                 client_app,
                 api_name="",
                 logger_name="",
                 return_raw_response=False):
        """
        :type client_app: ClientApp
        :param client_app: your client app information
        :param api_name: name of the API Service calling the service_manager: Used for Init logs purposes
        :param logger_name: name of the logger to use for logs
        :param return_raw_response: if True, returns the API response as is, else returns a Box object
        """

        self.client_app = client_app
        self.api_name = api_name
        self.logger_name = logger_name
        self.return_raw_response = return_raw_response
        self.accepted_responses = list(range(200, 207))

        self.session = requests.Session()
        self.logger = self.get_logger()

        if self.logger:
            self.get_service_info()
        else:
            print(self.get_service_info())

    def get_logger(self):
        if self.logger_name:
            return logging.getLogger(self.logger_name)
        else:
            for name in logging.root.manager.loggerDict:
                if name.startswith(self.api_name):
                    return logging.getLogger(name)
        return None

    def get_service_info(self):
        if self.logger:
            self.logger.info(f"ServiceManager for {self.api_name} initialized")
        else:
            return f"ServiceManager for {self.api_name} initialized"

    def get(self, uri_request, params='', timeout=60, verify=True):

        return self._test_response(
            self.session.get(url=uri_request, params=params, timeout=timeout, verify=verify), request_params=params)

    def post(self, uri_request, data='', json='', timeout=60, verify=True):
        data = self._dump_data(data)
        return self._test_response(
            self.session.post(url=uri_request, data=data, json=json, timeout=timeout, verify=verify),
            request_data=data,
            request_json=json)

    def patch(self, uri_request, data='', json='', timeout=60, verify=True):
        data = self._dump_data(data)
        return self._test_response(
            self.session.patch(url=uri_request, data=data, json=json, timeout=timeout, verify=verify),
            request_data=data,
            request_json=json)

    def put(self, uri_request, data='', json='', timeout=60, verify=True):
        data = self._dump_data(data)
        return self._test_response(
            self.session.put(url=uri_request, data=data, json=json, timeout=timeout, verify=verify),
            request_data=data,
            request_json=json)

    def delete(self, uri_request, timeout=60, verify=True):
        return self._test_response(
            self.session.delete(url=uri_request, json=json, timeout=timeout, verify=verify)
        )

    @staticmethod
    def _dump_data(data):
        if data:
            return json.dumps(data)
        return data

    def _test_response(self, response: Response, request_params: str = '', request_data: str = '', request_json=''):
        if not self.return_raw_response and response.status_code in self.accepted_responses:
            try:
                return response.json()
            except Exception as e:
                return print(f"{response.text} - {e}")

        if self.logger:
            log_string = f'Error on {response.request.method} method for this request: {response.request.url}\n' \
                         f"Status code: {response.status_code} - Reason: {response.reason} - Text: {response.text}"

            if request_params != '' and request_params is not None:
                log_string += f"\nRequest params: {request_params}"
            if request_data != '' and request_data is not None:
                log_string += f"\nRequest data: {request_data}"
            if request_json != '' and request_json is not None:
                log_string += f"\nReturn json: {request_json}"
            self.logger.error(log_string, exc_info=False)

        if response.status_code not in self.accepted_responses:
            return response.raise_for_status()
        return response
