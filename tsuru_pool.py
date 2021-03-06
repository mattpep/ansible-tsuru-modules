#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    # 'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: tsuru_pool

short_description: Create a tsuru pool

description:
    - "Creates a pool for use in tsuru. The target host must be logged in to a tsuru API server"

options:
    name:
        description:
            - The name of the pool
        required: true
    public:
        description:
            - Whether the pool should be public. (Defaults to false)
        required: false
    token:
        description:
            - A valid API token (can generate this tsurud token or similar)
        required: true
    endpoint:
        description:
            - THe Tsuru API endpoint
        required: true

author:
    - Matt Peperell (@mattpep)
'''

EXAMPLES = '''
- name: Create webapps tsuru pool
  tsuru_pool:
    name: webapps

- name: Delete webapps tsuru pool
  tsuru_pool:
    name: webapps
    state: absent

'''

from ansible.module_utils.basic import *
import requests


def pool_present(data):

    api_key = data['token']
    tsuru_url = data['endpoint']

    headers = {
        "Authorization": "bearer {}" . format(api_key)
    }
    url = "{}{}" . format(tsuru_url, '/pools')
    result = requests.get(url, headers=headers)
    filtered_result = filter(lambda p: p['name'] == data['name'], result.json())

    if filtered_result is not None and len(filtered_result) == 1:
        return False, False, result.json()

    url = "{}/pools" . format(tsuru_url)
    fields = { 'name': data['name'] }
    result = requests.post(url, fields, headers=headers)
    if result.status_code == 201:
        return False, True, {"status": "SUCCESS"}

    # default: something went wrong
    meta = {"status": result.status_code, 'response': result.text}
    return True, False, meta


def pool_absent(data=None):

    api_key = data['token']
    tsuru_url = data['endpoint']

    headers = {
        "Authorization": "bearer {}" . format(api_key)
    }
    url = "{}/pools/{}" . format(tsuru_url, data['name'])
    result = requests.delete(url, headers=headers)

    if result.status_code == 200:
        return False, True, {"status": "SUCCESS"}
    if result.status_code == 404:
	result = {"status": result.status_code, "data": result.text}
        return False, False, result
    else:
        result = {"status": result.status_code, "data": result.text}
        return True, False, result


def main():

    fields = {
        "name": {"required": True, "type": "str"},
        "public": {"required": False, "type": "str"},
        "token": {"required": True, "type": "str"},
        "endpoint": {"required": True, "type": "str"},
        "state": {
            "default": "present",
            "choices": ['present', 'absent'],
            "type": 'str'
        },
    }

    choice_map = {
        "present": pool_present,
        "absent": pool_absent,
    }

    module = AnsibleModule(argument_spec=fields)
    is_error, has_changed, result = choice_map.get(
        module.params['state'])(module.params)

    if not is_error:
        module.exit_json(changed=has_changed, meta=result)
    else:
        module.fail_json(msg="Error when communicating with API", meta=result)


if __name__ == '__main__':
    main()
