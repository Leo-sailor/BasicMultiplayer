from hashlib import scrypt
from math import floor

from fastapi.testclient import TestClient
from httpx import Response
from Server.main import app
from time import time
from typing import Any
client = TestClient(app)
test_num = 1
def print_response(response: Response):
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
def time_any_response(request_type:str,request,test_name: int=None):
    global test_num
    if test_name is None:
        test_name = test_num
    before = time()
    if request_type.lower() == "get":
        res = client.get(request)
    elif request_type == "post":
        res = client.post(request)
    elif request_type == "delete":
        res = client.delete(request)
    else:
        raise ValueError(f"Invalid request type: {request_type}")
    after = time() - before
    print(f"Test{test_name} took: {after:.4f} seconds")
    print_response(res)
    test_num += 1
    print("")
def test_response(request_type:str,request, expected_response_dict:dict[str,Any], test_name: int=None, ignored_response_fields:list[str]=None,force_print=False):
    global test_num
    if test_name is None:
        test_name = test_num
    if ignored_response_fields is None:
        ignored_response_fields = []
    ignored_response_fields.append("Server Time (epoch)")
    if request_type.lower() == "get":
        response = client.get(request)
    elif request_type == "post":
        response = client.post(request)
    elif request_type == "delete":
        response = client.delete(request)
    else:
        raise ValueError(f"Invalid request type: {request_type}")
    res_dict: dict[str,Any] = response.json()
    for field in ignored_response_fields:
        if field in res_dict:
            res_dict.pop(field)
    if response.status_code != 200 or res_dict != expected_response_dict:
        print(f"Test {test_name} failed:")
        print(f"Request {request}")
        print(f"Expected: {expected_response_dict}")
        print("Actual:")
        print_response(response)
    elif not force_print:
        print(f"Test {test_name} passed")
    else:
        print(f"Test {test_name} passed")
        print(f"Request {request}")
        print_response(response)
    test_num += 1
    print("")
    return response
def generate_token(code)-> int:
    correct_time = floor(time())
    salt = str(correct_time).encode()
    key = str(code).encode()
    hash_one = scrypt(key, salt=salt, n=16384, r=8, p=1, dklen=32)
    return int.from_bytes(hash_one)
time_any_response("get","/ping")
test_response("get","/test/hello", {"message": "hello"})
code = test_response("post","/0/join/leo", {"message": "Player leo successfully joined game 0","start_position":[0,0]}, ignored_response_fields=["private_code"],force_print=True).json()["private_code"]
test_response("delete",f"0/leave/{generate_token(code)}",{"message": "Player left game 0"},force_print=True)