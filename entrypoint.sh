#!/bin/sh

echo "========================================"
echo "   Запуск Custom Auth Application"
echo "========================================"

cd /app

echo "Выполняем миграции..."
python manage.py migrate --noinput

echo "Загружаем тестовые данные..."
python manage.py load_test_data || echo "Тестовые данные уже загружены или команда отсутствует"

echo "Запуск Django сервера..."
exec "$@"