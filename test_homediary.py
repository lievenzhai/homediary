import unittest
from app import app, db, User, Diary


class HomediaryTestCase(unittest.TestCase):
    def setUp(self):
        # 更新配置
        app.config.update(
            TESTING = True,  # 设为 True 来开启测试模式，这样在出错时不会输出多余信息
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # 使用 SQLite 内存型数据库，不会干扰开发时使用的数据库文件
        )
        # 创建数据库和表
        db.create_all()
        # 创建测试数据，一个用户，一个日记
        user = User(name='Test', username='test')
        user.set_password('123')
        diary = Diary(title='Test Title', article='Test Article', author='Test Author')
        db.session.add_all([user, diary])
        db.session.commit()

        self.client = app.test_client()  # 创建测试客户端，模拟客户端请求
        self.runner = app.test_cli_runner()  # 创建测试命令运行器，用来触发自定义命令


    def tearDown(self):
        db.session.remove()  # 清除数据库会话
        db.drop_all()

    # 测试程序实例是否存在
    def test_app_exist(self):
        self.assertIsNotNone(app)


    # 测试程序是否处于测试模式
    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    # 测试404页面
    def test_404_page(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found - 404',data)
        self.assertIn('Go Back',data)
        self.assertEqual(response.status_code, 404)


    # 测试主页
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)  # 参数设为 True 可以获取 Unicode 格式的响应主体
        #self.assertIn('Test的日记',data)
        self.assertIn('新建日记',data)
        self.assertEqual(response.status_code, 200)

    # 辅助方法，用于登入用户
    def login(self):
        self.client.post('/login', data=dict(
            username = 'test',
            password = '123'
        ), follow_redirects=True)  # 设置为True可以跟随重定向

    # 测试创建条目
    def test_create_item(self):
        self.login()

        # 测试创建条目操作
        response = self.client.post('/diary', data=dict(
            title='New diary',
            article='New diary',
            author='test'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('新的日记已保存',data)
        self.assertIn('新建日记', data)

        # 测试创建电影条目，但电影标题为空
        response = self.client.post('/diary', data=dict(
            title='',
            article='New diary',
            author='test'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('新的日记已保存', data)
        self.assertIn('无效的输入', data)

    # 测试登录保护
    def test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('退出', data)

    # 测试登录
    def test_login(self):
        response = self.client.post('/login',data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('设置', data)

        # 测试使用错误的密码登录
        response = self.client.post('/login',data=dict(
            username='test',
            password='456'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('登录成功！', data)
        self.assertIn('错误的用户名或密码',data)



if __name__ == '__main__':
    unittest.main()


