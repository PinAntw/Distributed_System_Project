from locust import HttpUser, task, between
import random
import string


class UserBehavior(HttpUser):
    """
    定義使用者行為，模擬註冊、登錄、保存 user_id，並執行其他操作的測試。
    """
    wait_time = between(1, 3)  # 每次請求之間的等待時間
    token = None  # 用於保存 JWT Token
    user_id = None  # 保存返回的 user_id
    username = None  # 保存用戶名
    group_name = None

    def on_start(self):
        """
        在每個虛擬用戶開始時執行，模擬用戶註冊或登錄。
        """
        # 隨機生成用戶名和密碼
        self.username = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        # 模擬註冊和登錄
        self.register(self.username, password)
        self.login(self.username, password)
        self.create_group()
        print(f'Time1| User: {self.user_id}, Group: {self.group_name}')

        if random.random() < 0.1:  # 產生隨機數，如果大於 0.4，跳過函式執行
            self.create_group()
            print(f'Time2| User: {self.user_id}, Group: {self.group_name}')

    def register(self, username, password):
        """
        模擬註冊 API 的請求。
        """
        payload = {"username": username, "password": password}
        response = self.client.post("/auth/register", json=payload)
        if response.status_code == 200:
            print(f"User registered: {username}")
        else:
            print(f"Failed to register: {response.text}")

    def login(self, username, password):
        """
        模擬登錄 API 的請求，並保存 user_id。
        """
        payload = {"username": username, "password": password}
        response = self.client.post("/auth/login", json=payload)
        if response.status_code == 200:
            data = response.json()
            self.user_id = int(data.get("user_id")) if data.get("user_id") else None  # 確保 user_id 是整數
            print(f"Login successful: {username}, User ID: {self.user_id}")
        else:
            print(f"Failed to login: {response.text}")
    
    # def create_group(self):
    #     """
    #     模擬創建隊伍
    #     """
    #     if not self.user_id:
    #         print("No user_id available, skipping create group request.")
    #         return

    #     self.group_name = ''.join(random.choices(string.ascii_letters + string.digits, k=12))  # 確保唯一
    #     response = self.client.post(f"/api/groups/create-group?user_id={self.user_id}&group_name={self.group_name}")
        
    #     if response.status_code == 200:
    #         print(f"Create Group Successful: User {self.user_id}, Group Name: {self.group_name}")
    #     else:
    #         print(f"Failed to Create Group: {response.status_code} {response.text}")

    def create_group(self):
        """
        模擬創建隊伍
        """
        if not self.user_id:
            print("No user_id available, skipping create group request.")
            return

        # 隨機生成組名，並確保唯一
        self.group_name = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        # 發送 POST 請求，使用 JSON body
        payload = {
            "user_id": self.user_id,
            "group_name": self.group_name
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = self.client.post("/api/groups/create-group", json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"Create Group Successful: User {self.user_id}, Group Name: {self.group_name}")
        else:
            print(f"Failed to Create Group: {response.status_code} {response.text}")


    @task
    def checkin(self):
        """
        模擬打卡 API 的請求。
        """
        if not self.user_id or not self.group_name:
            print("No user_id available, skipping check-in request.")
            return

        # 模擬打卡數據
        payload = {
            "user_id": self.user_id,
            "post_content": f"user{self.user_id}: 腳本自動打卡"
        }

        response = self.client.post("/post/checkin", json=payload)
        if response.status_code == 200:
            print(f"user{self.user_id}: 自動打卡成功")
        else:
            print(f"Check-in failed: {response.text}")
