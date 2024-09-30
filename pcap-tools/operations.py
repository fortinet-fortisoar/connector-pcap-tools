"""
Copyright start
MIT License
Copyright (c) 2024 Fortinet Inc
Copyright end
"""

import logging
import json
from pcapkit import extract
from connectors.core.connector import get_logger, ConnectorError
from integrations.crudhub import make_request
from connectors.cyops_utilities.builtins import download_file_from_cyops, upload_file_to_cyops


logger = get_logger('pcap-parser')
logger.setLevel(logging.DEBUG)

"""
Utilities: support functions
"""
def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        return file_content

    except IOError:
        logger.error("Can't read file: {}".format(file_path))
        raise Exception("Can't read file: {}".format(file_path))
    

def _print_json(json_object):
    return json.dumps(json_object, indent=4)


def _get_file_paths(file_id):
    iri_type = 'attachment'
    file_name = None

    if not file_id.startswith('/api/3/'):
        file_id = '/api/3/attachments/' + file_id
    elif file_id.startswith('/api/3/files'):
        iri_type = 'file'

    if iri_type == 'attachment':
        attachment_data = make_request(file_id, 'GET')
        file_iri = attachment_data['file']['@id']
        file_name = attachment_data['file']['filename']
    else:
        file_iri = file_id

    res = download_file_from_cyops(file_iri)
    if not file_name:
        file_name = res['filename']
    
    logger.info("res: {}".format(res))
    file_path = "{0}/{1}".format('/tmp', res['cyops_file_path'])
    json_file = "{0}/{1}.json".format('/tmp', res['cyops_file_path'])
    return [file_path, json_file]

    

"""
Operations: connector's actions implementation
"""

def pcap_to_json(config, params):
    """Reads QRcode from an image file"""
    files = _get_file_paths(params.get("file_iri"))
    logger.debug(files)
    j_data = extract(fin=files[0], fout=files[1], format='json', extension=False)
    
    return read_file(files[1])


