# -*- coding: utf-8 -*-

import re
import threading
import time
import unittest
from selenium import webdriver
from app import create_app, db
from app.models import Role, User, Post


class SeleniumTestCase(unittest.TestCase):
    """Заготовка модульного теста под управлением Selenium"""

    client = None
    
    @classmethod
    def setUpClass(cls):
        # запуск Firefox
        try:
            cls.client = webdriver.Firefox()
        except:
            pass

        # Пропустить следующие тесты если браузер не запустился
        if cls.client:
            # Создание приложения
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # Подавить вывод отладочных сообщений,
            # чтобы очистить вывод от лишнего мусора
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")

            # Создать базу данных и наполнить ее фиктивными данными
            db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)

            # Добавить админа
            admin_role = Role.query.filter_by(permissions=0xff).first()
            admin = User(
                email='john@example.com', username='john',
                password='cat', role=admin_role, confirmed=True
            )
            db.session.add(admin)
            db.session.commit()

            # Старт Flask server в отдельном потоке
            threading.Thread(target=cls.app.run).start()

            time.sleep(1) 

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # Остановить flask server и закрыть браузер
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()

            # Дропнуть бд
            db.drop_all()
            db.session.remove()

            # Удалить контекст приложения
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass
    
    def test_admin_home_page(self):
        # Перейти на глагне
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('Hello,\s+Stranger!', self.client.page_source))

        # Перейти на страницу аутентификации
        self.client.find_element_by_link_text('Log In').click()
        self.assertTrue('<h1>Login</h1>' in self.client.page_source)

        # Логин
        self.client.find_element_by_name('email').\
            send_keys('john@example.com')
        self.client.find_element_by_name('password').send_keys('cat')
        self.client.find_element_by_name('submit').click()
        self.assertTrue(re.search('Hello,\s+john!', self.client.page_source))

        # Перейти на страницу профиля пользователя
        self.client.find_element_by_link_text('Profile').click()
        self.assertTrue('<h1>john</h1>' in self.client.page_source)
