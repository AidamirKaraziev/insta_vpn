from config import OUTLINE_USERS_GATEWAY, OUTLINE_SALT, CONN_NAME


# class OutlineBackend:
#     # инициализация
#     def __init__(self, server: str = None):
#         self.session = requests.Session()
#         self.server = get_server(server)
#         self.base_url = self.server["apiUrl"]
#
#     # создание ключа
#     def _post(self, path: str, data=None):
#         url = f"{self.base_url}/{path}"
#         response = self.session.request(
#             "POST", url, verify=False, headers=headers, data=data
#         )
#         if response.status_code == 201:
#             return response.json()
#
#     # изменение ключа
#     def _put(self, path: str, data=None):
#         url = f"{self.base_url}/{path}"
#         json_data = json.dumps(data)
#         response = self.session.put(url, verify=False, headers=headers, data=json_data)
#         if response.status_code == 204:
#             return
#
#     def rename_key(self, key_id: Union[str, int], key_name: str):
#         return self._put(f"access-keys/{key_id}/name", data={"name": key_name})
#
#     def create_new_key(self, name: str):
#         response = self._post("access-keys")
#         key_id = response.get("id")
#         self.rename_key(key_id, name)
#         return key_id


def gen_outline_dynamic_link(profile_id: int):
    print(hex(profile_id))
    return f"{OUTLINE_USERS_GATEWAY}/conf/{OUTLINE_SALT}{hex(profile_id)}#{CONN_NAME}"


# def get_config_by_id(profile_id: int) -> dict:
#     conn = DataBaseConnector()
#     user_id = str(user_id)
#     result = dict(conn.select(CMD, (user_id, ))[0])
#     return result

